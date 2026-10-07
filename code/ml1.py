import pandas as pd

df = pd.read_csv(r"output\customer_features_20260731_120356.csv")
print("Original shape:", df.shape)
print(df.columns.tolist())

y = df["churn"]

numeric_cols = [
    "tenure",
    "monthly_charges",
    "total_charges",
    "service_count",
    "high_charge_flag",
    "is_long_term_customer",
    "has_streaming_bundle",
    "auto_pay_flag" ]


categorical_cols = ["contract", "internet_service"]
X = df[numeric_cols + categorical_cols].copy()
X = pd.get_dummies(X,columns=categorical_cols, drop_first=False)
# print("\nFinal feature set:")
# print(X.head)

# print("\nTarget:")
# print(y.head)

# print("\nX shape:", X.shape)
# print("y shape:", y.shape)

# print("\nClass balance:")
# print(y.value_counts(normalize=True))

# print("\nClass counts:")
# print(y.value_counts())

import os
import joblib

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

print("Training shape:", X_train.shape)
print("Testing shape:", X_test.shape)

logistic_model = make_pipeline(
    StandardScaler(),
    LogisticRegression(max_iter=1000)
)

tree_model = DecisionTreeClassifier(
    max_depth=5,
    random_state=42
)

logistic_model.fit(X_train, y_train)
tree_model.fit(X_train, y_train)

logistic_pred = logistic_model.predict(X_test)
tree_pred = tree_model.predict(X_test)

print("\n" + "=" * 60)
print("LOGISTIC REGRESSION")
print("=" * 60)
print("\nClassification Report:")
print(
    classification_report(
        y_test,
        logistic_pred,
        target_names=["Active", "Churned"]
    )
)
print("Confusion Matrix:")
print(confusion_matrix(y_test, logistic_pred))


print("\n" + "=" * 60)
print("DECISION TREE")
print("=" * 60)
print("\nClassification Report:")
print(
    classification_report(
        y_test,
        tree_pred,
        target_names=["Active", "Churned"]
    )
)
print("Confusion Matrix:")
print(confusion_matrix(y_test, tree_pred))

logistic_cv_f1 = cross_val_score(
    logistic_model,
    X,
    y,
    cv=5,
    scoring="f1"
)

tree_cv_f1 = cross_val_score(
    tree_model,
    X,
    y,
    cv=5,
    scoring="f1"
)

print("\n5-Fold CV F1 Scores")
print("Logistic Regression:", logistic_cv_f1)
print("Logistic Mean CV F1:", logistic_cv_f1.mean())
print("Decision Tree:", tree_cv_f1)
print("Decision Tree Mean CV F1:", tree_cv_f1.mean())

comparison = pd.DataFrame({
    "Model": [
        "Logistic Regression",
        "Decision Tree"
    ],

    "Accuracy": [
        accuracy_score(y_test, logistic_pred),
        accuracy_score(y_test, tree_pred)
    ],

    "Precision (Churned)": [
        precision_score(y_test, logistic_pred),
        precision_score(y_test, tree_pred)
    ],

    "Recall (Churned)": [
        recall_score(y_test, logistic_pred),
        recall_score(y_test, tree_pred)
    ],

    "F1 (Churned)": [
        f1_score(y_test, logistic_pred),
        f1_score(y_test, tree_pred)
    ],

    "CV F1": [
        logistic_cv_f1.mean(),
        tree_cv_f1.mean()
    ]
})

print("\n" + "=" * 80)
print("MODEL COMPARISON")
print("=" * 80)
print(comparison.round(4))

logistic_f1 = f1_score(y_test, logistic_pred)
tree_f1 = f1_score(y_test, tree_pred)

if logistic_f1 > tree_f1:
    print("\nBetter model: Logistic Regression")
    print(
        "Logistic Regression has the higher F1 score "
        "for the Churned class."
    )
else:
    print("\nBetter model: Decision Tree")
    print(
        "Decision Tree has the higher F1 score "
        "for the Churned class."
    )

os.makedirs("models", exist_ok=True)
joblib.dump(
    logistic_model,
    "models/logistic_churn.pkl"
)
joblib.dump(
    tree_model,
    "models/tree_churn.pkl"
)
print("\nModels saved successfully:")
print("models/logistic_churn.pkl")
print("models/tree_churn.pkl")






