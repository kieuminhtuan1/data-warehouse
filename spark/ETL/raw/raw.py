from pyspark.sql import SparkSession

# Khởi tạo Spark session
spark = SparkSession.builder.appName("Raw Layer").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
# Đọc dữ liệu
df_top_cv = spark.read.csv(
    '/opt/spark/data/extracted_jobs_1-50.csv', header=True, inferSchema=True)
df_top_cv.show(5)
