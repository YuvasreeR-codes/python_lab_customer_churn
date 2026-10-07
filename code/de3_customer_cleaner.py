import pandas as pd
from sqlalchemy import text
from code.cp2_customer_cleaner import CustomerCleaner


def clean_staging(engine):
    # Read staging table
    df = pd.read_sql(
        "SELECT * FROM stg_customer_raw",
        engine
    )

    raw_count = len(df)
    print(f"Raw staging rows: {raw_count}")
    cleaner = CustomerCleaner(df)
    cleaned_df = cleaner.clean()
    cleaned_count = len(cleaned_df)
    print(f"Cleaned rows: {cleaned_count}")

    # -------------------------------------------------
    # Row count check
    # -------------------------------------------------

    assert cleaned_count == raw_count, (
        f"Row count mismatch: "
        f"staging={raw_count}, cleaned={cleaned_count}"
    )
    print(
        f"PASS - Row count check: "
        f"{cleaned_count}/{raw_count}"
    )

    # -------------------------------------------------
    # Data quality checks
    # -------------------------------------------------

    null_customer_id = cleaned_df["customer_i_d"].isna().sum()
    if null_customer_id == 0:
        print("PASS - customer_id NULL check: 0")
    else:
        print(
            f"FAIL - customer_id NULL check: "
            f"{null_customer_id}"
        )
        raise AssertionError("customer_id contains NULLs")

    null_monthly = cleaned_df["monthly_charges"].isna().sum()
    if null_monthly == 0:
        print("PASS - monthly_charges NULL check: 0")
    else:
        print(
            f"FAIL - monthly_charges NULL check: "
            f"{null_monthly}"
        )
        raise AssertionError("monthly_charges contains NULLs")

    invalid_churn = (
        ~cleaned_df["churn"].isin([0, 1])
    ).sum()

    if invalid_churn == 0:
        print("PASS - churn values check: 0 invalid")
    else:
        print(
            f"FAIL - churn values check: "
            f"{invalid_churn} invalid"
        )
        raise AssertionError("Invalid churn values")

    # -------------------------------------------------
    # Write cleaned table
    # -------------------------------------------------
    cleaned_df.to_sql(
        "cleaned_customers",
        engine,
        if_exists="replace",
        index=False
    )
    print(
        f"cleaned_customers populated: "
        f"{cleaned_count} rows"
    )
    return cleaned_df


def build_curated_tables(engine):
    df = pd.read_sql(
        "SELECT * FROM cleaned_customers",
        engine
    )
    # ---------------------------------------------
    # dim_contract
    # ---------------------------------------------
    dim_contract = (
        df[["contract"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    dim_contract.insert(
        0,
        "contract_i_d",
        range(1, len(dim_contract) + 1)
    )
    dim_contract.to_sql(
        "dim_contract",
        engine,
        if_exists="replace",
        index=False
    )
    # ---------------------------------------------
    # dim_payment
    # ---------------------------------------------
    dim_payment = (
        df[["payment_method"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    dim_payment.insert(
        0,
        "payment_i_d",
        range(1, len(dim_payment) + 1)
    )
    dim_payment.to_sql(
        "dim_payment",
        engine,
        if_exists="replace",
        index=False
    )
    # ---------------------------------------------
    # customers
    # ---------------------------------------------
    customers = df[
        [
            "customer_i_d",
            "gender",
            "senior_citizen",
            "partner",
            "dependents"
        ]
    ].copy()
    customers.to_sql(
        "customers",
        engine,
        if_exists="replace",
        index=False
    )
    # ---------------------------------------------
    # fact_customer_account
    # ---------------------------------------------
    df = df.merge(
        dim_contract,
        on="contract",
        how="left"
    )
    # Map payment → payment_id
    df = df.merge(
        dim_payment,
        on="payment_method",
        how="left"
    )
    fact_customer_account = df[
        [
            "customer_i_d",
            "contract_i_d",
            "payment_i_d",
            "tenure",
            "monthly_charges",
            "total_charges",
            "churn"
        ]
    ].copy()

    fact_customer_account.to_sql(
        "fact_customer_account",
        engine,
        if_exists="replace",
        index=False
    )
    print("PASS - dim_contract populated")
    print("PASS - dim_payment populated")
    print("PASS - customers populated")
    print("PASS - fact_customer_account populated")

if __name__ == "__main__":

    from sqlalchemy import create_engine
    engine = create_engine(
        "mysql+pymysql://root:root@localhost/telecom_db_de"
    )
    clean_staging(engine)
    build_curated_tables(engine)