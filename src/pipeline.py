from minio import Minio
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType


client = Minio(
    "127.0.0.1:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

minio_bucket = "my-first-bucket"

found = client.bucket_exists(minio_bucket)
if not found:
    client.make_bucket(minio_bucket)

destination_file = 'data.csv'
source_file = './data/data.csv' ## The file should exist in the project folder

client.fput_object(minio_bucket, destination_file, source_file,)

# Create the SparkSession builder for Iceberg with Minio configuration
iceberg_builder = SparkSession.builder \
    .appName("iceberg-concurrent-write-isolation-test") \
    .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.0,org.apache.iceberg:iceberg-hive-runtime:1.5.0") \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.spark_catalog.type", "hadoop") \
    .config("spark.sql.catalog.spark_catalog.warehouse", f"s3a://{minio_bucket}/iceberg_data/") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .enableHiveSupport()

# Build the SparkSession for Iceberg
iceberg_spark = iceberg_builder.getOrCreate()

df = iceberg_spark.read.format('csv').option('header', 'true').option('inferSchema', 'true').load(source_file)

# Iceberg table location in Minio
iceberg_table_location = f"s3a://{minio_bucket}/iceberg_data/default"

# Write DataFrame to Iceberg table in Minio
df.write \
    .format("iceberg") \
    .mode("append") \
    .saveAsTable("iceberg_table_name")  # Name of the Iceberg table

# Read data from the Iceberg table
iceberg_df = iceberg_spark.read.format("iceberg").load(f"{iceberg_table_location}/iceberg_table_name")

# Show the dataframe schema and some sample data
iceberg_df.printSchema()
iceberg_df.show()

# delta_table_location = f"s3a://{minio_bucket}/delta_data/"
# iceberg_df.write.format("delta").mode("overwrite").save(delta_table_location)