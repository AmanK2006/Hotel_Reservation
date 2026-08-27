pipeline {
    agent any

    environment {
        GCP_PROJECT = 'hotel-reservation-mlops-506720'
    }

    stages {
        stage('Cloning Github Repo to Jenkins') {
            steps {
                script {
                    echo 'Cloning Github repo to Jenkins............'
                }
            }
        }

        stage('Syncing Dependencies via uv') {
            steps {
                script {
                    echo 'Setting up environment and syncing dependencies............'
                    sh 'uv sync'
                }
            }
        }

        stage('Run Model Training Pipeline') {
            steps {
                withCredentials([file(credentialsId: 'json-token', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo 'Running ML training pipeline inside Jenkins............'
                        sh '''
                            # Authenticate with GCP for GCS access
                            gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                            gcloud config set project ${GCP_PROJECT}

                            # Set PYTHONPATH so 'src' imports resolve
                            export PYTHONPATH=.

                            # Fallback MLflow tracking to local file storage to avoid 127.0.0.1:5000 connection errors
                            export MLFLOW_TRACKING_URI=file:./mlruns

                            # Execute training script using uv
                            uv run python pipelines/training_pipeline.py
                        '''
                    }
                }
            }
        }

        stage('Building and Pushing Docker Image to GCR') {
            steps {
                withCredentials([file(credentialsId: 'json-token', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo 'Building and Pushing Docker Image to GCR............'
                        sh '''
                            gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                            gcloud config set project ${GCP_PROJECT}
                            gcloud auth configure-docker --quiet

                            # Build container image with pre-trained model artifacts included
                            docker build -t gcr.io/${GCP_PROJECT}/ml_project:latest .

                            # Push image to GCR
                            docker push gcr.io/${GCP_PROJECT}/ml_project:latest
                        '''
                    }
                }
            }
        }
    }
}