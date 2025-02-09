from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import regexp_replace, to_date, col, split, udf
from pyspark.sql.types import StringType
import uuid

# Khởi tạo Spark session
spark = SparkSession.builder.appName("Foundation Layer").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
spark.conf.set("spark.sql.legacy.timeParserPolicy", "LEGACY")

df_parquet_kaggle = spark.read.parquet(
    '/opt/spark/data/raw/vietnamese-job-posting.parquet'
)

df_clean_kaggle = df_parquet_kaggle.filter(
    (df_parquet_kaggle['Job Title'].isNotNull())
)


def generate_uuid():
    return str(uuid.uuid4())


uuid_udf = udf(generate_uuid, StringType())

df_clean_kaggle = df_clean_kaggle.withColumn("JobID", uuid_udf())

df_clean_kaggle = (
    df_clean_kaggle
    .withColumnRenamed("JobID", "job_id")
    .withColumnRenamed("URL Job", "url_job")
    .withColumnRenamed("Job Title", "job_title")
    .withColumnRenamed("Name Company", "company_name")
    .withColumnRenamed("Company Overview", "company_overview")
    .withColumnRenamed("Company Size", "company_scale")
    .withColumnRenamed("Company Address", "company_address")
    .withColumnRenamed("Job Description", "job_responsibilities")
    .withColumnRenamed("Job Requirements", "requirements")
    .withColumnRenamed("Benefits", "benefits")
    .withColumnRenamed("Job Address", "job_city")
    .withColumnRenamed("Job Type", "job_type")
    .withColumnRenamed("Gender", "gender")
    .withColumnRenamed("Number Cadidate", "number_candidate")
    .withColumnRenamed("Career Level", "career_level")
    .withColumnRenamed("Years of Experience", "year_of_experience")
    .withColumnRenamed("Salary", "salary")
    .withColumnRenamed("Submission Deadline", "due_date")
    .withColumnRenamed("Industry", "industry")
)

df_clean_kaggle.coalesce(1).write.mode("overwrite").parquet(
    '/opt/spark/data/foundation/vietnamese-job-posting_clean.parquet'
)
