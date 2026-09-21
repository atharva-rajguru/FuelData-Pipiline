from datetime import datetime
from airflow.sdk import dag, task
from airflow.operators.bash import BashOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from scripts.all_data_retriever import fetch_all_stations
from scripts.s3_api_retriever import fetch_latest_session_from_s3
from scripts.get_token import main_outh

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DBT_PROJECT_PATH = os.path.abspath(
    os.path.join(CURRENT_DIR, "../dbt_transforms/fuel_pipeline_dbt")
)

@dag(
    dag_id="nsw_fuel_baseline_dag",
    schedule=None,  # Runs only when you manually trigger it once
    start_date=datetime(2026, 1, 1),
    catchup=False,
)
def nsw_fuel_baseline():

    @task
    def get_token_task():
        return main_outh()

    @task
    def fetch_stations_task():
        return fetch_latest_session_from_s3()

    @task
    def fetch_all_prices(session_keys):
        return fetch_all_stations(session_keys)

    run_static_dbt = BashOperator(
        task_id="run_static_dbt_transforms",
        bash_command=(
            f"cd '{DBT_PROJECT_PATH}' && "
            "dbt run --select "
            "bronze_static_prices_data_all "
            "bronze_static_stations_data_all "
            "silver_static_prices_data_all "
            "silver_static_stations_data_all "
            "silver_static_combined "
        ),
    )


    # --- Define tasks ---
    token_data = get_token_task()
    stations_data = fetch_stations_task()
    fetch_all_prices_task = fetch_all_prices(stations_data)

    # --- NEW: Automatically trigger DAG 2 once the baseline finishes ---
    trigger_second_dag = TriggerDagRunOperator(
        task_id="trigger_incremental_pipeline",
        trigger_dag_id="nsw_fuel_incremental_every_minute", # Must match DAG 2's dag_id exactly
    )

    # --- Wire up dependencies ---
    token_data >> stations_data >> fetch_all_prices_task >> run_static_dbt >> trigger_second_dag


nsw_fuel_baseline()