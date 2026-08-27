pipeline {
    agent any

    environment {
        GCP_PROJECT = 'hotel-reservation-mlops-506720'
        GCLOUD_PATH = "/var/jenkins_home/google-cloud-sdk/bin"
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

        stage('Building and Pushing Docker Image to GCR') {
            steps {
                withCredentials([file(credentialsId: 'json-token', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo 'Building and Pushing Docker Image to GCR............'
                        
                        sh '''
                            export PATH=$PATH:${GCLOUD_PATH}
                            
                            # Authenticate service account using the uploaded JSON key
                            gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}

                            # Set active GCP project
                            gcloud config set project ${GCP_PROJECT}

                            # Configure Docker CLI to use GCP credentials
                            gcloud auth configure-docker --quiet

                            # Build the ML application container
                            docker build -t gcr.io/${GCP_PROJECT}/ml_project:latest .

                            # Push image to Container Registry
                            docker push gcr.io/${GCP_PROJECT}/ml_project:latest
                        '''
                    }
                }
            }
        }
    }
}