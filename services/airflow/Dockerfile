FROM apache/airflow:2.5.0

USER root
COPY requirements.txt /tmp/airflow-requirements.txt
RUN chown airflow: /tmp/airflow-requirements.txt

USER airflow
RUN pip install --no-cache-dir -r /tmp/airflow-requirements.txt \
    && rm /tmp/airflow-requirements.txt