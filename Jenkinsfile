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

                            # Enable local file store tracking in MLflow
                            export MLFLOW_TRACKING_URI=file:./mlruns
                            export MLFLOW_ALLOW_FILE_STORE=true

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

        stage('Deploying on Google Cloud Run') {
            steps {
                withCredentials([file(credentialsId: 'json-token', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo 'Deploying on Google Cloud Run............'
                        sh '''
                            gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                            gcloud config set project ${GCP_PROJECT}
                            gcloud auth configure-docker --quiet

                            gcloud run deploy ml-project \
                            -- image=gcr.io/${GCP_PROJECT}/ml_project:latest \
                            -- platform=managed \
                            -- region=us-central1 \
                            -- allow=unauthenticated
                        '''
                    }
                }
            }
        }
    }
}