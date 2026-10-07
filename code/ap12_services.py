from sqlalchemy import text


def get_churn_summary(db):
    # 1. Overall churn summary

    overall_query = text("""
        SELECT
            COUNT(*) AS total_customers,
            SUM(churn) AS total_churned,
            AVG(churn) AS churn_rate
        FROM fact_customer_account
    """)

    overall = db.execute(overall_query).mappings().first()

    # 2. Churn rate by contract type

    contract_query = text("""
        SELECT
            dc.contract_name AS contract_type,
            AVG(f.churn) AS churn_rate
        FROM fact_customer_account f
        JOIN dim_contract dc
            ON f.contract_id = dc.contract_id
        GROUP BY dc.contract_name
        ORDER BY dc.contract_name
    """)

    contract_results = db.execute(contract_query).mappings().all()

    # 3. Churn rate by internet service

    internet_query = text("""
        SELECT
            s.InternetService AS internet_service,
            AVG(f.churn) AS churn_rate
        FROM fact_customer_account f
        JOIN stg_customer_raw s
            ON f.customer_id = s.customerID
        GROUP BY s.InternetService
        ORDER BY s.InternetService
    """)

    internet_results = db.execute(internet_query).mappings().all()

    # Return structured result

    return {
        "total_customers": overall["total_customers"],
        "total_churned": overall["total_churned"],
        "churn_rate": float(overall["churn_rate"]),

        "churn_rate_by_contract": [
            {
                "contract_type": row["contract_type"],
                "churn_rate": float(row["churn_rate"])
            }
            for row in contract_results
        ],

        "churn_rate_by_internet_service": [
            {
                "internet_service": row["internet_service"],
                "churn_rate": float(row["churn_rate"])
            }
            for row in internet_results
        ]
    }