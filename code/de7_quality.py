from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import json
import os
from datetime import datetime

import os
os.environ["HADOOP_HOME"] = r"C:\Users\yuvasree.r\Desktop\python test\hadoop"
os.environ["PATH"] = os.environ["PATH"] + r";C:\Users\yuvasree.r\Desktop\python test\hadoop\bin"

spark = (
    SparkSession.builder
    .appName("CustomerDataQuality")
    .master("local[2]")
    .config("spark.driver.memory", "4g")
    .config("spark.jars", r"C:\Users\yuvasree.r\Desktop\python test\mysql-connector-j-26.7.0\mysql-connector-j-26.7.0.jar") 
    .getOrCreate()
)
#  Quality Check 1 - NULL RATE
def check_null_rate(df, col, threshold):
    total_rows = df.count()
    null_count = df.filter(F.col(col).isNull()).count()
    if total_rows == 0:
        null_rate = 100
    else:
        null_rate = (null_count / total_rows) * 100
    passed = null_rate <= threshold
    return {
        "check_name": f"null_rate_{col}",
        "status": "PASS" if passed else "FAIL",
        "value_found": round(null_rate, 4),
        "threshold": threshold,
        "severity": "CRITICAL"
    }
#  Quality Check 2 - VALUE RANGE
def check_value_range(df, col, min_value, max_value=None):
    min_found = df.select(F.min(col)).first()[0]
    max_found = df.select(F.max(col)).first()[0]
    if max_value is None:
        passed = min_found is not None and min_found > min_value
        threshold = f"> {min_value}"
    else:
        passed = min_found is not None and min_found >= min_value and max_found <= max_value
        threshold = f"{min_value} - {max_value}"
    return {
        "check_name": f"value_range_{col}",
        "status": "PASS" if passed else "FAIL",
        "value_found": {
            "min": min_found,
            "max": max_found
        },
        "threshold": threshold,
        "severity": "CRITICAL"
    }

#  Quality Check 3 - ALLOWED VALUES
def check_allowed_values(df, col, allowed_set):
    invalid_count = df.filter(~F.col(col).isin(list(allowed_set))).count()
    passed = invalid_count == 0
    return {
        "check_name": f"allowed_values_{col}",
        "status": "PASS" if passed else "FAIL",
        "value_found": invalid_count,
        "threshold": list(allowed_set),
        "severity": "CRITICAL"
    }

#  Quality Check 4 - ROW COUNT
def check_row_count(df, expected_min):
    actual_count = df.count()
    passed = actual_count >= expected_min
    return {
        "check_name": "row_count",
        "status": "PASS" if passed else "FAIL",
        "value_found": actual_count,
        "threshold": expected_min,
        "severity": "CRITICAL"
    }
#  Quality Check 5 - DUPLICATES
def check_no_duplicates(df, key_col):
    total_count = df.count()
    unique_count = df.select(key_col).distinct().count()
    duplicate_count = total_count - unique_count
    passed = duplicate_count == 0
    return {
        "check_name": f"duplicates_{key_col}",
        "status": "PASS" if passed else "FAIL",
        "value_found": duplicate_count,
        "threshold": 0,
        "severity": "CRITICAL"
    }
# Quality Check 6 - CHURN DISTRIBUTION
def check_churn_distribution(df):
    total_count = df.count()
    churn_count = df.filter(F.col("churn") == 1).count()
    churn_rate = churn_count / total_count if total_count > 0 else 0
    churn_percentage = churn_rate * 100
    # Warning if churn is outside 5%-95%
    passed = 5 <= churn_percentage <= 95
    return {
        "check_name": "churn_distribution",
        "status": "PASS" if passed else "FAIL",
        "value_found": round(churn_percentage,2),
        "threshold": "5% - 95%",
        "severity": "WARNING"
    }

#  RUN ALL CHECKS
def run_quality_checks(df):
    results = []
    # NULL: monthly_charges
    results.append(check_null_rate(df, "monthly_charges", 0))
    # NULL: tenure
    results.append(check_null_rate(df, "tenure", 0))
    # tenure: 0-100
    results.append(check_value_range(df, "tenure", 0, 100))
    # monthly_charges > 0
    results.append(check_value_range(df, "monthly_charges", 0))
    # contract allowed values
    results.append(check_allowed_values(df, "contract", {"Month-to-month", "One year", "Two year"}))
    # at least 7000 rows
    results.append(check_row_count(df, 7000))
    # duplicate customer_i_d
    results.append(check_no_duplicates(df, "customer_i_d"))
    # churn distribution
    results.append(check_churn_distribution(df))
    return results
# 9. PRINT REPORT
def print_quality_report(results):
    print("\n======================================")
    print("DATA QUALITY REPORT")
    print("======================================")
    for result in results:
        print(f"{result['check_name']:35}{result['status']:7}{result['severity']}")
        print(f"  Value     : {result['value_found']}")
        print(f"  Threshold : {result['threshold']}")
# 10. SAVE JSON REPORT
def save_quality_report(results):
    os.makedirs("data/logs", exist_ok=True)
    report = {"run_timestamp": datetime.now().isoformat(), "checks": results}
    with open("data/logs/quality_report.json", "w") as file:
        json.dump(report, file, indent=4, default=str)
    print("\nReport saved to " "data/logs/quality_report.json")
# 11. HANDLE FAILURES
def handle_quality_results(results):
    critical_failures = [
        r for r in results
        if r["status"] == "FAIL"
        and r["severity"] == "CRITICAL"
    ]
    warnings = [
        r for r in results
        if r["status"] == "FAIL"
        and r["severity"] == "WARNING"
    ]
    for warning in warnings:
        print(f"WARNING: " f"{warning['check_name']} failed")
    # Critical failures
    if critical_failures:
        print("\nCRITICAL QUALITY FAILURE")
        for failure in critical_failures:
            print(f"FAIL: {failure['check_name']}")
        raise Exception(
            "Pipeline stopped because "
            "critical quality checks failed."
        )
    print("\nAll critical checks passed.")

# 12. MAIN
if __name__ == "__main__":

    # Read cleaned table
    df = (spark.read.format("jdbc")
        .option("url", "jdbc:mysql://localhost:3306/telecom_db_de")
        .option("dbtable", "cleaned_customers")
        .option("user", "root")
        .option("password", "root")
        .option("driver", "com.mysql.cj.jdbc.Driver")
        .load())

    print("\nCleaned customer data:")
    df.show(5)

    print("\nSchema:")
    df.printSchema()

    results = run_quality_checks(df)
    print_quality_report(results)
    save_quality_report(results)
    handle_quality_results(results)
    spark.stop()