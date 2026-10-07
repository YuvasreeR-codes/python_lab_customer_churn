import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

def get_existing_customers(engine):

    query = """
        SELECT
            customer_i_d,
            gender,
            senior_citizen,
            partner,
            dependents
        FROM customers
    """
    return pd.read_sql(query, engine)


def classify_records(incoming_df, existing_df):
    # Make customer IDs consistent
    incoming_df["customer_i_d"] = (
        incoming_df["customer_i_d"]
        .astype(str)
        .str.strip()
    )

    existing_df["customer_i_d"] = (
        existing_df["customer_i_d"]
        .astype(str)
        .str.strip()
    )

    # Existing customer IDs
    existing_ids = set(
        existing_df["customer_i_d"]
    )

    # Create lookup dictionary
    existing_dict = (
        existing_df
        .set_index("customer_i_d")
        .to_dict("index")
    )

    rows_inserted = 0
    rows_updated = 0
    rows_unchanged = 0

    records_to_upsert = []

    compare_columns = [
        "gender",
        "senior_citizen",
        "partner",
        "dependents"
    ]

    for _, row in incoming_df.iterrows():

        customer_id = row["customer_i_d"]

        # =============================================
        # NEW CUSTOMER
        # =============================================

        if customer_id not in existing_ids:

            rows_inserted += 1

            records_to_upsert.append(
                row.to_dict()
            )

        # =============================================
        # EXISTING CUSTOMER
        # =============================================

        else:

            old_values = existing_dict[customer_id]

            changed = False

            for col in compare_columns:

                old_value = old_values[col]
                new_value = row[col]

                # Handle NULLs
                if pd.isna(old_value) and pd.isna(new_value):
                    continue

                if pd.isna(old_value) != pd.isna(new_value):
                    changed = True
                    break

                # Compare as strings
                if str(old_value).strip() != str(new_value).strip():
                    changed = True
                    break

            # =========================================
            # EXISTING + CHANGED
            # =========================================

            if changed:

                rows_updated += 1

                records_to_upsert.append(
                    row.to_dict()
                )

            # =========================================
            # EXISTING + SAME
            # =========================================

            else:

                rows_unchanged += 1

    return (
        records_to_upsert,
        rows_inserted,
        rows_updated,
        rows_unchanged
    )
# =========================================================
# INSERT / UPDATE customers
# =========================================================

def upsert_customers(records, engine):

    if not records:
        return

    query = text("""
        INSERT INTO customers (
            customer_i_d,
            gender,
            senior_citizen,
            partner,
            dependents
        )
        VALUES (
            :customer_i_d,
            :gender,
            :senior_citizen,
            :partner,
            :dependents
        )

        ON DUPLICATE KEY UPDATE
            gender = VALUES(gender),
            senior_citizen = VALUES(senior_citizen),
            partner = VALUES(partner),
            dependents = VALUES(dependents)
    """)

    with engine.begin() as connection:

        for record in records:

            connection.execute(
                query,
                {
                    "customer_i_d": record["customer_i_d"],
                    "gender": record["gender"],
                    "senior_citizen": int(
                        record["senior_citizen"]
                    ),
                    "partner": int(
                        record["partner"]
                    ),
                    "dependents": int(
                        record["dependents"]
                    )
                }
            )


# =========================================================
# Create pipeline run log
# =========================================================

def create_pipeline_log_table(engine):

    query = text("""
        CREATE TABLE IF NOT EXISTS pipeline_run_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            file_name VARCHAR(255),
            rows_inserted INT,
            rows_updated INT,
            rows_unchanged INT,
            run_timestamp DATETIME
        )
    """)

    with engine.begin() as connection:
        connection.execute(query)


# =========================================================
# Log pipeline run
# =========================================================

def log_pipeline_run(
    engine,
    file_name,
    rows_inserted,
    rows_updated,
    rows_unchanged
):

    query = text("""
        INSERT INTO pipeline_run_log (
            file_name,
            rows_inserted,
            rows_updated,
            rows_unchanged,
            run_timestamp
        )
        VALUES (
            :file_name,
            :rows_inserted,
            :rows_updated,
            :rows_unchanged,
            :run_timestamp
        )
    """)

    with engine.begin() as connection:

        connection.execute(
            query,
            {
                "file_name": file_name,
                "rows_inserted": rows_inserted,
                "rows_updated": rows_updated,
                "rows_unchanged": rows_unchanged,
                "run_timestamp": datetime.now()
            }
        )


# =========================================================
# Main incremental processing
# =========================================================

def process_incremental(filepath, engine):

    print("\n======================================")
    print("INCREMENTAL CUSTOMER PROCESSING")
    print("======================================")

    # ---------------------------------------------
    # Read today's CSV
    # ---------------------------------------------

    incoming_df = pd.read_csv(filepath)

    print(
        f"Incoming CSV rows: {len(incoming_df)}"
    )

  

    # ---------------------------------------------
    # Read existing database customers
    # ---------------------------------------------

    existing_df = get_existing_customers(engine)

    print(
        f"Existing customers: {len(existing_df)}"
    )

    # ---------------------------------------------
    # Classify records
    # ---------------------------------------------

    (
        records,
        rows_inserted,
        rows_updated,
        rows_unchanged
    ) = classify_records(
        incoming_df,
        existing_df
    )

    # ---------------------------------------------
    # Perform INSERT / UPDATE
    # ---------------------------------------------

    upsert_customers(
        records,
        engine
    )

    # ---------------------------------------------
    # Log run
    # ---------------------------------------------

    file_name = filepath.split("/")[-1]

    log_pipeline_run(
        engine,
        file_name,
        rows_inserted,
        rows_updated,
        rows_unchanged
    )

    # ---------------------------------------------
    # Print result
    # ---------------------------------------------

    print("\nPIPELINE RESULT")
    print("-----------------------------")

    print(
        f"Rows inserted   : {rows_inserted}"
    )

    print(
        f"Rows updated    : {rows_updated}"
    )

    print(
        f"Rows unchanged  : {rows_unchanged}"
    )

    return (
        rows_inserted,
        rows_updated,
        rows_unchanged
    )


# =========================================================
# Main
# =========================================================

if __name__ == "__main__":

    engine = create_engine(
        "mysql+pymysql://root:root@localhost/telecom_db_de"
    )

    # Create log table if it doesn't exist
    create_pipeline_log_table(engine)

    # Process daily customer extract
    process_incremental(
        "new_data.csv",
        engine
    )