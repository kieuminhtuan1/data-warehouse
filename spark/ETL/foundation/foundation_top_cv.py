from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql.functions import from_json, col, to_date, explode, when, regexp_replace, trim, lit, udf
from pyspark.sql.types import StructType, StructField, StringType, ArrayType
import uuid

# Khởi tạo Spark session
spark = SparkSession.builder.appName("Foundation Layer").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
spark.conf.set("spark.sql.legacy.timeParserPolicy", "LEGACY")

df_parquet_top_cv = spark.read.parquet(
    '/opt/spark/data/raw/extracted_jobs_1-50.parquet'
)

df_clean_top_cv = df_parquet_top_cv.filter(
    df_parquet_top_cv['job_title'].isNotNull()
)


def generate_uuid():
    return str(uuid.uuid4())


uuid_udf = udf(generate_uuid, StringType())

# Thay thế cột job_id bằng UUID
df_clean_top_cv = df_clean_top_cv.withColumn("job_id", uuid_udf())

json_schema = ArrayType(StructType([
    StructField("title", StringType(), True),
    StructField("content", StringType(), True)
]))

df_clean_top_cv = df_clean_top_cv.select(
    [trim(regexp_replace(regexp_replace(col(c), "[\n\r\t]+", " "),
          "\s+", " ")).alias(c) for c in df_clean_top_cv.columns]
)


# Kiểm tra và xử lý nếu cột job_description tồn tại
if "job_description" in df_clean_top_cv.columns:
    # Parse JSON từ cột job_description
    df_clean_top_cv = df_clean_top_cv.withColumn(
        "job_description_parsed",
        from_json(col("job_description"), json_schema)
    )

    # Dùng explode để tách các phần tử trong mảng JSON thành các dòng
    df_clean_top_cv = df_clean_top_cv.withColumn(
        "job_description_exploded",
        explode(col("job_description_parsed"))
    )

    # Tạo các cột mới dựa trên điều kiện title trong job_description_exploded
    df_clean_top_cv = df_clean_top_cv.withColumn(
        "job_responsibilities",
        F.when(col("job_description_exploded.title") == "Mô tả công việc",
               col("job_description_exploded.content")).otherwise(F.lit(None))
    )
    df_clean_top_cv = df_clean_top_cv.withColumn(
        "requirements",
        F.when(col("job_description_exploded.title") == "Yêu cầu ứng viên",
               col("job_description_exploded.content")).otherwise(F.lit(None))
    )
    df_clean_top_cv = df_clean_top_cv.withColumn(
        "benefits",
        F.when(col("job_description_exploded.title") == "Quyền lợi",
               col("job_description_exploded.content")).otherwise(F.lit(None))
    )
    df_clean_top_cv = df_clean_top_cv.withColumn(
        "working_location",
        F.when(col("job_description_exploded.title") == "Địa điểm làm việc",
               col("job_description_exploded.content")).otherwise(F.lit(None))
    )
    df_clean_top_cv = df_clean_top_cv.withColumn(
        "working_time",
        F.when(col("job_description_exploded.title") == "Thời gian làm việc",
               col("job_description_exploded.content")).otherwise(F.lit(None))
    )
    df_clean_top_cv = df_clean_top_cv.withColumn(
        "application_method",
        F.when(col("job_description_exploded.title") == "Cách thức ứng tuyển",
               col("job_description_exploded.content")).otherwise(F.lit(None))
    )

    # Định nghĩa window spec
    window_spec = Window.partitionBy("job_id")

    # Dùng `first()` để lấy giá trị đầu tiên không phải null trong mỗi nhóm và tránh trùng lặp
    df_clean_top_cv = df_clean_top_cv.withColumn(
        "job_responsibilities",
        F.first("job_responsibilities", True).over(window_spec)
    )
    df_clean_top_cv = df_clean_top_cv.withColumn(
        "requirements",
        F.first("requirements", True).over(window_spec)
    )
    df_clean_top_cv = df_clean_top_cv.withColumn(
        "benefits",
        F.first("benefits", True).over(window_spec)
    )
    df_clean_top_cv = df_clean_top_cv.withColumn(
        "working_location",
        F.first("working_location", True).over(window_spec)
    )
    df_clean_top_cv = df_clean_top_cv.withColumn(
        "working_time",
        F.first("working_time", True).over(window_spec)
    )
    df_clean_top_cv = df_clean_top_cv.withColumn(
        "application_method",
        F.first("application_method", True).over(window_spec)
    )

    # Loại bỏ các dòng trùng lặp
    df_clean_top_cv = df_clean_top_cv.dropDuplicates(subset=["job_id"])

    # Xóa các cột không cần thiết
    df_clean_top_cv = df_clean_top_cv.drop(
        "job_description", "job_description_parsed", "job_description_exploded"
    )

if "due_date" in df_clean_top_cv.columns:
    df_clean_top_cv = df_clean_top_cv.withColumn(
        "due_date", to_date(col("due_date"), "dd/MM/yyyy")
    )
df_clean_top_cv = df_clean_top_cv.withColumn(
    "due_date",
    F.when(F.col("due_date").isNull(), "Hết Hạn").otherwise(F.col("due_date"))
)
df_clean_top_cv.show(1, truncate=False)
exit()
df_clean_top_cv.coalesce(1).write.mode("overwrite").parquet(
    '/opt/spark/data/foundation/extracted_jobs_1-50_clean.parquet'
)
