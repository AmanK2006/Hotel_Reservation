pipeline {
    agent any

    environment{
        GCP_PROJECT = "hotel-reservation-mlops-506720"
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
                withCredentials([file(credentialId : 'json-token', variable: 'GOOGLE_APPLICATION_CREDENTIALS')])
                script {
                    echo 'Building and Pushing Docker Image to Jenkins............'
                    sh '''
                    export PATH = $PATH: ${GCLOUD_PATH}

                    gcloud auth activate-service-account --key-file = ${GOOGLE_APPLICATION_CREDENTIALS}

                    gcloud config set project ${GCP_PROJECT}

                    gcloud auth configure-docker --quiet

                    docker build -t gcr.io/${GCP_PROJECT}/ml_project:latest .

                    docker push gcr.io/${GCP_PROJECT}/ml_project:latest
                    
                    '''
                }
            }
        }
    }
}