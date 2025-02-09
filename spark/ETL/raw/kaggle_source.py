from pyspark.sql import SparkSession

# Khởi tạo Spark session
spark = SparkSession.builder.appName("Raw Layer").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

df_kaggle = spark.read.option("header", True) \
    .csv("/opt/spark/data/JOB_DATA.csv")

df_kaggle.write.parquet(
    '/opt/spark/data/raw/vietnamese-job-posting.parquet', mode='overwrite')
