from pyspark.sql import SparkSession

# Khởi tạo Spark session
spark = SparkSession.builder.appName("Raw Layer").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
# Đọc dữ liệu
df_top_cv = spark.read.option("header", True).option("multiLine", True).option(
    "quote", '"').csv("/opt/spark/data/extracted_jobs_1-50.csv")
df_top_cv.show(5, truncate=False)
exit()
df_top_cv.write.parquet(
    '/opt/spark/data/raw/extracted_jobs_1-50.parquet', mode='overwrite')
