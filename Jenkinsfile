pipeline {
    agent { label 'pine64' }
    
    environment {
        VENV_DIR = 'venv'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code...'
                checkout scm
            }
        }
        
        stage('Setup Virtual Environment') {
            steps {
                echo 'Creating virtual environment...'
                sh '''
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    python --version
                    pip --version
                '''
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo 'Installing dependencies...'
                sh '''
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                echo 'Running pytest...'
                sh '''
                    . ${VENV_DIR}/bin/activate
                    pytest tests/ \
                        --verbose \
                        --junit-xml=test-results/junit.xml \
                        --html=test-results/report.html \
                        --cov=src \
                        --cov-report=xml:test-results/coverage.xml \
                        --cov-report=html:test-results/htmlcov \
                        --cov-report=term-missing
                '''
            }
        }
    }
    
    post {
        always {
            echo 'Publishing test results...'
            
            // Publish JUnit test results
            junit testResults: 'test-results/junit.xml', allowEmptyResults: true
            
            // Publish HTML test report
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'test-results',
                reportFiles: 'report.html',
                reportName: 'Pytest Report'
            ])
            
            // Publish coverage report
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'test-results/htmlcov',
                reportFiles: 'index.html',
                reportName: 'Coverage Report'
            ])
            
            // Archive test artifacts
            archiveArtifacts artifacts: 'test-results/**/*', allowEmptyArchive: true
        }
        
        success {
            echo 'Tests passed successfully!'
        }
        
        failure {
            echo 'Tests failed!'
        }
        
        cleanup {
            echo 'Cleaning up...'
            sh 'rm -rf ${VENV_DIR}'
        }
    }
}