import pandas as pd

# -----------------------------
# Load dataset
# -----------------------------
df = pd.read_csv("customer_churn.csv")

# -----------------------------
# 1. Print dataset shape
# -----------------------------
print("=" * 50)
print("Dataset Shape")
print("=" * 50)
print(f"Rows: {df.shape[0]}")
print(f"Columns: {df.shape[1]}")

# -----------------------------
# 2. Column names and data types
# -----------------------------
print("\n" + "=" * 50)
print("Column Names and Data Types")
print("=" * 50)

print(df.dtypes)

# -----------------------------
# 3. Null values and percentages
# -----------------------------
print("\n" + "=" * 50)
print("Null Values")
print("=" * 50)

null_counts = df.isnull().sum()
null_percentage = (null_counts / len(df)) * 100

null_df = pd.DataFrame({
    "Null Count": null_counts,
    "Null Percentage": null_percentage.round(2)
})

print(null_df)

# -----------------------------
# 4. Categorical column analysis
# -----------------------------
categorical_columns = [
    "gender",
    "Partner",
    "Dependents",
    "PhoneService",
    "InternetService",
    "Contract",
    "PaymentMethod",
    "Churn"
]

print("\n" + "=" * 50)
print("Categorical Columns")
print("=" * 50)

for col in categorical_columns:
    print(f"\nColumn: {col}")
    print("-" * 40)

    print("Unique Values:")
    print(df[col].unique())

    print("\nValue Counts:")
    print(df[col].value_counts())

    print("\nValue Percentages:")
    print(df[col].value_counts(normalize=True) * 100)

# -----------------------------
# 5. Churn rate
# -----------------------------
print("\n" + "=" * 50)
print("Churn Analysis")
print("=" * 50)

churn_counts = df["Churn"].value_counts()
print(churn_counts)

churn_rate = (df["Churn"] == "Yes").mean() * 100

print(f"\nChurn Rate: {churn_rate:.2f}%")

# -----------------------------
# 6. TotalCharges inspection
# -----------------------------
print("\n" + "=" * 50)
print("TotalCharges Inspection")
print("=" * 50)

print("Original dtype:")
print(df["TotalCharges"].dtype)

total_numeric = pd.to_numeric(df["TotalCharges"], errors="coerce")

print("\nNaN values after conversion:")
print(total_numeric.isna().sum())

# -----------------------------
# 7. Numerical statistics
# -----------------------------
print("\n" + "=" * 50)
print("Numerical Summary")
print("=" * 50)

print("Tenure")
print(f"Min : {df['tenure'].min()}")
print(f"Max : {df['tenure'].max()}")
print(f"Mean: {df['tenure'].mean():.2f}")

print("\nMonthlyCharges")
print(f"Min : {df['MonthlyCharges'].min()}")
print(f"Max : {df['MonthlyCharges'].max()}")
print(f"Mean: {df['MonthlyCharges'].mean():.2f}")

print("\nTotalCharges")

print(f"Min : {total_numeric.min():.2f}")
print(f"Max : {total_numeric.max():.2f}")
print(f"Mean: {total_numeric.mean():.2f}")

# -----------------------------
# 8. Profiling Summary
# -----------------------------
print("\n" + "=" * 50)
print("Profiling Summary")
print(df.info())
print("=" * 50)

