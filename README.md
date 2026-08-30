# Hotel Reservation MLOps Project

An end-to-end Machine Learning Operations (MLOps) project that predicts hotel reservation outcomes (e.g., cancellations) using a LightGBM model. The project features a complete pipeline from data processing and model training to deployment, utilizing a modern tech stack with a strong focus on CI/CD and cloud deployment.

## 🚀 Features

- **End-to-End ML Pipeline:** Modularized scripts for data ingestion, processing, and model training.
- **Web Interface:** A Flask-based web application to interact with the trained model and get real-time predictions.
- **Experiment Tracking:** MLflow integration for tracking model parameters, metrics, and artifacts locally.
- **CI/CD Automation:** A fully configured Jenkins pipeline (`Jenkinsfile`) to automate testing, building, and deployment.
- **Containerization:** Dockerfile provided for reproducible environments and cloud deployment.
- **Cloud Deployment:** Automated deployment to Google Cloud Run via Google Container Registry (GCR).
- **Fast Dependency Management:** Utilizes `uv` for lightning-fast Python package resolution and installation.

## 🛠️ Technologies Used

- **Programming Language:** Python 3.12+
- **Machine Learning:** LightGBM, scikit-learn, XGBoost, imbalanced-learn
- **Experiment Tracking:** MLflow
- **Web Framework:** Flask
- **Dependency Management:** `uv` (`pyproject.toml`)
- **Containerization:** Docker
- **CI/CD:** Jenkins
- **Cloud Provider:** Google Cloud Platform (GCR, Cloud Run)

## 📁 Project Structure

```bash
Hotel_Reservation/
├── artifacts/             # Stored raw/processed data and trained models
├── config/                # Configuration files (paths, hyperparams)
├── pipelines/             # ML training and prediction pipelines
├── src/                   # Source code for data processing and model training
├── static/                # Static assets for the Flask app
├── templates/             # HTML templates for the web interface
├── notebooks/             # Jupyter notebooks for exploratory data analysis
├── application.py         # Flask application entry point
├── Dockerfile             # Container definition
├── Jenkinsfile            # Jenkins CI/CD pipeline configuration
├── pyproject.toml         # Python dependencies and project metadata
└── setup.py               # Package setup script
```

## ⚙️ Local Setup & Installation

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) (for fast dependency management)

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd Hotel_Reservation
```

### 2. Install dependencies using `uv`

```bash
# Sync dependencies and create a virtual environment
uv sync
```

### 3. Run Model Training (Optional)

If you want to retrain the model locally (make sure data is present in `artifacts/raw`):

```bash
uv run python pipelines/training_pipeline.py
```
*Note: This will also log the run in the local `mlruns` directory via MLflow.*

### 4. Start the Web Application

```bash
uv run python application.py
```
The application will be accessible at `http://localhost:8080` (or `http://0.0.0.0:8080`).

## 🐳 Docker Setup

To build and run the application using Docker:

```bash
# Build the Docker image
docker build -t hotel-reservation-app .

# Run the container
docker run -p 8080:8080 hotel-reservation-app
```

## 🔄 CI/CD Pipeline

This project uses Jenkins for Continuous Integration and Continuous Deployment. The pipeline defined in `Jenkinsfile` consists of the following stages:

1. **Cloning Github Repo:** Pulls the latest code.
2. **Syncing Dependencies:** Uses `uv` to install dependencies in the CI environment.
3. **Model Training:** Executes the ML pipeline and tracks experiments using MLflow.
4. **Build & Push Docker Image:** Builds the application container and pushes it to Google Container Registry (GCR).
5. **Deploy to Cloud Run:** Deploys the latest container to Google Cloud Run, making it publicly accessible.

### CI/CD Environment Requirements
- A Jenkins server with Docker and Google Cloud SDK (`gcloud`) installed.
- Appropriate GCP Service Account credentials stored in Jenkins as `json-token`.

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request if you have suggestions for improvements.

## 📝 License

This project is licensed under the MIT License.
