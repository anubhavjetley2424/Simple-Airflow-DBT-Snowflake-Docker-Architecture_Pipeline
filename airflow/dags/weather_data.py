from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import os
import snowflake.connector
import json
from airflow.operators.bash import BashOperator

API_KEY = os.getenv("WEATHER_API_KEY")
CITY = "London"

def fetch_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    with open("/tmp/weather.json", "w") as f:
        json.dump(data, f)

def load_to_snowflake():
    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )
    cursor = conn.cursor()
    cursor.execute("CREATE OR REPLACE TABLE raw_weather (data VARIANT)")
    with open("/tmp/weather.json") as f:
        weather = json.load(f)
    cursor.execute("INSERT INTO raw_weather SELECT PARSE_JSON(%s)", (json.dumps(weather),))

default_args = {
    'start_date': datetime(2023, 1, 1),
}

with DAG('weather_pipeline', schedule_interval='@daily', default_args=default_args, catchup=False) as dag:
    fetch_task = PythonOperator(task_id='fetch_weather', python_callable=fetch_weather)
    load_task = PythonOperator(task_id='load_to_snowflake', python_callable=load_to_snowflake)

    fetch_task >> load_task


dbt_task = BashOperator(
    task_id='run_dbt',
    bash_command='cd /opt/airflow/dbt/weather && dbt run',
)

load_task >> dbt_task
