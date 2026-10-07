# import pandas as pd
# import joblib
# from datetime import datetime
# from sqlalchemy import create_engine

# model = joblib.load("models/tree_churn.pkl")
# df = pd.read_csv("customer_features1.csv")

# print("Total customers:", len(df))

# numeric_cols = ["tenure", "monthly_charges", "total_charges", "service_count", "high_charge_flag", "is_long_term_customer", "has_streaming_bundle", "auto_pay_flag"]
# categorical_cols = ["contract", "internet_service"]

# X = df[numeric_cols + categorical_cols].copy()
# X = pd.get_dummies(X, columns=categorical_cols, drop_first=False)

# probabilities = model.predict_proba(X)[:, 1]
# predictions = model.predict(X)

# # Convert prediction to business-friendly label
# prediction_labels = ["Likely to churn" if prediction == 1 else "Unlikely to churn" for prediction in predictions]

# # Confidence = probability of predicted class
# confidence = [probability if prediction == 1 else 1 - probability for probability, prediction in zip(probabilities, predictions)]

# scoring_date = datetime.today().strftime("%Y-%m-%d")

# risk_df = pd.DataFrame({
#     "customer_id": df["customer_i_d"],
#     "risk_score": probabilities,
#     "prediction": prediction_labels,
#     "confidence": confidence,
#     "scoring_date": scoring_date
# })

# # Save CSV
# # risk_df.to_csv("customer_risk_table.csv", index=False)
# # print("\nCustomer risk table saved:")
# # print("customer_risk_table.csv")

# print("\nPrediction Summary:")
# print(risk_df["prediction"].value_counts())

# print("\nPrediction Percentages:")
# print(risk_df["prediction"].value_counts(normalize=True).mul(100).round(2))

# print("\nTop 10 Highest-Risk Customers:")

# top10 = risk_df.sort_values(by="risk_score", ascending=False).head(10)

# print(top10[["customer_id", "risk_score", "prediction", "confidence"]].to_string(index=False))




import pandas as pd
import joblib
from datetime import datetime
from sqlalchemy import create_engine

model = joblib.load("models/tree_churn.pkl")

df = pd.read_csv("customer_features1.csv")
print("Total customers:", len(df))
numeric_cols = [
    "tenure",
    "monthly_charges",
    "total_charges",
    "service_count",
    "high_charge_flag",
    "is_long_term_customer",
    "has_streaming_bundle",
    "auto_pay_flag"
]

categorical_cols = [
    "contract",
    "internet_service"
]

def predict_churn(row):

    row_df = pd.DataFrame([row])

    X = row_df[numeric_cols + categorical_cols].copy()

    X = pd.get_dummies(
        X,
        columns=categorical_cols,
        drop_first=False
    )

    # Align columns with training data
    model_features = model.feature_names_in_

    X = X.reindex(
        columns=model_features,
        fill_value=0
    )

    probability = model.predict_proba(X)[0, 1]
    prediction = model.predict(X)[0]

    prediction_label = (
        "Likely to churn"
        if prediction == 1
        else "Unlikely to churn"
    )

    confidence = (
        probability
        if prediction == 1
        else 1 - probability
    )

    return pd.Series({
        "risk_score": probability,
        "prediction": prediction_label,
        "confidence": confidence
    })


# =========================
# Score All Customers
# =========================
results = df.apply(
    predict_churn,
    axis=1
)

df_scored = pd.concat(
    [df, results],
    axis=1
)

# =========================
# Add Scoring Date
# =========================
df_scored["scoring_date"] = datetime.today().strftime("%Y-%m-%d")

risk_df = df_scored[
    [
        "customer_i_d",
        "risk_score",
        "prediction",
        "confidence",
        "scoring_date"
    ]
].rename(
    columns={
        "customer_i_d": "customer_id"
    }
)

risk_df.to_csv(
    "customer_risk_table.csv",
    index=False
)

print("\nCustomer risk table saved:")
print("customer_risk_table.csv")

# SQL Output (Optional)
# risk_df.to_sql(
#     "customer_risk_table",
#     engine,
#     if_exists="replace",
#     index=False
# )

print("\nPrediction Summary:")
print(
    risk_df["prediction"]
    .value_counts()
)

print("\nPrediction Percentages:")
print(
    risk_df["prediction"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)

# Estimated churn rate
churn_rate = (
    (risk_df["prediction"] == "Likely to churn")
    .mean()
    * 100
)

print(f"\nPredicted Churn Rate: {churn_rate:.2f}%")
print("Expected: approximately 27% based on training distribution")

# Top 10 High-Risk Customers
print("\nTop 10 Highest-Risk Customers:")

top10 = (
    risk_df
    .sort_values(
        by="risk_score",
        ascending=False
    )
    .head(10)
)

print(
    top10[
        [
            "customer_id",
            "risk_score",
            "prediction",
            "confidence"
        ]
    ].to_string(index=False)
)