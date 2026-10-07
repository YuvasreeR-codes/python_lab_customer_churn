from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    DoubleType
)
from pyspark.sql import functions as F

import os
os.environ["HADOOP_HOME"] = r"C:\Users\yuvasree.r\Desktop\python test\hadoop"
os.environ["PATH"] = os.environ["PATH"] + r";C:\Users\yuvasree.r\Desktop\python test\hadoop\bin"

spark = (
    SparkSession.builder
    .appName("CustomerChurnDE5")
    .master("local[2]")
    .config("spark.driver.memory", "4g")
    .getOrCreate()
)

schema = StructType([

    StructField("customerID", StringType(), True),
    StructField("gender", StringType(), True),
    StructField("SeniorCitizen", IntegerType(), True),
    StructField("Partner", StringType(), True),
    StructField("Dependents", StringType(), True),
    StructField("tenure", IntegerType(), True),
    StructField("PhoneService", StringType(), True),
    StructField("MultipleLines", StringType(), True),
    StructField("InternetService", StringType(), True),
    StructField("OnlineSecurity", StringType(), True),
    StructField("OnlineBackup", StringType(), True),
    StructField("DeviceProtection", StringType(), True),
    StructField("TechSupport", StringType(), True),
    StructField("StreamingTV", StringType(), True),
    StructField("StreamingMovies", StringType(), True),
    StructField("Contract", StringType(), True),
    StructField("PaperlessBilling", StringType(), True),
    StructField("PaymentMethod", StringType(), True),
    StructField("MonthlyCharges", DoubleType(), True),
    StructField("TotalCharges", StringType(), True),
    StructField("Churn", StringType(), True)
])

df = (
    spark.read
    .option("header", True)
    .schema(schema)
    .csv("customer_churn.csv")
)

print("\n========== ORIGINAL SPARK SCHEMA ==========")
df.printSchema()
print("\n========== SAMPLE DATA ==========")
df.show(5, truncate=False)

df = df.withColumn(
    "TotalCharges",
    F.regexp_replace(
        F.col("TotalCharges"),
        r"^\s*$",
        ""
    )
)
df = df.withColumn(
    "TotalCharges",
    F.when(
        F.col("TotalCharges") == "",
        None
    ).otherwise(
        F.col("TotalCharges")
    )
)
df = df.withColumn(
    "TotalCharges",
    F.col("TotalCharges").cast(DoubleType())
)


df = df.withColumn(
    "churn_encoded",
    F.when(
        F.col("Churn") == "Yes",
        1
    ).otherwise(0)
)

print("\n========== CLEANED SPARK SCHEMA ==========")
df.printSchema()

contract_summary = (
    df.groupBy("Contract")
    .agg(
        F.count("*").alias("customer_count"),
        F.avg("churn_encoded").alias("churn_rate")
    )
    .orderBy("Contract")
)
print("\n========== CHURN BY CONTRACT ==========")
contract_summary.show(truncate=False)

internet_summary = (
    df.groupBy("InternetService")
    .agg(
        F.avg("MonthlyCharges").alias("avg_monthly_charges"),
        F.avg("churn_encoded").alias("churn_rate")
    )
    .orderBy("InternetService")
)
print("\n========== INTERNET SERVICE SUMMARY ==========")
internet_summary.show(truncate=False)


contract_summary_display = contract_summary.withColumn(
    "churn_rate_percent",
    F.col("churn_rate") * 100
)
print("\n========== CONTRACT CHURN RATE (%) ==========")
contract_summary_display.show(truncate=False)


internet_summary_display = internet_summary.withColumn(
    "churn_rate_percent",
    F.col("churn_rate") * 100
)
print("\n========== INTERNET SERVICE CHURN RATE (%) ==========")
internet_summary_display.show(truncate=False)


output_path = "data/spark_output/contract_summary"

(
    contract_summary
    .write
    .mode("overwrite")
    .partitionBy("Contract")
    .parquet(output_path)
)

print(f"\nParquet written to: {output_path}")

parquet_df = spark.read.parquet(output_path)
print("\n========== PARQUET SCHEMA ==========")
parquet_df.printSchema()

print("\n========== PARQUET DATA ==========")
parquet_df.show(truncate=False)

# Round-trip validation

original_count = contract_summary.count()
parquet_count = parquet_df.count()

print("\n========== ROUND-TRIP VALIDATION ==========")

print(f"Original summary rows : {original_count}")
print(f"Parquet summary rows  : {parquet_count}")

assert original_count == parquet_count
print("PASS - Parquet row count matches")

spark.stop()