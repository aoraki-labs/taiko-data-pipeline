import datetime
import pendulum

from airflow.decorators import dag, task

args = {
    'owner': 'airflow',
    'email': ['nju.jianghao@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': True,
    'depends_on_past': False,
}

@dag(
    dag_id="taiko-fetch-l2-data",
    schedule_interval="*/1 * * * *",
    start_date=pendulum.datetime(2023, 5, 26, tz="UTC"),
    max_active_runs=1,
    catchup=False,
    dagrun_timeout=datetime.timedelta(minutes=60),
    tags=["taiko"],
    default_args=args,
)
def job():
    """
    ### Taiko Fetch L2 Data
    
    - max_active_runs=1 plus catchup=False will skip next schedule of DAG if 
      previous run not yet finished by the time of next schedule.
    """

    @task()
    def taiko_fetch_l2():
        import sys
        import os
        sys.path.append(os.path.abspath(os.environ["AIRFLOW_HOME"]))
        from taiko_l2.task_manager import TaskManager
            
        task_manager = TaskManager()
        task_manager.run()
    

    taiko_fetch_l2()


job()
