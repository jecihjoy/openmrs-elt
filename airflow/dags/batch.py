from builtins import range
from datetime import timedelta

import airflow
from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['akendagor@ampath.or.ke'],
    'email_on_failure': True,
    'email_on_retry': True,
    'start_date': datetime.now(),
    'retries': 0,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    dag_id='batch_job',
    default_args=default_args,
    schedule_interval='0 0 * * *',
    dagrun_timeout=timedelta(minutes=60),
)

bash_command = """
                cd /usr/local/airflow/spark-jobs/ &&\
                python3 batch_job.py
               """

run_this = BashOperator(
    task_id='batch_job',
    bash_command=bash_command,
    dag=dag,
)


if __name__ == "__main__":
    dag.cli()
