# Deployment Guide - Customer Success Copilot

## 🚀 Quick Start (Development)

### Prerequisites
- Docker & Docker Compose
- Python 3.9+
- Node.js 16+
- Git

### Local Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/your-org/customer-success-copilot.git
cd customer-success-copilot
```

2. **Start infrastructure services**
```bash
# Start all infrastructure services (PostgreSQL, Redis, Airflow, etc.)
docker-compose up -d

# Wait for services to be ready (check health)
docker-compose ps
```

3. **Set up backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the backend API
uvicorn app.main:app --reload --port 8000
```

4. **Set up frontend**
```bash
cd frontend
npm install
npm run dev
```

5. **Access the application**
- **Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Airflow**: http://localhost:8080 (admin/admin)
- **MLflow**: http://localhost:5000
- **Jupyter**: http://localhost:8888
- **Grafana**: http://localhost:3000 (admin/admin123)

## 🛠️ Configuration

### Environment Variables

#### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://cs_user:cs_password@localhost:5432/customer_success
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External Integrations
SALESFORCE_CLIENT_ID=your-salesforce-client-id
SALESFORCE_CLIENT_SECRET=your-salesforce-client-secret
ZENDESK_API_TOKEN=your-zendesk-token
SLACK_BOT_TOKEN=your-slack-bot-token

# ML Platform
MLFLOW_TRACKING_URI=http://localhost:5000
S3_ENDPOINT_URL=http://localhost:9000
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin123

# Monitoring
PROMETHEUS_ENDPOINT=http://localhost:9090
```

#### Frontend (.env)
```bash
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
REACT_APP_VERSION=0.1.0
```

## 🏗️ Production Deployment

### Option 1: Kubernetes Deployment

#### Prerequisites
- Kubernetes cluster (1.25+)
- kubectl configured
- Helm 3.x
- Container registry access

#### 1. Build and Push Images

```bash
# Build backend image
docker build -t your-registry/cs-copilot-backend:latest ./backend
docker push your-registry/cs-copilot-backend:latest

# Build frontend image
docker build -t your-registry/cs-copilot-frontend:latest ./frontend
docker push your-registry/cs-copilot-frontend:latest
```

#### 2. Deploy Infrastructure Components

```bash
cd infrastructure/kubernetes

# Create namespace
kubectl create namespace customer-success

# Deploy PostgreSQL
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install postgres bitnami/postgresql \
  --namespace customer-success \
  --values postgres-values.yaml

# Deploy Redis
helm install redis bitnami/redis \
  --namespace customer-success \
  --values redis-values.yaml

# Deploy Airflow
helm repo add apache-airflow https://airflow.apache.org
helm install airflow apache-airflow/airflow \
  --namespace customer-success \
  --values airflow-values.yaml
```

#### 3. Deploy Application Services

```bash
# Apply ConfigMaps and Secrets
kubectl apply -f configmaps/ -n customer-success
kubectl apply -f secrets/ -n customer-success

# Deploy backend services
kubectl apply -f backend/ -n customer-success

# Deploy frontend
kubectl apply -f frontend/ -n customer-success

# Deploy ingress
kubectl apply -f ingress/ -n customer-success
```

#### 4. Verify Deployment

```bash
# Check pod status
kubectl get pods -n customer-success

# Check services
kubectl get services -n customer-success

# Check ingress
kubectl get ingress -n customer-success

# View logs
kubectl logs -f deployment/cs-copilot-backend -n customer-success
```

### Option 2: Docker Compose (Production)

#### 1. Production Docker Compose

```bash
# Use production docker-compose file
docker-compose -f docker-compose.prod.yml up -d

# Monitor services
docker-compose -f docker-compose.prod.yml logs -f
```

### Option 3: Cloud Provider Specific

#### AWS Deployment

1. **EKS Cluster Setup**
```bash
# Create EKS cluster
eksctl create cluster --name cs-copilot --region us-west-2 --nodegroup-name standard-workers --node-type t3.medium --nodes 3

# Configure kubectl
aws eks update-kubeconfig --region us-west-2 --name cs-copilot
```

2. **RDS Database**
```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier cs-copilot-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 13.7 \
  --master-username csuser \
  --master-user-password your-password \
  --allocated-storage 20
