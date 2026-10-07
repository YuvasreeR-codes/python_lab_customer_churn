import logging
import pandas as pd
import re

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class CustomerCleaner:
    def __init__(self, df):
        # Work on a copy so the original DataFrame is unchanged
        self.df = df.copy()

    def standardize_column_names(self):
        """
        Convert column names to lowercase snake_case.
        Example:
        MonthlyCharges -> monthly_charges
        PaperlessBilling -> paperless_billing
        """

        new_columns = []

        for col in self.df.columns:
            col = re.sub(r'(?<!^)(?=[A-Z])', '_', col)
            col = col.lower()
            new_columns.append(col)

        self.df.columns = new_columns

        logging.info("Column names standardized to snake_case.")

    def fix_total_charges(self):
        """
        Replace blank strings with NaN and convert total_charges to float.
        """

        try:
            blanks = (
                self.df["total_charges"]
                .astype(str)
                .str.strip()
                .eq("")
                .sum()
            )

            self.df["total_charges"] = (
                self.df["total_charges"]
                .replace(r'^\s*$', pd.NA, regex=True)
            )

            self.df["total_charges"] = pd.to_numeric(
                self.df["total_charges"],
                errors="coerce"
            )

            logging.info(
                f"Converted total_charges to float. "
                f"{blanks} blank values converted to NaN."
            )

        except Exception as e:
            logging.exception(
                f"Unexpected error while cleaning total_charges: {e}"
            )

    def normalize_binary_columns(self):

        binary_columns = [
            "partner",
            "dependents",
            "phone_service",
            "paperless_billing",
            "churn"
        ]

        mapping = {
            "Yes": 1,
            "No": 0
        }

        for col in binary_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].map(mapping)

        logging.info("Binary columns normalized.")

    def handle_nulls(self):
        missing = self.df["total_charges"].isna().sum()

        self.df["total_charges"] = self.df["total_charges"].fillna(
            self.df["monthly_charges"]
        )

        logging.info(
            f"Filled {missing} missing total_charges values "
            "using monthly_charges."
        )

    def clean(self):
      
        logging.info("Starting customer data cleaning.")

        self.standardize_column_names()
        self.fix_total_charges()
        self.normalize_binary_columns()
        self.handle_nulls()

        logging.info("Customer data cleaning completed.")

        return self.df