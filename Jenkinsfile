pipeline {
    agent any
    
    parameters {
        string(name: 'IMAGE_TAG', defaultValue: 'latest', description: 'Docker image tag')
        string(name: 'REGISTRY', defaultValue: 'docker.io', description: 'Docker registry')
        string(name: 'IMAGE_NAME', defaultValue: 'student-management-system', description: 'Docker image name')
        string(name: 'DOCKER_USERNAME', defaultValue: '', description: 'Docker registry username')
        booleanParam(name: 'DEPLOY_TO_K8S', defaultValue: true, description: 'Deploy to Kubernetes')
        string(name: 'K8S_NAMESPACE', defaultValue: 'student-system', description: 'Kubernetes namespace')
    }
    
    environment {
        DOCKER_CREDENTIALS = credentials('docker-credentials')
        KUBECONFIG = credentials('kubeconfig')
        // removed BUILD_TIMESTAMP and GIT_REPO sh calls from here (they must run on agent)
    }
    
    stages {
        stage('Checkout') {
            steps {
                script {
                    echo '========== Checking out code =========='
                    checkout scm
                    // compute values that require a workspace/agent
                    env.GIT_REPO = env.GIT_URL
                    env.BUILD_TIMESTAMP = sh(script: "date +'%Y%m%d_%H%M%S'", returnStdout: true).trim()
                    echo "GIT_REPO=${env.GIT_REPO}, BUILD_TIMESTAMP=${env.BUILD_TIMESTAMP}"
                }
            }
        }
        
        stage('Build') {
            steps {
                script {
                    echo '========== Building application =========='
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                    '''
                }
            }
        }
        
        stage('Test') {
            steps {
                script {
                    echo '========== Running tests =========='
                    sh '''
                        . venv/bin/activate
                        python -m pytest tests/ -v --cov=. --cov-report=xml || true
                    '''
                }
            }
        }
        
        stage('Code Quality') {
            steps {
                script {
                    echo '========== Running code quality checks =========='
                    sh '''
                        . venv/bin/activate
                        pylint app.py || true
                        flake8 app.py --max-line-length=100 || true
                    '''
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    echo '========== Building Docker image =========='
                    sh '''
                        docker build -t ${REGISTRY}/${DOCKER_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG} .
                        docker tag ${REGISTRY}/${DOCKER_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${DOCKER_USERNAME}/${IMAGE_NAME}:latest
                    '''
                }
            }
        }
        
        stage('Push Docker Image') {
            steps {
                script {
                    echo '========== Pushing Docker image to registry =========='
                    sh '''
                        echo $DOCKER_CREDENTIALS_PSW | docker login -u $DOCKER_CREDENTIALS_USR --password-stdin ${REGISTRY}
                        docker push ${REGISTRY}/${DOCKER_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}
                        docker push ${REGISTRY}/${DOCKER_USERNAME}/${IMAGE_NAME}:latest
                        docker logout ${REGISTRY}
                    '''
                }
            }
        }
        
        stage('Create Kubernetes Namespace') {
            when {
                expression { params.DEPLOY_TO_K8S == true }
            }
            steps {
                script {
                    echo '========== Creating Kubernetes namespace =========='
                    sh '''
                        kubectl create namespace ${K8S_NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                    '''
                }
            }
        }
        
        stage('Deploy to Kubernetes') {
            when {
                expression { params.DEPLOY_TO_K8S == true }
            }
            steps {
                script {
                    echo '========== Deploying to Kubernetes =========='
                    sh '''
                        # Update image tag in deployment.yaml
                        sed -i "s|IMAGE_TAG|${REGISTRY}/${DOCKER_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}|g" k8s/deployment.yaml
                        
                        # Apply Kubernetes manifests
                        kubectl apply -f k8s/ -n ${K8S_NAMESPACE}
                        
                        # Wait for deployment to be ready
                        kubectl rollout status deployment/student-management-system -n ${K8S_NAMESPACE} --timeout=5m
                    '''
                }
            }
        }
        
        stage('Health Check') {
            when {
                expression { params.DEPLOY_TO_K8S == true }
            }
            steps {
                script {
                    echo '========== Performing health check =========='
                    sh '''
                        sleep 10
                        POD_NAME=$(kubectl get pods -n ${K8S_NAMESPACE} -l app=student-management-system -o jsonpath='{.items[0].metadata.name}')
                        kubectl port-forward -n ${K8S_NAMESPACE} $POD_NAME 5000:5000 &
                        sleep 5
                        curl -f http://localhost:5000/health || exit 1
                    '''
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo '========== Cleaning up =========='
                // guard the sh with a presence check to avoid MissingContextVariable when no workspace/filepath is available
                if (env.WORKSPACE) {
                    sh 'rm -rf venv || true'
                } else {
                    echo 'No workspace available; skipping cleanup'
                }
            }
        }
        
        success {
            echo '========== Pipeline completed successfully =========='
        }
        
        failure {
            echo '========== Pipeline failed =========='
        }
    }
}
