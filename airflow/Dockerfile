FROM apache/airflow:2.10.4
RUN pip install apache-airflow==${AIRFLOW_VERSION}
# Copy file requirements.txt vào container
COPY requirements.txt .

# Cài đặt các thư viện từ requirements.txt
RUN pip install -r requirements.txt