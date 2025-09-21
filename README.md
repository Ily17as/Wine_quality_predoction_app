
# Wine Quality Prediction App

## Project Overview
The Wine Quality Prediction App is an end-to-end solution for classifying red wines as "good" or "bad" based on eleven physicochemical properties. It combines a FastAPI microservice for programmatic inference, a Streamlit dashboard for interactive exploration, and Apache Airflow pipelines for orchestrating data preparation, model training, and deployment tasks. A pre-trained scikit-learn model bundled with the repository delivers instant predictions, while Docker Compose ensures reproducible, multi-service deployments.

### Key Features
- **Binary quality classification** powered by a scikit-learn ensemble stored in `models/wine_quality_model.joblib`.
- **FastAPI REST service** that accepts JSON payloads and returns predictions for integration with other systems.
- **Streamlit web interface** for manual data entry, visualization, and probability feedback.
- **Apache Airflow pipelines** (`services/airflow/dags/`) for data ingestion, model retraining, and deployment automation.
- **Dockerized deployment** of the API, web app, Airflow components, and PostgreSQL metadata database.

## Requirements & Dependencies
| Component | Version / Notes |
|-----------|-----------------|
| Python | 3.9 or newer (for local execution) |
| Pip & Virtualenv | Recommended for dependency isolation |
| Docker | 20.10+ |
| Docker Compose plugin | 2.5+ |
| Python packages | Listed in [`requirements.txt`](requirements.txt) and [`services/airflow/requirements.txt`](services/airflow/requirements.txt) |

Additional datasets are stored under [`data/`](data/) and trained models under [`models/`](models/).

## Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/Ily17as/Wine_quality_predoction_app.git
   cd Wine_quality_predoction_app
   ```

2. **Set up a Python environment (optional but recommended)**  
   ```bash
   python3 -m venv venv
   source venv/bin/activate      # macOS/Linux
   venv\Scripts\activate       # Windows
   ```

3. **Install Python dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   # Airflow-specific extras (only if running Airflow locally)
   pip install -r services/airflow/requirements.txt
   ```

## Running the Project
### Using Docker Compose (recommended)
1. **Initialize Airflow metadata and admin user**
   ```bash
   docker compose up airflow-init
   ```
   Wait for the command to finish successfully before continuing.
2. **Build and start all services**
   ```bash
   docker compose up --build
   ```
   This command launches the following containers:
   - **app** – Streamlit UI available at http://localhost:8501
   - **api** – FastAPI service with interactive docs at http://localhost:8000/docs
   - **airflow-webserver** – Airflow UI at http://localhost:8080 (login: `admin`/`admin`)
   - **airflow-scheduler**, **airflow-init**, and **postgres** supporting services
3. **Stop and clean up**
   ```bash
   docker compose down
   ```
### Local execution without Docker
1. **Start the FastAPI service**
   ```bash
   uvicorn code.deployment.api.main:app --host 0.0.0.0 --port 8000 --reload
   ```
2. **Run the Streamlit dashboard** (in a separate terminal)
   ```bash
   streamlit run code/deployment/app/app.py
   ```
3. **(Optional) Launch Airflow locally** – requires a running PostgreSQL instance and proper environment variables mirroring the Docker configuration.

## Usage
### Streamlit UI
1. Navigate to http://localhost:8501.
2. Enter the eleven chemical measurements using the sliders and numeric inputs.
3. Click **Predict Quality** to receive the classification (`GOOD` or `BAD`) and the associated probability.

### FastAPI Endpoints
- Interactive API documentation: http://localhost:8000/docs
- Sample prediction request:
  ```bash
  curl -X POST http://localhost:8000/predict/ \
       -H "Content-Type: application/json" \
       -d '{
            "fixed_acidity": 7.4,
            "volatile_acidity": 0.7,
            "citric_acid": 0.0,
            "residual_sugar": 1.9,
            "chlorides": 0.076,
            "free_sulfur_dioxide": 11,
            "total_sulfur_dioxide": 34,
            "density": 0.9978,
            "pH": 3.51,
            "sulphates": 0.56,
            "alcohol": 9.4
          }'
  ```
  The response returns `{ "prediction": 0 }` or `{ "prediction": 1 }`, where `1` represents a high-quality wine.

### Airflow Pipelines
Airflow DAGs located in [`services/airflow/dags/`](services/airflow/dags/) orchestrate data preparation, model training, and deployment steps. Once the Airflow webserver is running:
1. Visit http://localhost:8080 and sign in with `admin` / `admin`.
2. Enable the desired DAGs (`data_pipeline`, `model_pipeline`, `deployment_pipeline`).
3. Trigger DAG runs manually or rely on their defined schedules.

## Project Structure
```
.
├── code/
│   └── deployment/
│       ├── api/
│       │   ├── Dockerfile
│       │   └── main.py
│       └── app/
│           ├── Dockerfile
│           └── app.py
├── data/
├── models/
├── services/
│   └── airflow/
│       ├── dags/
│       ├── Dockerfile
│       └── requirements.txt
├── docker-compose.yml
└── requirements.txt
```

## Support & Contact
- For questions and bug reports, please open an [issue on GitHub](https://github.com/Ily17as/Wine_quality_predoction_app/issues).
- For commercial support or collaboration inquiries, reach out via email: <ilyas_gal@internet.com>.

## License

This project is released under the [MIT License](LICENSE).