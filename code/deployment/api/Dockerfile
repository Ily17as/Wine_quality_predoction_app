FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY ./models /app/models

COPY ./code/deployment/api/ /app/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

#FROM python:3.9-slim
#
#WORKDIR /app
#
## Копируем requirements
#COPY requirements.txt /app/
#
## Устанавливаем зависимости
#RUN pip install --no-cache-dir -r requirements.txt
#
## Копируем весь код в контейнер
#COPY ./code/deployment/ /app/
#
#CMD ["python", "main.py"]
