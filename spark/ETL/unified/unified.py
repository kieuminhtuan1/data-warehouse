from pyspark.sql import SparkSession
import pyspark.sql.functions as F
import uuid

# Khởi tạo Spark session
spark = SparkSession.builder \
    .appName("Unified Layer") \
    .config("spark.jars", "/opt/spark/jars/mysql-connector-java-8.0.26.jar") \
    .getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
spark.conf.set("spark.sql.legacy.timeParserPolicy", "LEGACY")

df = spark.read.parquet(
    "/opt/spark/data/trusted/trusted.parquet")

# Thông tin MySQL
mysql_url = "jdbc:mysql://mysql:3306/dwh"

mysql_properties = {
    "user": "mysql",
    "password": "mysql",
    "driver": "com.mysql.cj.jdbc.Driver"
}

df_dim_company = df.select(
    "company_name", "company_overview", "company_scale", "company_field"
).distinct()
df_dim_company = df_dim_company.withColumn(
    "company_id", F.udf(lambda: str(uuid.uuid4()))()
)

df_dim_industry = df.select("industry").distinct()
df_dim_industry = df_dim_industry.withColumn(
    "industry_id", F.udf(lambda: str(uuid.uuid4()))()
)

df_dim_job_type = df.select("job_type").distinct()
df_dim_job_type = df_dim_job_type.withColumn(
    "job_type_id", F.udf(lambda: str(uuid.uuid4()))()
)

df_dim_working_location = df.select(
    "working_location", "job_city", "company_address").distinct()
df_dim_working_location = df_dim_working_location.withColumn(
    "working_location_id", F.udf(lambda: str(uuid.uuid4()))()
)

df_dim_working_time = df.select("working_time").distinct()
df_dim_working_time = df_dim_working_time.withColumn(
    "working_time_id", F.udf(lambda: str(uuid.uuid4()))()
)
df.printSchema()
df_dim_working_location.printSchema()
df_dim_working_time.printSchema()
exit()
df_fact_job_postings = df \
    .join(df_dim_company, ["company_name"], "left") \
    .join(df_dim_industry, ["industry"], "left") \
    .join(df_dim_working_location, ["working_location"], "left") \
    .join(df_dim_working_time, ["working_time"], "left") \
    .join(df_dim_job_type, ["job_type"], "left") \
    .select(
        "job_id", "url_job", "job_title", "company_id", "industry_id",
        "working_location_id", "working_time_id", "job_type_id",
        "salary", "number_candidate", "year_of_experience", "due_date"
    ) \
    .dropDuplicates()

df_dim_company.write.jdbc(
    url=mysql_url, table="dim_company", mode="overwrite", properties=mysql_properties)

df_dim_industry.write.jdbc(
    url=mysql_url, table="dim_industry", mode="overwrite", properties=mysql_properties)

df_dim_job_type.write.jdbc(
    url=mysql_url, table="dim_job_type", mode="overwrite", properties=mysql_properties)

df_dim_working_location.write.jdbc(
    url=mysql_url, table="dim_working_location", mode="overwrite", properties=mysql_properties)

df_dim_working_time.write.jdbc(
    url=mysql_url, table="dim_working_time", mode="overwrite", properties=mysql_properties)

df_fact_job_postings.write.jdbc(
    url=mysql_url, table="fact_job_postings", mode="overwrite", properties=mysql_properties)
