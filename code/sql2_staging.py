import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "mysql+pymysql://root:root@localhost/telecom_db"
)

df = pd.read_csv("customer_churn.csv")

df.to_sql(
    "stg_customer_raw",
    engine,
    if_exists="append",
    index=False
)

print("Data loaded successfully.")