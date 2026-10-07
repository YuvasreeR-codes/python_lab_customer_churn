import pandas as pd
from code.cp2_customer_cleaner import CustomerCleaner

# ----------------------------
# Load and clean the dataset
# ----------------------------
df = pd.read_csv("customer_churn.csv")

cleaner = CustomerCleaner(df)
df = cleaner.clean()

# ----------------------------
# 1. Churn rate by Contract
# ----------------------------
print("\n===== Churn Rate by Contract =====")

contract_churn = (
    df.groupby("contract")["churn"]
      .mean()
      .sort_values(ascending=False)
      * 100
)

print(contract_churn)

highest_contract = contract_churn.idxmax()

print(f"\nHighest Churn Contract: {highest_contract}")

# ----------------------------
# 2. Churn rate by Internet Service
# ----------------------------
print("\n===== Churn Rate by Internet Service =====")

internet_churn = (
    df.groupby("internet_service")["churn"]
      .mean()
      * 100
)

print(internet_churn)

# ----------------------------
# 3. Churn rate by Payment Method
# ----------------------------
print("\n===== Churn Rate by Payment Method =====")

payment_churn = (
    df.groupby("payment_method")["churn"]
      .mean()
      * 100
)

print(payment_churn)

# ----------------------------
# 4. Tenure Buckets
# ----------------------------

df["tenure_bucket"] = pd.cut(
    df["tenure"],
    bins=[0, 12, 24, 48, 72],
    labels=["0-12", "13-24", "25-48", "49-72"],
    include_lowest=True
)

print("\n===== Churn Rate by Tenure Bucket =====")

tenure_churn = (
    df.groupby("tenure_bucket")["churn"]
      .mean()
      * 100
)

print(tenure_churn)

# ----------------------------
# 5. Average Monthly Charges
# ----------------------------
print("\n===== Average Monthly Charges =====")

avg_monthly = (
    df.groupby("churn")["monthly_charges"]
      .mean()
)

print(avg_monthly)

# ----------------------------
# 6. Highest Churn Combination
# ----------------------------
print("\n===== Contract + Internet Service =====")

combo = (
    df.groupby(["contract", "internet_service"])["churn"]
      .mean()
      .sort_values(ascending=False)
      * 100
)

print(combo)

print("\nHighest Risk Combination:")
print(combo.head(1))