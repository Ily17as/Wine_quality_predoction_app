"""Airflow DAG that builds and deploys the application containers.

The pipeline waits for a trained model artefact to be available, synchronises it
with the deployment sources, rebuilds the API and Streamlit images and finally
restarts the running containers so that the most recent model is served.
"""

import logging
import shutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

from airflow import DAG
from airflow.operators.python import PythonOperator, ShortCircuitOperator

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[3]
MODEL_DIR = REPO_ROOT / "models"
APP_MODEL_PATH = REPO_ROOT / "code" / "deployment" / "app" / "models" / "wine_quality_model.joblib"
API_DOCKERFILE = REPO_ROOT / "code" / "deployment" / "api" / "Dockerfile"
APP_DOCKERFILE = REPO_ROOT / "code" / "deployment" / "app" / "Dockerfile"

API_IMAGE_TAG = "wine-quality-api:latest"
APP_IMAGE_TAG = "wine-quality-app:latest"
API_CONTAINER_NAME = "wine_quality_api"
APP_CONTAINER_NAME = "wine_quality_app"
DOCKER_NETWORK_NAME = "wine_network"
MODEL_XCOM_KEY = "model_artifact_path"


def _find_latest_model() -> Optional[Path]:
    """Return the most recently modified model artefact if it exists."""

    if not MODEL_DIR.exists():
        logger.info("Model directory %s does not exist yet", MODEL_DIR)
        return None

    candidates = list(MODEL_DIR.glob("*.joblib")) + list(MODEL_DIR.glob("*.pkl"))
    if not candidates:
        logger.info("No model artefacts found in %s", MODEL_DIR)
        return None

    candidates.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    latest = candidates[0]
    logger.info("Using latest model artefact: %s", latest)
    return latest


def model_available(**context) -> bool:
    """Short-circuit the DAG if no trained model is present."""

    latest_model = _find_latest_model()
    if latest_model is None:
        return False

    context["ti"].xcom_push(key=MODEL_XCOM_KEY, value=str(latest_model))
    return True


def sync_model_artifacts(**context) -> str:
    """Copy the latest model artefact to the deployment directories."""

    ti = context["ti"]
    model_path = Path(ti.xcom_pull(key=MODEL_XCOM_KEY, task_ids="wait_for_model"))
    if not model_path.exists():
        raise FileNotFoundError(f"Model artefact {model_path} is missing")

    target_api_model = MODEL_DIR / "wine_quality_model.joblib"
    if model_path.resolve() != target_api_model.resolve():
        shutil.copy2(model_path, target_api_model)
        logger.info("Copied model to %s", target_api_model)
    else:
        logger.info("Model artefact already located at %s", target_api_model)

    app_model_path = APP_MODEL_PATH
    app_model_path.parent.mkdir(parents=True, exist_ok=True)
    if model_path.resolve() != app_model_path.resolve():
        shutil.copy2(model_path, app_model_path)
        logger.info("Copied model to %s", app_model_path)
    else:
        logger.info("Model artefact already located at %s", app_model_path)

    return str(model_path)


def ensure_network_exists() -> None:
    """Create the Docker network if it is not available."""

    try:
        result = subprocess.run(
            [
                "docker",
                "network",
                "ls",
                "--filter",
                f"name=^{DOCKER_NETWORK_NAME}$",
                "--format",
                "{{.Name}}",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError as exc:  # pragma: no cover - helpful error message
        raise RuntimeError(
            "Docker CLI is required to run the deployment pipeline."
        ) from exc

    existing_networks = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    if DOCKER_NETWORK_NAME in existing_networks:
        logger.info("Docker network %s already exists", DOCKER_NETWORK_NAME)
        return

    subprocess.run(["docker", "network", "create", DOCKER_NETWORK_NAME], check=True)
    logger.info("Created docker network %s", DOCKER_NETWORK_NAME)


def build_docker_image(image_tag: str, dockerfile_path: Path) -> None:
    """Build the Docker image for the specified dockerfile."""

    logger.info("Building image %s using %s", image_tag, dockerfile_path)
    subprocess.run(
        [
            "docker",
            "build",
            "-t",
            image_tag,
            "-f",
            str(dockerfile_path),
            str(REPO_ROOT),
        ],
        check=True,
    )


def deploy_container(
    image_tag: str,
    container_name: str,
    ports: Dict[int, int],
    network: Optional[str] = None,
    environment: Optional[Dict[str, str]] = None,
) -> None:
    """Run the container, replacing any previous instance with the same name."""

    logger.info("Deploying container %s from image %s", container_name, image_tag)
    subprocess.run(["docker", "rm", "-f", container_name], check=False)

    cmd = ["docker", "run", "-d", "--name", container_name, "--restart", "always"]
    if network:
        cmd.extend(["--network", network])
    for host_port, container_port in ports.items():
        cmd.extend(["-p", f"{host_port}:{container_port}"])
    if environment:
        for key, value in environment.items():
            cmd.extend(["-e", f"{key}={value}"])

    cmd.append(image_tag)
    subprocess.run(cmd, check=True)


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="deployment_pipeline",
    description="Build and deploy the API and Streamlit services with the latest model",
    default_args=default_args,
    schedule_interval="*/5 * * * *",
    start_date=datetime(2023, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["deployment"],
) as dag:
    wait_for_model = ShortCircuitOperator(
        task_id="wait_for_model",
        python_callable=model_available,
    )

    sync_models = PythonOperator(
        task_id="sync_model_artifacts",
        python_callable=sync_model_artifacts,
    )

    prepare_network = PythonOperator(
        task_id="ensure_network",
        python_callable=ensure_network_exists,
    )

    build_api_image = PythonOperator(
        task_id="build_api_image",
        python_callable=build_docker_image,
        op_kwargs={"image_tag": API_IMAGE_TAG, "dockerfile_path": API_DOCKERFILE},
    )

    deploy_api = PythonOperator(
        task_id="deploy_api",
        python_callable=deploy_container,
        op_kwargs={
            "image_tag": API_IMAGE_TAG,
            "container_name": API_CONTAINER_NAME,
            "ports": {8000: 8000},
            "network": DOCKER_NETWORK_NAME,
        },
    )

    build_app_image = PythonOperator(
        task_id="build_app_image",
        python_callable=build_docker_image,
        op_kwargs={"image_tag": APP_IMAGE_TAG, "dockerfile_path": APP_DOCKERFILE},
    )

    deploy_app = PythonOperator(
        task_id="deploy_app",
        python_callable=deploy_container,
        op_kwargs={
            "image_tag": APP_IMAGE_TAG,
            "container_name": APP_CONTAINER_NAME,
            "ports": {8501: 8501},
            "network": DOCKER_NETWORK_NAME,
        },
    )

    wait_for_model >> sync_models >> prepare_network
    prepare_network >> build_api_image >> deploy_api
    deploy_api >> build_app_image >> deploy_app