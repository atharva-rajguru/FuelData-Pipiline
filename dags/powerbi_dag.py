from datetime import datetime, timedelta
from airflow.sdk import dag, task
from airflow.operators.bash import BashOperator
import sys
import os
import pendulum
local_tz = pendulum.timezone("Australia/Sydney")

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DBT_PROJECT_PATH = os.path.abspath(
    os.path.join(CURRENT_DIR, "../dbt_transforms/fuel_pipeline_dbt")
)

@dag(
    dag_id="powerbi_dag",
    schedule="58 23 * * *",
    start_date=pendulum.datetime(2026, 1, 1, tz=local_tz),
    catchup=False,
    dagrun_timeout=timedelta(minutes=5),
)
def powerbi_dag():
    run_dbt_gold = BashOperator(
        task_id="run_powerbi_dbt_transforms",
        bash_command=(
            f"cd '{DBT_PROJECT_PATH}' && "
            "dbt run --select "
            "gold_daily_status "
            "gold_station_summary "
            "gold_weekwise_status "
            "gold_stations_data "
        ),
    )

    run_dbt_gold

powerbi_dag()
