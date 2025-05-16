
import streamlit as st
import pandas as pd
import joblib

st.title("Wine Quality Prediction")
st.write("Введите физико-химические параметры красного вина:")

# Ввод признаков
features = {
    'fixed acidity': st.number_input('Fixed Acidity', min_value=0.0, value=7.4, step=0.1),
    'volatile acidity': st.number_input('Volatile Acidity', min_value=0.0, value=0.7, step=0.01),
    'citric acid': st.number_input('Citric Acid', min_value=0.0, value=0.0, step=0.01),
    'residual sugar': st.number_input('Residual Sugar', min_value=0.0, value=1.9, step=0.1),
    'chlorides': st.number_input('Chlorides', min_value=0.0, value=0.076, step=0.001),
    'free sulfur dioxide': st.number_input('Free Sulfur Dioxide', min_value=0.0, value=11.0, step=1.0),
    'total sulfur dioxide': st.number_input('Total Sulfur Dioxide', min_value=0.0, value=34.0, step=1.0),
    'density': st.number_input('Density', min_value=0.0, value=0.9978, step=0.0001, format="%.4f"),
    'pH': st.number_input('pH', min_value=0.0, max_value=14.0, value=3.51, step=0.01),
    'sulphates': st.number_input('Sulphates', min_value=0.0, value=0.56, step=0.01),
    'alcohol': st.number_input('Alcohol', min_value=0.0, value=9.4, step=0.1)
}

if st.button("Predict Quality"):
    # Сбор в DataFrame
    X_new = pd.DataFrame([features])
    # Загрузка модели (убедитесь, что wine_quality_model.joblib лежит рядом с app.py)
    model = joblib.load("wine_quality_model.joblib")
    # Предсказание
    pred = model.predict(X_new)[0]
    proba = model.predict_proba(X_new)[0][1]
    # Вывод
    if pred == 1:
        st.success(f"Вино классифицировано как GOOD (вероятность {proba:.2f})")
    else:
        st.warning(f"Вино классифицировано как BAD (вероятность {1 - proba:.2f})")
