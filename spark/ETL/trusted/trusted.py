from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, udf, array, split, to_json
from pyspark.sql.types import StringType, ArrayType, DateType
import uuid

# Khởi tạo Spark session
spark = SparkSession.builder \
    .appName("Trusted Layer") \
    .getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
spark.conf.set("spark.sql.legacy.timeParserPolicy", "LEGACY")

df1 = spark.read.parquet(
    "/opt/spark/data/foundation/vietnamese-job-posting_clean.parquet")
df2 = spark.read.parquet(
    "/opt/spark/data/foundation/extracted_jobs_1-50_clean.parquet")

df1 = df1.withColumn("company_field", lit(None)) \
    .withColumn("working_location", lit(None)) \
    .withColumn("working_time", lit(None)) \
    .withColumn("application_method", lit(None))


df2 = df2.withColumn("company_overview", lit(None)) \
         .withColumn("job_type", lit(None)) \
         .withColumn("gender", lit(None)) \
         .withColumn("number_candidate", lit(None)) \
         .withColumn("career_level", lit(None)) \
         .withColumn("industry", lit(None)) \
         .withColumnRenamed("url", "url_job")

df_combined = df1.unionByName(df2, allowMissingColumns=True)

df_combined.write.parquet(
    '/opt/spark/data/trusted/trusted.parquet', mode='overwrite')
