from datetime import datetime, timedelta
from airflow.sdk import dag, task
from airflow.operators.bash import BashOperator
# YAHAN TRIGGER OPERATOR IMPORT ADD KIYA HAI:
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DBT_PROJECT_PATH = os.path.abspath(
    os.path.join(CURRENT_DIR, "../dbt_transforms/fuel_pipeline_dbt")
)

from scripts.s3_api_retriever import fetch_latest_session_from_s3
from scripts.fetch_updated_only import fetch_updated_data

@dag(
    dag_id="nsw_fuel_incremental_every_minute",
    schedule="* * * * *",  # Runs every 1 minute
    start_date=datetime(2026, 1, 1),
    catchup=False,
    dagrun_timeout=timedelta(minutes=2),
)
def nsw_fuel_incremental():

    @task
    def fetch_stations_task():
        return fetch_latest_session_from_s3()

    @task
    def fetch_all_prices(session_keys):
        return fetch_updated_data(session_keys)

    run_updated_dbt = BashOperator(
        task_id="run_updated_dbt_transforms",
        bash_command=(
            f"cd '{DBT_PROJECT_PATH}' && "
            "dbt run --select "
            "bronze_updated_prices_data_all "
            "bronze_updated_stations_data_all "
            "silver_updated_prices_data_all "
            "silver_updated_stations_data_all "
            "silver_updated_combined "
            "gold_historic_data "
        ),
    )

    stations_data = fetch_stations_task()
    fetch_all_prices_task = fetch_all_prices(stations_data)

    # Sirf data pipeline chalegi, bar bar Power BI DAG trigger nahi hoga
    fetch_all_prices_task >> run_updated_dbt

nsw_fuel_incremental()