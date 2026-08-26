pipeline {
    agent any

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
    }
}