import os
import csv
import shutil
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime


EXPECTED_COLS = [
    "customerID", "gender", "SeniorCitizen", "Partner", "Dependents",
    "tenure", "PhoneService", "MultipleLines", "InternetService",
    "OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport",
    "StreamingTV", "StreamingMovies", "Contract", "PaperlessBilling",
    "PaymentMethod", "MonthlyCharges", "TotalCharges", "Churn"
]

LANDING_DIR = "data/landing"
RAW_DIR = "data/raw"
REJECTED_DIR = "data/rejected"
LOG_DIR = "data/logs"


def detect_files():
    """Return all CSV files present in landing/."""

    files = []

    for filename in os.listdir(LANDING_DIR):
        if filename.lower().endswith(".csv"):
            files.append(os.path.join(LANDING_DIR, filename))

    return files


def validate_schema(filepath):
    """Check whether CSV header exactly matches EXPECTED_COLS."""

    with open(filepath, newline="", encoding="utf-8") as f:
        header = next(csv.reader(f))

    return header == EXPECTED_COLS, header


def load_to_staging(filepath, engine):
    """Load valid CSV into staging table."""

    df = pd.read_csv(filepath)

    df.to_sql(
        "stg_customer_raw",
        engine,
        if_exists="replace",
        index=False
    )

    return len(df)


def log_ingestion(filename, status, rows, reason, engine):
    """Insert ingestion result into ingestion_log."""

    log_data = pd.DataFrame([{
        "filename": filename,
        "status": status,
        "rows": rows,
        "reason": reason,
        "ingested_at": datetime.now()
    }])

    log_data.to_sql(
        "ingestion_log",
        engine,
        if_exists="append",
        index=False
    )


def process_landing(engine):
    """Detect, validate, load and log each landing file."""

    files = detect_files()

    for filepath in files:

        filename = os.path.basename(filepath)

        # 1. Validate schema
        valid, header = validate_schema(filepath)

        if not valid:

            print(f"REJECTED: {filename}")

            log_ingestion(
                filename=filename,
                status="REJECTED",
                rows=0,
                reason="Schema validation failed",
                engine=engine
            )

            shutil.move(
                filepath,
                os.path.join(REJECTED_DIR, filename)
            )

            continue

        # 2. Load into staging
        try:
            rows = load_to_staging(filepath, engine)

            print(f"LOADED: {filename} ({rows} rows)")

            log_ingestion(
                filename=filename,
                status="LOADED",
                rows=rows,
                reason="Schema valid and loaded successfully",
                engine=engine
            )

            # Move successfully processed file
            shutil.move(
                filepath,
                os.path.join(RAW_DIR, filename)
            )

        except Exception as e:

            print(f"ERROR: {filename} -> {e}")

            log_ingestion(
                filename=filename,
                status="ERROR",
                rows=0,
                reason=str(e),
                engine=engine
            )


if __name__ == "__main__":

    # Change these according to your MySQL setup
    engine = create_engine(
        "mysql+pymysql://root:root@localhost/telecom_db_de"
    )

    # Create required folders
    os.makedirs(LANDING_DIR, exist_ok=True)
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(REJECTED_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)

    process_landing(engine)