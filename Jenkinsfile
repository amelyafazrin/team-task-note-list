pipeline {
    agent any

    environment {
        APP_NAME = 'team-task-note-list'
        COMPOSE_FILE = 'docker-compose.jenkins.yml'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Source code berhasil di-checkout.'
            }
        }

        stage('Syntax Check') {
            steps {
                echo 'Memeriksa syntax Python...'
                sh 'python3 -m py_compile backend/app.py'
                echo 'Syntax Python valid.'
            }
        }

        stage('Build Image') {
            steps {
                echo 'Building Docker images...'
                sh 'docker compose -p team-task-note-list -f docker-compose.jenkins.yml build'
            }
        }

        stage('Automated Deployment') {
            steps {
                echo 'Deploying application...'
                sh 'docker compose -p team-task-note-list -f docker-compose.jenkins.yml up -d'
            }
        }

        stage('Health Check') {
            steps {
                echo 'Checking backend health...'
                sh '''
                    for i in $(seq 1 15); do
                        if docker compose -p team-task-note-list -f docker-compose.jenkins.yml exec -T backend python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health', timeout=3)"; then
                            echo "Backend is healthy!"
                            exit 0
                        fi
                        sleep 2
                    done
                    echo "Backend health check failed!"
                    exit 1
                '''
            }
        }
    }

    post {
        success {
            echo 'CI/CD Pipeline berhasil!'
        }
        failure {
            echo 'CI/CD Pipeline gagal. Periksa console output.'
        }
    }
}