```

3. **ElastiCache Redis**
```bash
# Create Redis cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id cs-copilot-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1
```

## 🔍 Monitoring & Observability

### Application Monitoring

#### Prometheus Configuration
```yaml
# infrastructure/monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'cs-copilot-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    
  - job_name: 'cs-copilot-postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
```

#### Grafana Dashboards
- **Application Performance**: API response times, error rates
- **Business Metrics**: Alert accuracy, customer health trends
- **Infrastructure**: CPU, memory, disk usage
- **ML Models**: Prediction accuracy, model drift

### Logging Configuration

#### Structured Logging (Backend)
```python
# backend/app/core/logging.py
import structlog

logger = structlog.get_logger()

# Usage in services
logger.info("Alert generated", 
           customer_id=customer.id, 
           alert_type="churn_risk",
           risk_score=0.85)
```

#### Log Aggregation
- **ELK Stack**: Elasticsearch + Logstash + Kibana
- **Cloud Solutions**: CloudWatch, Google Cloud Logging
- **Alternative**: Loki + Grafana

## 🔒 Security Hardening

### 1. Database Security
```sql
-- Create read-only user for analytics
CREATE USER analytics_user WITH PASSWORD 'secure_password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_user;

-- Enable SSL connections
ALTER SYSTEM SET ssl = on;
```

### 2. API Security
```python
# backend/app/core/security.py
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Token verification logic
    pass
```

### 3. Container Security
```dockerfile
# Use non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

USER appuser
```

### 4. Network Security
```yaml
# kubernetes/network-policies/backend-network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-network-policy
spec:
  podSelector:
    matchLabels:
      app: cs-copilot-backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: cs-copilot-frontend
    ports:
    - protocol: TCP
      port: 8000
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Connection Issues
```bash
# Check database connectivity
docker-compose exec postgres psql -U cs_user -d customer_success -c "SELECT 1;"

# Check database logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

#### 2. Redis Connection Issues
```bash
# Test Redis connectivity
docker-compose exec redis redis-cli ping

# Check Redis logs
docker-compose logs redis

# Clear Redis cache
docker-compose exec redis redis-cli FLUSHALL
```

#### 3. Airflow DAG Issues
```bash
# Check DAG status
docker-compose exec airflow-webserver airflow dags list

# Test DAG
docker-compose exec airflow-webserver airflow dags test customer_data_pipeline 2024-01-01

# Check task logs
docker-compose exec airflow-webserver airflow tasks logs customer_data_pipeline extract_crm_data 2024-01-01
```

#### 4. Frontend Build Issues
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check for TypeScript errors
npm run type-check
```

### Performance Tuning

#### Database Optimization
```sql
-- Add indexes for common queries
CREATE INDEX CONCURRENTLY idx_alerts_customer_severity ON alerts(customer_id, severity) WHERE status = 'open';

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM alerts WHERE customer_id = 'uuid' AND status = 'open';

-- Update table statistics
ANALYZE customers;
ANALYZE alerts;
```

#### API Performance
```python
# backend/app/core/cache.py
from functools import wraps
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiration=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            cached = redis_client.get(cache_key)
            
            if cached:
                return json.loads(cached)
            
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator
```

## 📊 Health Checks

### Service Health Endpoints

#### Backend Health Check
```python
# backend/app/api/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
import redis

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    checks = {}
    
    # Database check
    try:
        db.execute("SELECT 1")
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"
    
    # Redis check
    try:
        r = redis.Redis(host='localhost', port=6379)
        r.ping()
        checks["redis"] = "healthy"
    except Exception as e:
        checks["redis"] = f"unhealthy: {str(e)}"
    
    return {"status": "ok", "checks": checks}
```

### Kubernetes Health Checks
```yaml
# kubernetes/backend/deployment.yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

## 🔄 Backup and Recovery

### Database Backup
```bash
# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="customer_success"

# Create backup
pg_dump -h localhost -U cs_user -d $DB_NAME > "$BACKUP_DIR/backup_$TIMESTAMP.sql"

# Compress backup
gzip "$BACKUP_DIR/backup_$TIMESTAMP.sql"

# Remove backups older than 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
```

### Disaster Recovery
```bash
# Restore from backup
gunzip backup_20240101_120000.sql.gz
psql -h localhost -U cs_user -d customer_success_new < backup_20240101_120000.sql
```

This deployment guide provides comprehensive instructions for setting up the Customer Success Copilot in various environments, from local development to production Kubernetes clusters. 