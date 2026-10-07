import pandas as pd
import joblib
import matplotlib.pyplot as plt

# Load CP4 CSV
df = pd.read_csv("output\customer_features_20260731_120356.csv")

# Load best model from ML2
tree_model = joblib.load("models/tree_churn.pkl")

# Same features used in ML2
numeric_cols = ["tenure", "monthly_charges", "total_charges", "service_count", "high_charge_flag", "is_long_term_customer", "has_streaming_bundle", "auto_pay_flag"]
categorical_cols = ["contract", "internet_service"]

# Create X exactly as in ML2
X = df[numeric_cols + categorical_cols].copy()

X = pd.get_dummies(X, columns=categorical_cols, drop_first=False)

# Feature importances
importance = pd.Series(tree_model.feature_importances_, index=X.columns)
importance = importance.sort_values(ascending=False)

print("\nFeature Importances:")
print(importance)

top10 = importance.head(10).sort_values()

plt.figure(figsize=(8, 5))
top10.plot(kind="barh")

plt.title("Top 10 Features Driving Churn")
plt.xlabel("Feature Importance")
plt.ylabel("Feature")

plt.tight_layout()
plt.show()

top3 = importance.head(3)

print("\nTop 3 Churn Drivers:")
print(top3)

from sklearn.model_selection import train_test_split

y = df["churn"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# 259. Predict churn probability
churn_prob = tree_model.predict_proba(X_test)[:, 1]

print("\nFirst 10 churn probabilities:")
print(churn_prob[:10])

test_customer_ids = df.loc[X_test.index, "customer_i_d"]
risk_df = pd.DataFrame({"customer_i_d": test_customer_ids, "churn_probability": churn_prob})

risk_df = risk_df.sort_values(by="churn_probability", ascending=False)

top20 = risk_df.head(20)

print(tree_model.classes_)
print("\nTop 20 Highest-Risk Customers:")
print(top20.to_string(index=False))