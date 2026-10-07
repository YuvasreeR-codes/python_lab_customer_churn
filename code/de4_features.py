import pandas as pd
from sqlalchemy import create_engine

from code.cp4_feat_engg import build_features

def build_ml_features(engine):

    df = pd.read_sql(
        "SELECT * FROM cleaned_customers",
        engine
    )
    cleaned_count = len(df)
    print(f"Cleaned customers: {cleaned_count}")

    df = build_features(df)
    original_columns = [
        "customer_i_d",
        "gender",
        "senior_citizen",
        "partner",
        "dependents",
        "tenure",
        "phone_service",
        "multiple_lines",
        "internet_service",
        "online_security",
        "online_backup",
        "device_protection",
        "tech_support",
        "streaming_t_v",
        "streaming_movies",
        "contract",
        "paperless_billing",
        "payment_method",
        "monthly_charges",
        "total_charges",
        "churn"
    ]
    engineered_features = [
        "tenure_bucket",
        "high_charge_flag",
        "service_count",
        "is_long_term_customer",
        "has_streaming_bundle",
        "auto_pay_flag"
    ]

    required_columns = (
        original_columns +
        engineered_features
    )
    missing_columns = [
        col
        for col in required_columns
        if col not in df.columns
     ]

    if missing_columns:
       raise AssertionError(
           f"Missing columns: {missing_columns}"
       )

    print("\nPASS - All 27 columns are present")

    ml_features = df[
        required_columns
    ].copy()
    # Integer columns
    integer_columns = [
        "senior_citizen",
        "partner",
        "dependents",
        "tenure",
        "phone_service",
        "online_security",
        "online_backup",
        "device_protection",
        "tech_support",
        "streaming_t_v",
        "streaming_movies",
        "paperless_billing",
        "churn",
        "high_charge_flag",
        "service_count",
        "is_long_term_customer",
        "has_streaming_bundle",
        "auto_pay_flag"
    ]

    for col in integer_columns:
        ml_features[col] = ml_features[col].astype(int)

    # Float columns
    ml_features["monthly_charges"] = (
        ml_features["monthly_charges"].astype(float)
    )

    ml_features["total_charges"] = (
        ml_features["total_charges"].astype(float)
    )

    print("\nSchema / NULL Checks")
    print("--------------------")

    for col in engineered_features:
        null_count = ml_features[col].isna().sum()
        if null_count == 0:
            print(
                f"PASS - {col}: 0 NULLs"
            )
        else:
            print(
                f"FAIL - {col}: "
                f"{null_count} NULLs"
            )

            raise AssertionError(
                f"{col} contains NULL values"
            )

    null_customer_id = (
        ml_features["customer_i_d"].isna().sum()
    )

    null_monthly_charges = (
        ml_features["monthly_charges"].isna().sum()
    )

    invalid_churn = (
        ~ml_features["churn"].isin([0, 1])
    ).sum()

    if null_customer_id == 0:
        print("PASS - customer_id NULL check: 0")
    else:
        print(
            f"FAIL - customer_id NULL check: "
            f"{null_customer_id}"
        )
        raise AssertionError(
            "customer_id contains NULLs"
        )
    if null_monthly_charges == 0:
        print(
            "PASS - monthly_charges NULL check: 0"
        )
    else:
        print(
            f"FAIL - monthly_charges NULL check: "
            f"{null_monthly_charges}"
        )
        raise AssertionError(
            "monthly_charges contains NULLs"
        )

    if invalid_churn == 0:
        print(
            "PASS - churn values check: 0 invalid"
        )
    else:
        print(
            f"FAIL - churn values check: "
            f"{invalid_churn} invalid"
        )
        raise AssertionError(
            "Invalid churn values"
        )

    feature_count = len(ml_features)
    if feature_count == cleaned_count:
        print(
            f"PASS - Row count: "
            f"{feature_count}/{cleaned_count}"
        )
    else:
        print(
            f"FAIL - Row count: "
            f"{feature_count}/{cleaned_count}"
        )
        raise AssertionError(
            "Row count mismatch"
        )
    ml_features.to_sql(
        "customer_ml_features",
        engine,
        if_exists="replace",
        index=False
    )
    print("\nSUCCESS")
    print(
        "customer_ml_features populated with "
        f"{len(ml_features)} rows and "
        f"{len(ml_features.columns)} columns."
    )

    return ml_features
if __name__ == "__main__":
    engine = create_engine(
        "mysql+pymysql://root:root@localhost/telecom_db_de"
    )
    build_ml_features(engine)