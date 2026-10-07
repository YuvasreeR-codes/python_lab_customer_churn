# import pandas as pd 
# df = pd.read_csv("telecom_churn.csv") 
# assert df.shape == (7043, 21), f"Unexpected shape: {df.shape}" 
# assert "customerID" in df.columns, "Missing customerID column" 
# assert "Churn" in df.columns, "Missing Churn column" 
# print("Dataset OK:", df.shape) 

# import csv

# with open("telecom_churn.csv", "r") as file:
#     reader = csv.reader(file)
#     columns = next(reader)   # First row (header)

# print(columns)

import csv

with open("telecom_churn.csv", "r") as file:
    reader = csv.DictReader(file)
    rows = list(reader)

# -------------------------------
# Shape
# -------------------------------
num_rows = len(rows)
num_cols = len(reader.fieldnames)

print("Shape:", (num_rows, num_cols))

# -------------------------------
# Column names
# -------------------------------
print("\nColumns:")
for col in reader.fieldnames:
    print(col)

# # -------------------------------
# # Data types (guessed)
# # -------------------------------
# print("\nData Types:")

# for col in reader.fieldnames:
#     values = [row[col] for row in rows if row[col] != ""]

#     dtype = "string"

#     try:
#         for v in values:
#             int(v)
#         dtype = "int"
#     except:
#         try:
#             for v in values:
#                 float(v)
#             dtype = "float"
#         except:
#             dtype = "string"

#     print(col, ":", dtype)

# # -------------------------------
# # Null count and percentage
# # -------------------------------
# print("\nNull Values")

# for col in reader.fieldnames:
#     nulls = sum(1 for row in rows if row[col] == "")
#     percent = (nulls / num_rows) * 100
#     print(f"{col}: {nulls} ({percent:.2f}%)")

# # -------------------------------
# # Categorical columns
# # -------------------------------
# categorical = [
#     "gender",
#     "telecom_partner",
#     "state",
#     "city",
#     "churn"
# ]

# print("\nCategorical Analysis")

# for col in categorical:
#     counts = {}

#     for row in rows:
#         value = row[col]
#         counts[value] = counts.get(value, 0) + 1

#     print("\n", col)
#     print("Unique:", list(counts.keys()))

#     for k, v in counts.items():
#         print(k, ":", v)

# # -------------------------------
# # Churn Rate
# # -------------------------------
# counts = {}

# for row in rows:
#     value = row["churn"]
#     counts[value] = counts.get(value, 0) + 1

# print("\nChurn Counts")
# print(counts)

# yes = counts.get("1", 0)
# rate = (yes / num_rows) * 100

# print("Churn Rate:", round(rate, 2), "%")

# # -------------------------------
# # Numeric Summary
# # -------------------------------
# numeric_cols = [
#     "age",
#     "estimated_salary",
#     "calls_made",
#     "sms_sent",
#     "data_used",
#     "num_dependents"
# ]

# print("\nNumeric Summary")

# for col in numeric_cols:

#     values = []

#     for row in rows:
#         if row[col] != "":
#             values.append(float(row[col]))

#     print("\n", col)
#     print("Min:", min(values))
#     print("Max:", max(values))
#     print("Mean:", sum(values) / len(values))