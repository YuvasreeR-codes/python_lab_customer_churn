import pandas as pd
from cp2_customer_cleaner import CustomerCleaner

# ----------------------------------------
# Load and clean data
# ----------------------------------------

df = pd.read_csv("customer_churn.csv")

cleaner = CustomerCleaner(df)
df = cleaner.clean()
print(df.columns)


def build_features(df):
    # ----------------------------------------
    # Feature 1 - tenure_bucket
    # ----------------------------------------

    df["tenure_bucket"] = pd.cut(
        df["tenure"],
        bins=[0, 12, 24, 48, 72],
        labels=["0-12", "13-24", "25-48", "49-72"],
        include_lowest=True
    )

    # ----------------------------------------
    # Feature 2 - high_charge_flag
    # ----------------------------------------

    median_charge = df["monthly_charges"].median()
    print("median charge is")
    print(median_charge)

    df["high_charge_flag"] = (
        df["monthly_charges"] > median_charge
    ).astype(int)

    # ----------------------------------------
    # Convert service columns to 1/0
    # (needed because they contain Yes/No)
    # ----------------------------------------

    service_columns = [
        "online_security",
        "online_backup",
        "device_protection",
        "tech_support",
        "streaming_t_v",
        "streaming_movies"
    ]

    for col in service_columns:
        df[col] = df[col].map({"Yes": 1, "No": 0}).fillna(0).astype(int)

    # ----------------------------------------
    # Feature 3 - service_count
    # ----------------------------------------

    df["service_count"] = df[service_columns].sum(axis=1)

    # ----------------------------------------
    # Feature 4 - is_long_term_customer
    # ----------------------------------------

    df["is_long_term_customer"] = (
        df["tenure"] >= 24
    ).astype(int)

    # ----------------------------------------
    # Feature 5 - has_streaming_bundle
    # ----------------------------------------

    df["has_streaming_bundle"] = (
        (df["streaming_t_v"] == 1) &
        (df["streaming_movies"] == 1)
    ).astype(int)

    # ----------------------------------------
    # Feature 6 - auto_pay_flag
    # ----------------------------------------

    df["auto_pay_flag"] = (
        df["payment_method"]
        .str.contains("automatic", case=False, na=False)
    ).astype(int)

    
# ----------------------------------------
# Correlation with churn
# ----------------------------------------

    print("\nCorrelation with Churn\n")

    features = [
        "high_charge_flag",
        "service_count",
        "is_long_term_customer",
        "has_streaming_bundle",
        "auto_pay_flag"
    ]

    for feature in features:
        corr = df[feature].corr(df["churn"])
        print(f"{feature:25s}: {corr:.4f}")

    return df

# ----------------------------------------
# Save dataset
# ----------------------------------------
df = build_features(df)

df.to_csv("customer_features1.csv", index=False)

print("\ncustomer_features.csv saved successfully.")