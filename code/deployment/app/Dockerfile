FROM python:3.9-slim

WORKDIR /app

COPY code/deployment/app/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY ./code/deployment/app/ /app/

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]
