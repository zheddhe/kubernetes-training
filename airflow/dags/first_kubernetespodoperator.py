from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator

with DAG(
    dag_id='first_kubernetespodoperator',
    description='My first DAG with KubernetesPodOperator',
    tags=['datascientest'],
    schedule_interval=None,
    default_args={
        'owner': 'airflow',
        'start_date': days_ago(2),
    }
) as my_dag:

    hello_world_task = KubernetesPodOperator(
        task_id="hello_world",
        image="hello-world"
    )

    hello_world_task  # type: ignore
