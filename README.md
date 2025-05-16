
# Wine Quality Prediction App

A Streamlit web application for predicting whether a red wine sample is “good” or “bad” based on its physicochemical properties. The app loads a pre-trained Random Forest classifier to deliver instant predictions and probability estimates.

## Features

- Interactive web interface powered by Streamlit  
- Input form for 11 chemical measurements (acidity, sulfur dioxide, sugar, alcohol, etc.)  
- Binary classification: **good** (quality ≥ 7) vs **bad** (quality < 7)  
- Probability score for the “good” class  
- Self-contained: model, preprocessing and inference all wrapped in one pipeline

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

3. **Install dependencies**  
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Usage

1. Ensure the model file `wine_quality_model.joblib` is located in the project root.  
2. Launch the Streamlit app:  
   ```bash
   streamlit run app.py
   ```  
3. In the browser window that opens, enter the wine’s physicochemical parameters and click **Predict Quality**.  
4. The app will display the predicted class and the probability for “good” wine.

## Project Structure

```
.
├── app.py                          # Streamlit application
├── wine_quality_model.joblib       # Pre-trained Random Forest model
├── requirements.txt                # List of Python dependencies
├── notebooks/                      # Jupyter notebooks for EDA and training
│   ├── 01_data_exploration.ipynb
│   └── 02_model_training.ipynb
└── README.md                       # This documentation
```

## Retraining the Model

To retrain or refine the classifier:

1. Open the notebooks in the `notebooks/` directory.  
2. Follow the sections in order:
   - Data loading and exploratory analysis  
   - Preprocessing (winsorization, scaling, train/test split)  
   - Statistical hypothesis testing  
   - Model training with cross-validation and hyperparameter search  
3. Export the best model to `wine_quality_model.joblib`:
   ```python
   import joblib
   joblib.dump(best_pipeline, 'wine_quality_model.joblib')
   ```

## Requirements

- Python 3.7+  
- streamlit  
- pandas  
- scikit-learn  
- joblib  
- scipy  

_(All listed in `requirements.txt`.)_

## Contributing

1. Fork the repository  
2. Create a feature branch (`git checkout -b feature/your-feature`)  
3. Commit your changes (`git commit -m "Add your feature"`)  
4. Push to your branch (`git push origin feature/your-feature`)  
5. Open a pull request

Please follow standard Python style (PEP 8) and write clear, descriptive commit messages.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
