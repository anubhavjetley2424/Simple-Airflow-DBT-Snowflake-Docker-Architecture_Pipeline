FROM apache/airflow:2.9.1-python3.9
WORKDIR /opt/airflow

# Install system and build dependencies as root
USER root
RUN apt-get update && apt-get install -y \
    libssl-dev \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Change ownership of /tmp to airflow user
RUN chown -R airflow /tmp

# Switch to airflow user for pip commands
USER airflow
ENV PIP_USER=false

RUN pip install --upgrade pip setuptools
RUN pip install psycopg2-binary
COPY airflow/requirements.txt .
COPY airflow/dags /opt/airflow/dags
COPY dbt/weather /opt/airflow/dbt/weather
RUN pip install --no-cache-dir -r requirements.txt

# Create data and model directories
RUN mkdir -p /opt/airflow/data/raw /opt/airflow/data/processed /opt/airflow/data/models