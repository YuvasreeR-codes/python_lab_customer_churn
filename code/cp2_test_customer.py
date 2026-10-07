import pandas as pd
from cp2_customer_cleaner import CustomerCleaner

# Load dataset
df = pd.read_csv("customer_churn.csv")

print("Before Cleaning")
print("-" * 50)
print("Shape:", df.shape)
print(df.dtypes)

# Clean
cleaner = CustomerCleaner(df)
clean_df = cleaner.clean()

print("\nAfter Cleaning")
print("-" * 50)
print("Shape:", clean_df.shape)
print(clean_df.dtypes)

print("\nFirst Five Rows")
print(clean_df.head())