from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import pandas as pd
from sklearn.model_selection import train_test_split

def load_and_clean_data():
    df = pd.read_csv('data/raw/winequality-red.csv')
    df.dropna(inplace=True)
    X = df.drop(columns=['quality'])
    y = df['quality']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    X_train.to_csv('data/processed/X_train.csv', index=False)
    X_test.to_csv('data/processed/X_test.csv', index=False)
    y_train.to_csv('data/processed/y_train.csv', index=False)
    y_test.to_csv('data/processed/y_test.csv', index=False)

dag = DAG(
    'data_pipeline',
    description='Wine Quality Data Pipeline',
    schedule_interval='*/5 * * * *',
    start_date=datetime(2025, 9, 21),
    catchup=False
)

data_task = PythonOperator(
    task_id='data_cleaning_task',
    python_callable=load_and_clean_data,
    dag=dag
)
