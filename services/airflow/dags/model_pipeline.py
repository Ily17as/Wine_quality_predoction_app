"""Airflow DAG to train and evaluate the wine quality model."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

import joblib
import pandas as pd
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


BASE_DIR = Path(__file__).resolve().parents[3]
PROCESSED_DIR = BASE_DIR / "data" / "processed"
MODEL_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"
MODEL_PATH = MODEL_DIR / "wine_quality_model.joblib"
METRICS_PATH = LOGS_DIR / "model_metrics.json"


def _required_processed_files() -> List[Path]:
    """Return the list of processed dataset paths that the model depends on."""
    return [
        PROCESSED_DIR / "X_train.csv",
        PROCESSED_DIR / "X_test.csv",
        PROCESSED_DIR / "y_train.csv",
        PROCESSED_DIR / "y_test.csv",
    ]


def ensure_processed_data_available(**context) -> None:
    """Verify the processed training artifacts exist before training the model."""
    missing_files = [path for path in _required_processed_files() if not path.exists()]
    if missing_files:
        logging.info("Processed data not ready yet. Waiting for files: %s", missing_files)
        raise FileNotFoundError(
            "The following processed datasets are missing: "
            + ", ".join(str(path) for path in missing_files)
        )

    logging.info("All required processed datasets are available: %s", _required_processed_files())


def _load_processed_data() -> Dict[str, pd.DataFrame]:
    """Load the processed train/test splits from disk."""
    X_train = pd.read_csv(PROCESSED_DIR / "X_train.csv")
    X_test = pd.read_csv(PROCESSED_DIR / "X_test.csv")
    y_train = pd.read_csv(PROCESSED_DIR / "y_train.csv").iloc[:, 0]
    y_test = pd.read_csv(PROCESSED_DIR / "y_test.csv").iloc[:, 0]

    logging.info("Loaded processed data with shapes: X_train=%s, X_test=%s", X_train.shape, X_test.shape)
    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
    }


def _build_model_pipeline() -> Pipeline:
    """Create the preprocessing and model training pipeline."""
    pipeline = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=300,
                    max_depth=None,
                    min_samples_leaf=1,
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )
    logging.info("Constructed training pipeline: %s", pipeline)
    return pipeline


def _evaluate(predictions, y_true) -> Dict[str, float]:
    """Evaluate the model predictions and return a dictionary of metrics."""
    metrics = {
        "mae": float(mean_absolute_error(y_true, predictions)),
        "mse": float(mean_squared_error(y_true, predictions)),
        "rmse": float(mean_squared_error(y_true, predictions, squared=False)),
        "r2": float(r2_score(y_true, predictions)),
    }
    logging.info("Evaluation metrics: %s", metrics)
    return metrics


def _persist_metrics(metrics: Dict[str, float], model_path: Path) -> None:
    """Persist metrics to a JSON log so runs are automatically captured."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    record = {
        "timestamp": timestamp,
        "model_path": str(model_path.relative_to(BASE_DIR)),
        "metrics": metrics,
    }

    existing_records: List[Dict[str, object]]
    if METRICS_PATH.exists():
        try:
            existing_records = json.loads(METRICS_PATH.read_text())
            if not isinstance(existing_records, list):
                existing_records = [existing_records]
        except json.JSONDecodeError:
            existing_records = []
    else:
        existing_records = []

    existing_records.append(record)
    METRICS_PATH.write_text(json.dumps(existing_records, indent=4))
    logging.info("Persisted metrics to %s", METRICS_PATH)


def train_evaluate_and_save_model(**context) -> None:
    """Load processed data, train the model, evaluate it, and persist artifacts."""
    data = _load_processed_data()
    pipeline = _build_model_pipeline()
    pipeline.fit(data["X_train"], data["y_train"])

    predictions = pipeline.predict(data["X_test"])
    metrics = _evaluate(predictions, data["y_test"])

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    logging.info("Saved trained model to %s", MODEL_PATH)

    _persist_metrics(metrics, MODEL_PATH)


def create_dag() -> DAG:
    default_args = {
        "owner": "airflow",
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
    }

    dag = DAG(
        dag_id="model_pipeline",
        description="Wine Quality Model Training Pipeline",
        schedule_interval="*/5 * * * *",
        start_date=datetime(2025, 9, 21, 0, 5),
        catchup=False,
        max_active_runs=1,
        default_args=default_args,
    )

    wait_for_data = PythonOperator(
        task_id="wait_for_processed_datasets",
        python_callable=ensure_processed_data_available,
        retries=12,
        retry_delay=timedelta(minutes=1),
        dag=dag,
    )

    train_model = PythonOperator(
        task_id="train_evaluate_and_save_model",
        python_callable=train_evaluate_and_save_model,
        dag=dag,
    )

    wait_for_data >> train_model

    return dag


dag = create_dag()