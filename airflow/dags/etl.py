from airflow import DAG
from airflow.operators.bash_operator import BashOperator
import datetime as dt

raw_kaggle_source = 'docker exec spark-master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --conf spark.executor.memory=2g \
  --verbose \
  /opt/spark/ETL/raw/kaggle_source.py'

raw_top_cv_source = 'docker exec spark-master /opt/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    --conf spark.executor.memory=2g \
    --verbose \
    /opt/spark/ETL/raw/top_cv_source.py'

foundation_kaggle = 'docker exec spark-master /opt/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    --conf spark.executor.memory=2g \
    --verbose \
    /opt/spark/ETL/foundation/foundation_kaggle.py'

foundation_top_cv = 'docker exec spark-master /opt/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    --conf spark.executor.memory=2g \
    --verbose \
    /opt/spark/ETL/foundation/foundation_top_cv.py'

trusted = 'docker exec spark-master /opt/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    --conf spark.executor.memory=2g \
    --verbose \
    /opt/spark/ETL/trusted/trusted.py'

unified = 'docker exec spark-master /opt/spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    --conf spark.executor.memory=2g \
    --verbose \
    /opt/spark/ETL/unified/unified.py'

default_args = {
    'owner': 'etl',
    'start_date': dt.datetime.now(),
    'retries': 3,
    'retry_delay': dt.timedelta(minutes=5),
}

with DAG('etl', default_args=default_args, schedule_interval='@daily') as dag:
    raw_kaggle_source_task = BashOperator(
        task_id='raw_kaggle_source', bash_command=raw_kaggle_source)

    raw_top_cv_source_task = BashOperator(
        task_id='raw_top_cv_source', bash_command=raw_top_cv_source)

    foundation_kaggle_task = BashOperator(
        task_id='foundation_kaggle', bash_command=foundation_kaggle)

    foundation_top_cv_task = BashOperator(
        task_id='foundation_top_cv', bash_command=foundation_top_cv)

    trusted_task = BashOperator(
        task_id='trusted', bash_command=trusted)

    unified_task = BashOperator(
        task_id='unified', bash_command=unified)

    raw_kaggle_source_task >> foundation_kaggle_task
    raw_top_cv_source_task >> foundation_top_cv_task
    [foundation_kaggle_task, foundation_top_cv_task] >> trusted_task
    trusted_task >> unified_task
