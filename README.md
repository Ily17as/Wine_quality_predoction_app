
# Wine Quality Prediction App

A Streamlit web application for predicting whether a red wine sample is “good” or “bad” based on its physicochemical properties. The app loads a pre-trained Random Forest classifier to deliver instant predictions and probability estimates.

## Features

- Interactive web interface powered by Streamlit  
- Input form for 11 chemical measurements (acidity, sulfur dioxide, sugar, alcohol, etc.)  
- Binary classification: **good** (quality ≥ 7) vs **bad** (quality < 7)  
- Probability score for the “good” class  
- Self-contained: model, preprocessing and inference all wrapped in one pipeline


**The project includes:**

- **FastAPI**: for creating a RESTful API serving the model.
- **Streamlit**: for developing an interactive web application.
- **Docker**: for containerizing the application and ensuring reproducibility.
- **Docker Compose**: for simplifying the management of multi-container applications.

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

## Build and Run with Docker Compose

```bash
docker-compose up --build
```
This will build and start two containers:
- API: accessible at http://localhost:8000/docs
 for testing endpoints.

- Streamlit App: accessible at http://localhost:8501
 for user interaction.
## Project Structure

## Stop the Containers
```bash
docker-compose down
```

```
.
├── code/
│ ├── deployment/
│ │ ├── api/ # FastAPI application
│ │ │ ├── Dockerfile
│ │ │ └── main.py
│ │ │
│ │ └── app/ # Streamlit application
│ │ ├── Dockerfile 
│ │ ├── app.py 
│ └─└── models/ # Models and training scripts
│
├── data/ # Raw and processed data
├── models/ # Saved models
├── requirements.txt # Common dependencies
└── docker-compose.yml # Docker Compose configuration
```

## Contributing

1. Fork the repository  
2. Create a feature branch (`git checkout -b feature/your-feature`)  
3. Commit your changes (`git commit -m "Add your feature"`)  
4. Push to your branch (`git push origin feature/your-feature`)  
5. Open a pull request

Please follow standard Python style (PEP 8) and write clear, descriptive commit messages.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
