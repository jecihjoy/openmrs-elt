import os
import sys
from builtins import range
from datetime import timedelta

import airflow
from airflow.models import DAG
from datetime import datetime

# Import the operator
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from airflow.operators.bash_operator import BashOperator

# Set the path for our files.
entry_point = os.path.join(os.environ["AIRFLOW_HOME"], "spark-jobs", "batch_job.py")

default_args = {
    'owner': 'airflow',
    'description' : 'OpenMRS ETL',
    'depends_on_past': False,
    'email': ['akendagor@ampath.or.ke'],
    'email_on_failure': False,
    'email_on_retry': False,
    'start_date': datetime.now() - timedelta(minutes=20),
    'retries': 5,
    'retry_delay': timedelta(minutes=1),
    'dagrun_timeout':timedelta(minutes=5)
    
}


with DAG('batch_pipeline', schedule_interval='@daily', default_args=default_args, catchup=False ) as dag:
  	# Define task clean, running a cleaning job.

    t1 = BashOperator(
                task_id='print_current_date',
                bash_command='date'
        )

    t2 = BashOperator(
                task_id='print_job_started',
                bash_command='echo "******* *** *** Spark Batch Job Has Started ********************"'
        )

    flat_obs = SparkSubmitOperator(
        application=entry_point, 
        verbose=True,
        task_id='flat_obs',
        conn_id='spark_default')

    t3 = BashOperator(
                task_id='print_hello',
                bash_command='echo "hello world"'
        )

    t1 >> t2  >> flat_obs >> t3