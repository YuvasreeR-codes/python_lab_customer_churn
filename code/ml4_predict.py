import joblib
import pandas as pd

# Load model once when the application starts
model = joblib.load("models/tree_churn.pkl")

# Exact feature order used during training
FEATURE_COLUMNS = ["tenure", "monthly_charges", "total_charges", "service_count", "high_charge_flag", "is_long_term_customer", "has_streaming_bundle", "auto_pay_flag", "contract_Month-to-month", "contract_One year", "contract_Two year", "internet_service_DSL", "internet_service_Fiber optic", "internet_service_No"]

# def preprocess_input(tenure, monthly_charges, contract_type, service_count):
#     # ----------------------------------------
#     # Original numeric features
#     # ----------------------------------------
#     total_charges = monthly_charges * tenure
#     high_charge_flag = 1 if  monthly_charges > 70.35 else 0
#     is_long_term_customer = 1 if tenure >= 24 else 0
#     has_streaming_bundle = 0
#     auto_pay_flag = 0
#     contract_month_to_month = 0
#     contract_one_year = 0
#     contract_two_year = 0
#
#     if contract_type == "Month-to-month":
#         contract_month_to_month = 1
#     elif contract_type == "One year":
#         contract_one_year = 1
#     elif contract_type == "Two year":
#         contract_two_year = 1
#
#     internet_service_dsl = 0
#     internet_service_fiber = 0
#     internet_service_no = 0
#
#     data = {
#         "tenure": tenure, "monthly_charges": monthly_charges, "total_charges": total_charges,
#         "service_count": service_count, "high_charge_flag": high_charge_flag,
#         "is_long_term_customer": is_long_term_customer, "has_streaming_bundle": has_streaming_bundle,
#         "auto_pay_flag": auto_pay_flag, "contract_Month-to-month": contract_month_to_month,
#         "contract_One year": contract_one_year, "contract_Two year": contract_two_year,
#         "internet_service_DSL": internet_service_dsl, "internet_service_Fiber optic": internet_service_fiber,
#         "internet_service_No": internet_service_no
#     }
#
#     df = pd.DataFrame([data], columns=FEATURE_COLUMNS)
#     return df
#
# def predict_churn_ml(tenure, monthly_charges, contract_type, service_count):
#     # Preprocess input
#     features = preprocess_input(tenure, monthly_charges, contract_type, service_count)
#
#     # Model prediction
#     prediction = model.predict(features)[0]
#
#     # Probability of churn
#     probabilities = model.predict_proba(features)[0]
#     risk_score = probabilities[1]
#
#     # Confidence = probability of predicted class
#     confidence = max(probabilities)
#
#     return {
#         "risk_score": float(risk_score),
#         "prediction": ("Likely to churn" if prediction == 1 else "Unlikely to churn"),
#         "confidence": float(confidence)
#     }


def preprocess_input(tenure, monthly_charges, contract_type, service_count, has_streaming_bundle, auto_pay_flag, internet_service):
    total_charges = monthly_charges * tenure
    high_charge_flag = 1 if monthly_charges > 70.35 else 0
    is_long_term_customer = 1 if tenure >= 24 else 0

    contract_month_to_month = 0
    contract_one_year = 0
    contract_two_year = 0

    if contract_type == "Month-to-month":
        contract_month_to_month = 1
    elif contract_type == "One year":
        contract_one_year = 1
    elif contract_type == "Two year":
        contract_two_year = 1

    internet_service_dsl = 0
    internet_service_fiber = 0
    internet_service_no = 0

    if internet_service == "DSL":
        internet_service_dsl = 1
    elif internet_service == "Fiber optic":
        internet_service_fiber = 1
    elif internet_service == "No":
        internet_service_no = 1

    data = {
        "tenure": tenure,
        "monthly_charges": monthly_charges,
        "total_charges": total_charges,
        "service_count": service_count,
        "high_charge_flag": high_charge_flag,
        "is_long_term_customer": is_long_term_customer,
        "has_streaming_bundle": has_streaming_bundle,
        "auto_pay_flag": auto_pay_flag,
        "contract_Month-to-month": contract_month_to_month,
        "contract_One year": contract_one_year,
        "contract_Two year": contract_two_year,
        "internet_service_DSL": internet_service_dsl,
        "internet_service_Fiber optic": internet_service_fiber,
        "internet_service_No": internet_service_no
    }
    df = pd.DataFrame([data], columns=FEATURE_COLUMNS)
    return df

def predict_churn_ml(tenure, monthly_charges, contract_type, service_count, has_streaming_bundle, auto_pay_flag, internet_service):
    features = preprocess_input(tenure, monthly_charges, contract_type, service_count, has_streaming_bundle, auto_pay_flag, internet_service)
    # Model prediction
    prediction = model.predict(features)[0]
    # Probability
    probabilities = model.predict_proba(features)[0]
    risk_score = probabilities[1]
    confidence = max(probabilities)
    return {
        "risk_score": float(risk_score),
        "prediction": ("Likely to churn" if prediction == 1 else "Unlikely to churn"),
        "confidence": float(confidence)
    }