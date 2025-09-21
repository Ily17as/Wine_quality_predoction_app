from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

# Загрузка обученной модели
model = joblib.load("/app/models/wine_quality_model.joblib")

# Инициализация FastAPI
app = FastAPI()

# Модель данных для входных признаков
class WineFeatures(BaseModel):
    fixed_acidity: float
    volatile_acidity: float
    citric_acid: float
    residual_sugar: float
    chlorides: float
    free_sulfur_dioxide: float
    total_sulfur_dioxide: float
    density: float
    pH: float
    sulphates: float
    alcohol: float

# Эндпоинт для предсказания качества вина
@app.post("/predict/")
async def predict(features: WineFeatures):
    data = np.array([[
        features.fixed_acidity,
        features.volatile_acidity,
        features.citric_acid,
        features.residual_sugar,
        features.chlorides,
        features.free_sulfur_dioxide,
        features.total_sulfur_dioxide,
        features.density,
        features.pH,
        features.sulphates,
        features.alcohol
    ]])
    prediction = model.predict(data)
    return {"prediction": int(prediction[0])}
