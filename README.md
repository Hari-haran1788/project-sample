# Student Management System

A comprehensive Student Management System built with Flask, Docker, and Kubernetes. This application allows managing student records and their academic grades.

## Features

- **Student Management**: Add, update, delete, and retrieve student information
- **Grade Management**: Track student grades across semesters and subjects
- **RESTful API**: Complete REST API for all operations
- **Docker Containerization**: Production-ready Docker image
- **Kubernetes Deployment**: Ready for Kubernetes orchestration
- **CI/CD Pipeline**: Jenkins pipeline for automated build and deployment
- **Health Checks**: Built-in health monitoring
- **Security**: Non-root container user, RBAC, security contexts
- **Scalability**: HorizontalPodAutoscaler for automatic scaling
- **High Availability**: Pod disruption budgets and anti-affinity rules

## Technology Stack

- **Backend**: Flask 3.0.0
- **Database**: SQLAlchemy (SQLite by default, PostgreSQL ready)
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **CI/CD**: Jenkins
- **Server**: Gunicorn
- **Testing**: pytest

## Project Structure

```
project-sample/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker image definition
├── Jenkinsfile                 # Jenkins CI/CD pipeline
├── docker-compose.yml          # Docker Compose setup
├── nginx.conf                  # Nginx configuration
├── .dockerignore               # Docker ignore file
├── .env.example                # Environment variables template
├── tests/
│   └── test_app.py            # Unit tests
├── k8s/                        # Kubernetes manifests
│   ├── namespace.yaml         # Namespace configuration
│   ├── deployment.yaml        # Deployment configuration
│   ├── service.yaml           # Service configuration
│   ├── configmap.yaml         # ConfigMap configuration
│   ├── secret.yaml            # Secret configuration
│   ├── hpa.yaml               # HorizontalPodAutoscaler
│   ├── pdb.yaml               # PodDisruptionBudget
│   ├── rbac.yaml              # RBAC configuration
│   ├── ingress.yaml           # Ingress configuration
│   ├── monitoring.yaml        # Monitoring configuration
│   └── kustomization.yaml     # Kustomize deployment
└── README.md                   # This file
```

## Local Development

### Prerequisites

- Python 3.11+
- Docker (for containerization)
- Kubernetes cluster (for deployment)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Hari-haran1788/project-sample.git
   cd project-sample
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

   The application will be available at `http://localhost:5000`

## Docker Compose

### Run with Docker Compose

```bash
docker-compose up -d
```

Services:
- Web App: http://localhost (via Nginx)
- Flask API: http://localhost:5000
- PostgreSQL: localhost:5432

### Stop Services

```bash
docker-compose down
```

## API Endpoints

### Health Check
- `GET /health` - Health check endpoint

### Students
- `GET /api/students` - Get all students (paginated)
- `GET /api/students/<id>` - Get specific student
- `POST /api/students` - Create new student
- `PUT /api/students/<id>` - Update student
- `DELETE /api/students/<id>` - Delete student

### Grades
- `GET /api/students/<id>/grades` - Get student's grades
- `POST /api/grades` - Add grade for student
- `DELETE /api/grades/<id>` - Delete grade

## Docker

### Build Docker Image

```bash
docker build -t student-management-system:latest .
```

### Run Docker Container

```bash
docker run -p 5000:5000 \
  -e DATABASE_URL="sqlite:///students.db" \
  -e SECRET_KEY="your-secret-key" \
  student-management-system:latest
```

## Kubernetes Deployment

### Prerequisites

- Kubectl configured and connected to your Kubernetes cluster
- Docker image pushed to a registry

### Deploy to Kubernetes

1. **Create namespace and deploy**
   ```bash
   kubectl apply -f k8s/namespace.yaml
   kubectl apply -f k8s/ -n student-system
   ```

2. **Update secrets (important!)**
   ```bash
   kubectl create secret generic student-system-secrets \
     -n student-system \
     --from-literal=database-url="your-db-url" \
     --from-literal=secret-key="your-secret-key" \
     --dry-run=client -o yaml | kubectl apply -f -
   ```

3. **Check deployment status**
   ```bash
   kubectl get deployments -n student-system
   kubectl get pods -n student-system
   kubectl get services -n student-system
   ```

4. **Access the application**
   ```bash
   # Using port forwarding
   kubectl port-forward -n student-system svc/student-management-system 5000:80
   # Application will be available at http://localhost:5000
   ```

## Jenkins Pipeline

### Setup

1. **Create Jenkins credentials**
   - `docker-credentials`: Docker registry credentials
   - `kubeconfig`: Kubernetes configuration

2. **Create Jenkins pipeline job**
   - Point to this repository
   - Use `Jenkinsfile` as the pipeline script

3. **Configure parameters**
   - IMAGE_TAG: Docker image tag
   - REGISTRY: Docker registry URL
   - IMAGE_NAME: Docker image name
   - DOCKER_USERNAME: Docker registry username
   - DEPLOY_TO_K8S: Deploy to Kubernetes
   - K8S_NAMESPACE: Kubernetes namespace

## Testing

### Run Unit Tests

```bash
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ -v --cov=. --cov-report=html
```

## API Examples

### Create a Student

```bash
curl -X POST http://localhost:5000/api/students \
  -H "Content-Type: application/json" \
  -d '{
    "roll_number": "STU001",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "1234567890",
    "address": "123 Main St",
    "class_name": "Class A"
  }'
```

### Get All Students

```bash
curl http://localhost:5000/api/students?page=1&per_page=10
```

### Add Grade

```bash
curl -X POST http://localhost:5000/api/grades \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "subject": "Mathematics",
    "marks": 95.5,
    "grade": "A",
    "semester": "Sem 1"
  }'
```

## Security Considerations

- Application runs as non-root user
- Read-only root filesystem where possible
- Security contexts configured in Kubernetes
- Secrets management via Kubernetes Secrets
- RBAC configuration for least privilege access
- Network policies can be added for additional security
- Health checks configured for pod auto-recovery

## Monitoring

The deployment includes:
- Liveness probes (checks if pod is running)
- Readiness probes (checks if pod is ready for traffic)
- Resource requests and limits
- HorizontalPodAutoscaler for automatic scaling
- PodDisruptionBudget for high availability

## Environment Variables

```
FLASK_ENV=production
DATABASE_URL=sqlite:///students.db
SECRET_KEY=your-secret-key
LOG_LEVEL=INFO
```

## Troubleshooting

### Pod not starting?
```bash
kubectl describe pod <pod-name> -n student-system
kubectl logs <pod-name> -n student-system
```

### Database connectivity issues?
```bash
# Check secrets
kubectl get secrets -n student-system
kubectl describe secret student-system-secrets -n student-system
```

### Port forwarding?
```bash
kubectl port-forward -n student-system svc/student-management-system 5000:80
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions, please open an issue on GitHub.