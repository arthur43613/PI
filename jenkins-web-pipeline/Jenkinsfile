pipeline {
    agent any

    environment {
        DOCKER_HUB_USER = 'educg11'
        IMAGE_PYTHON = "${DOCKER_HUB_USER}/python-generator"
        IMAGE_R = "${DOCKER_HUB_USER}/r-cleaner"
        IMAGE_DASH = "${DOCKER_HUB_USER}/dash-app"
        IMAGE_GRAFANA = "${DOCKER_HUB_USER}/custom-grafana"
        GIT_REPO_URL = 'https://github.com/CarlosEducg11/jenkins-web-pipeline.git'
        GIT_CREDENTIALS_ID = 'github-creds'
    }

    stages {
        stage('Clone Git Repository') {
            steps {
                script {
                    git credentialsId: "${GIT_CREDENTIALS_ID}", url: "${GIT_REPO_URL}"
                }
            }
        }

        stage('Build and Push Docker Images') {
            steps {
                script {
                    sh "docker build -t ${IMAGE_PYTHON}:latest ./python-generator"
                    sh "docker build -t ${IMAGE_R}:latest ./r-cleaner"
                    sh "docker build -t ${IMAGE_DASH}:latest ./dash-app"
                    sh "docker build -t ${IMAGE_GRAFANA}:latest ./grafana"

                    withCredentials([usernamePassword(credentialsId: 'token2', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh "echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin"
                        sh "docker push ${IMAGE_PYTHON}:latest"
                        sh "docker push ${IMAGE_R}:latest"
                        sh "docker push ${IMAGE_DASH}:latest"
                        sh "docker push ${IMAGE_GRAFANA}:latest"
                    }
                }
            }
        }

        stage('Deploy with Docker Compose') {
            steps {
                script {
                    sh 'docker-compose down'
                    sh 'docker-compose pull'
                    sh 'docker-compose up -d --build'
                }
            }
        }

        stage('Stop Containers') { 
            steps {
                sh 'docker-compose down'
            }
        }
    }
}
