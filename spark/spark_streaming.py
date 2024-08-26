from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StructType, StructField, IntegerType, FloatType, StringType, LongType

# Initialize Spark session
spark = SparkSession.builder.appName(
    "TransactionProcessor").master("local[*]").getOrCreate()

# Define schema for transactions
schema = StructType([
    StructField("user_id", IntegerType(), True),
    StructField("transaction_amount", FloatType(), True),
    StructField("card", StringType(), True),
    StructField("timestamp", LongType(), True),
    StructField("merchant_id", IntegerType(), True)
])

# HDFS URL
hdfs_url = "hdfs://172.20.0.2:8020/transactions"

# Read streaming data from HDFS directory
transaction_df = spark.readStream.schema(schema).json(hdfs_url)

# Perform some transformation (example: calculate total transaction amount per merchant)
processed_df = transaction_df.groupBy("merchant_id").agg(
    sum("transaction_amount").alias("total_transaction_amount"),
    count("*").alias("transaction_count")
)

# Write the processed data to the console
query = processed_df.writeStream.outputMode(
    "complete").format("console").start()

query.awaitTermination()
