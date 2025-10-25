from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime
import subprocess

def run_forecast():
    subprocess.run(["python3", "/workspaces/Global-Market-Project/forecasting/model_forecast.py"], check=True)

def update_dashboard():
    subprocess.run(["python3", "/workspaces/Global-Market-Project/dash/update_dashboard.py"], check=True)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'retries': 1
}

with DAG(
    dag_id='global_market_index_pipeline',
    default_args=default_args,
    description='End-to-end pipeline for Global Market Index Analytics',
    schedule='@daily',
    catchup=False,
    tags=['market', 'dbt', 'forecast', 'analytics']
) as dag:

    ingest_data = BashOperator(
        task_id='ingest_data',
        bash_command='python3 /workspaces/Global-Market-Project/sql/load_data.py'
    )

    run_dbt = BashOperator(
    task_id='run_dbt',
    bash_command='''
        source /home/codespace/dbt_env/bin/activate
        cd /workspaces/Global-Market-Project/dbt
        dbt run --profiles-dir .
    ''',
)

    dbt_test = BashOperator(
    task_id='dbt_test',
    bash_command='''
        source /home/codespace/dbt_env/bin/activate
        cd /workspaces/Global-Market-Project/dbt
        dbt test --profiles-dir .
    '''
)

    forecast = PythonOperator(
        task_id='forecast',
        python_callable=run_forecast
    )

    refresh_dashboard = PythonOperator(
        task_id='refresh_dashboard',
        python_callable=update_dashboard
    )

    
    ingest_data >> run_dbt >> dbt_test >> forecast >> refresh_dashboard