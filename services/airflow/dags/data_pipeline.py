from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal
from pathlib import Path
from sklearn.model_selection import train_test_split

def load_and_clean_data():
    df = pd.read_csv('data/raw/winequality-red.csv')
    df.dropna(inplace=True)

    numeric_columns = df.select_dtypes(include='number').columns.tolist()
    feature_columns = [column for column in numeric_columns if column != 'quality']

    if feature_columns:
        q1 = df[feature_columns].quantile(0.25)
        q3 = df[feature_columns].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        within_bounds = ~((df[feature_columns] < lower_bound) | (df[feature_columns] > upper_bound)).any(axis=1)
        df = df.loc[within_bounds].reset_index(drop=True)
    else:
        df = df.reset_index(drop=True)

    X = df.drop(columns=['quality'])
    y = df['quality']
    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    # X_train.to_csv('data/processed/X_train.csv', index=False)
    # X_test.to_csv('data/processed/X_test.csv', index=False)
    # y_train.to_csv('data/processed/y_train.csv', index=False)
    # y_test.to_csv('data/processed/y_test.csv', index=False)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42
    )

    X_train = X_train.reset_index(drop=True)
    X_test = X_test.reset_index(drop=True)
    y_train = y_train.reset_index(drop=True)
    y_test = y_test.reset_index(drop=True)

    processed_dir = Path('data/processed')
    processed_dir.mkdir(parents=True, exist_ok=True)

    X_train_path = processed_dir / 'X_train.csv'
    X_test_path = processed_dir / 'X_test.csv'
    y_train_path = processed_dir / 'y_train.csv'
    y_test_path = processed_dir / 'y_test.csv'

    X_train.to_csv(X_train_path, index=False)
    X_test.to_csv(X_test_path, index=False)
    y_train.to_csv(y_train_path, index=False)
    y_test.to_csv(y_test_path, index=False)

    saved_X_train = pd.read_csv(X_train_path)
    saved_X_test = pd.read_csv(X_test_path)
    saved_y_train = pd.read_csv(y_train_path).squeeze('columns')
    saved_y_test = pd.read_csv(y_test_path).squeeze('columns')

    assert_frame_equal(saved_X_train, X_train)
    assert_frame_equal(saved_X_test, X_test)
    assert_series_equal(saved_y_train, y_train)
    assert_series_equal(saved_y_test, y_test)


dag = DAG(
    'data_pipeline',
    description='Wine Quality Data Pipeline',
    schedule_interval='*/5 * * * *',
    start_date=days_ago(1),
    catchup=False
)

data_task = PythonOperator(
    task_id='data_cleaning_task',
    python_callable=load_and_clean_data,
    dag=dag
)
