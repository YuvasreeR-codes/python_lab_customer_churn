import os
import logging
from datetime import datetime

import pandas as pd

from code.cp2_customer_cleaner import CustomerCleaner
from code.cp4_feat_engg import build_features


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def load_data(filepath):

    try:
        df = pd.read_csv(filepath)

        logging.info(f"Successfully loaded {len(df)} rows from '{filepath}'")

        return df

    except Exception as e:
        logging.exception("Error while loading data.")
        raise


def save_outputs(clean_df, feature_df, output_dir):

    try:

        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        clean_file = os.path.join(
            output_dir,
            f"customer_clean_{timestamp}.csv"
        )

        feature_file = os.path.join(
            output_dir,
            f"customer_features_{timestamp}.csv"
        )

        clean_df.to_csv(clean_file, index=False)
        feature_df.to_csv(feature_file, index=False)

        logging.info(f"Clean dataset saved to: {clean_file}")
        logging.info(f"Feature dataset saved to: {feature_file}")

    except Exception:
        logging.exception("Error while saving output files.")
        raise


# ---------------------------------------------------
# Main Pipeline
# ---------------------------------------------------

def main():

    logging.info("=" * 50)
    logging.info("Customer ETL Pipeline Started")
    logging.info("=" * 50)

    try:
        # -----------------------------
        # Step 1 : Load
        # -----------------------------
        raw_df = load_data("customer_churn.csv")

        # -----------------------------
        # Step 2 : Clean
        # -----------------------------
        try:
            cleaner = CustomerCleaner(raw_df)
            clean_df = cleaner.clean()

            logging.info(
                f"Cleaning completed successfully. Rows: {len(clean_df)}"
            )

        except Exception:
            logging.exception("Cleaning step failed.")
            raise

        # -----------------------------
        # Step 3 : Feature Engineering
        # -----------------------------
        try:
            feature_df = build_features(clean_df.copy())

            logging.info(
                f"Feature engineering completed. Rows: {len(feature_df)}"
            )

        except Exception:
            logging.exception("Feature engineering failed.")
            raise

        # -----------------------------
        # Step 4 : Data Quality Checks
        # -----------------------------
        try:

            assert (
                feature_df["monthly_charges"].isnull().sum() == 0
            ), "monthly_charges contains NULL values."

            assert (
                set(feature_df["churn"].unique()).issubset({0, 1})
            ), "churn column contains values other than 0 and 1."

            logging.info("Data quality checks passed.")

        except Exception:
            logging.exception("Data quality validation failed.")
            raise

        # -----------------------------
        # Step 5 : Save
        # -----------------------------
        try:
            save_outputs(
                clean_df,
                feature_df,
                "output"
            )

        except Exception:
            logging.exception("Saving outputs failed.")
            raise

        logging.info("=" * 50)
        logging.info("Pipeline Completed Successfully")
        logging.info("=" * 50)

    except Exception:
        logging.exception("Pipeline execution failed.")
        raise


# ---------------------------------------------------

if __name__ == "__main__":
    main()