# 🚀 Production Deployment Guide

Complete guide for deploying MLB Statistics Analysis System to production.

## Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Platforms](#cloud-platforms)
4. [Monitoring & Observability](#monitoring--observability)
5. [Security Hardening](#security-hardening)
6. [Performance Optimization](#performance-optimization)
7. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

### ✅ Code Quality
- [ ] All tests passing (`python run_tests.py`)
- [ ] Security scan clean (`python run_security_check.py`)
- [ ] No TODO/FIXME in production code
- [ ] Code reviewed and approved
- [ ] Version tagged in git (`git tag v1.0.0`)

### ✅ Configuration
- [ ] `.env` file configured for production
- [ ] `ENVIRONMENT=production` set
- [ ] `LOG_LEVEL=WARNING` or `ERROR` (not DEBUG)
- [ ] API keys secured (not in code)
- [ ] Secrets management configured

### ✅ Dependencies
- [ ] All dependencies updated (`pip list --outdated`)
- [ ] No known vulnerabilities (`pip-audit`)
- [ ] `requirements.lock` generated

### ✅ Documentation
- [ ] README.md up to date
- [ ] API documentation complete
- [ ] Runbook for operations team
- [ ] Incident response plan

---

## Docker Deployment

### Quick Start

```bash
# 1. Build and run with Docker Compose
docker-compose up -d

# 2. Check status
docker-compose ps

# 3. View logs
docker-compose logs -f mlb-stats-web

# 4. Access app
open http://localhost:8501
```

### Production Docker Build

```bash
# Build optimized production image
docker build -t mlb-stats:1.0.0 .

# Run container
docker run -d \
  --name mlb-stats-web \
  -p 8501:8501 \
  -e ENVIRONMENT=production \
  -e LOG_LEVEL=WARNING \
  -v mlb-cache:/app/data/cache \
  mlb-stats:1.0.0

# Health check
docker exec mlb-stats-web curl http://localhost:8501/_stcore/health
```

### Docker Compose for Production

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  mlb-stats-web:
    image: mlb-stats:1.0.0
    ports:
      - "8501:8501"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=WARNING
      - SENTRY_DSN=${SENTRY_DSN}
    volumes:
      - cache-data:/app/data/cache
      - ai-cache-data:/app/data/ai_code_cache
    restart: always
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  cache-data:
  ai-cache-data:
```

---

## Cloud Platforms

### AWS (Elastic Container Service)

#### Option 1: AWS ECS with Fargate

```bash
# 1. Push to ECR
aws ecr create-repository --repository-name mlb-stats
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

docker tag mlb-stats:1.0.0 YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/mlb-stats:1.0.0
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/mlb-stats:1.0.0

# 2. Create ECS task definition (see task-definition.json)
aws ecs register-task-definition --cli-input-json file://task-definition.json

# 3. Create service
aws ecs create-service \
  --cluster mlb-cluster \
  --service-name mlb-stats-service \
  --task-definition mlb-stats:1 \
  --desired-count 2 \
  --launch-type FARGATE
```

**task-definition.json:**
```json
{
  "family": "mlb-stats",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "mlb-stats-web",
      "image": "YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/mlb-stats:1.0.0",
      "portMappings": [
        {
          "containerPort": 8501,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "ENVIRONMENT", "value": "production"},
        {"name": "LOG_LEVEL", "value": "WARNING"}
      ],
      "secrets": [
        {
          "name": "SENTRY_DSN",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:mlb-stats/sentry-dsn"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/mlb-stats",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### Option 2: AWS App Runner (Simplest)

```bash
# Create apprunner.yaml
cat > apprunner.yaml <<EOF
version: 1.0
runtime: python3
build:
  commands:
    build:
      - pip install -r requirements.txt -r requirements_web.txt
run:
  runtime-version: 3.11
  command: streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
  network:
    port: 8501
  env:
    - name: ENVIRONMENT
      value: production
EOF

# Deploy with AWS CLI
aws apprunner create-service \
  --service-name mlb-stats \
  --source-configuration file://apprunner-source.json
```

### Google Cloud Platform (Cloud Run)

```bash
# 1. Build and push to GCR
gcloud builds submit --tag gcr.io/YOUR_PROJECT/mlb-stats:1.0.0

# 2. Deploy to Cloud Run
gcloud run deploy mlb-stats \
  --image gcr.io/YOUR_PROJECT/mlb-stats:1.0.0 \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=production,LOG_LEVEL=WARNING \
  --memory 1Gi \
  --cpu 1 \
  --port 8501
```

### Azure (Container Instances)

```bash
# 1. Push to ACR
az acr create --resource-group mlb-stats-rg --name mlbstatsacr --sku Basic
az acr login --name mlbstatsacr
docker tag mlb-stats:1.0.0 mlbstatsacr.azurecr.io/mlb-stats:1.0.0
docker push mlbstatsacr.azurecr.io/mlb-stats:1.0.0

# 2. Deploy to ACI
az container create \
  --resource-group mlb-stats-rg \
  --name mlb-stats-web \
  --image mlbstatsacr.azurecr.io/mlb-stats:1.0.0 \
  --cpu 1 --memory 1 \
  --ports 8501 \
  --environment-variables ENVIRONMENT=production LOG_LEVEL=WARNING
```

### Streamlit Cloud (Easiest - FREE)

See [DEPLOY_NOW.md](../DEPLOY_NOW.md) for step-by-step guide.

---

## Monitoring & Observability

### Sentry Setup (Error Tracking)

```bash
# 1. Install Sentry SDK
pip install sentry-sdk

# 2. Get DSN from sentry.io
# Sign up at https://sentry.io
# Create new project → Get DSN

# 3. Configure in .env
SENTRY_DSN=https://your_key@sentry.io/your_project

# 4. Initialize in streamlit_app.py
from src.monitoring import init_monitoring
init_monitoring()
```

### Application Logs

**CloudWatch (AWS):**
```bash
# View logs
aws logs tail /ecs/mlb-stats --follow

# Create metric filter
aws logs put-metric-filter \
  --log-group-name /ecs/mlb-stats \
  --filter-name ErrorCount \
  --filter-pattern "ERROR" \
  --metric-transformations \
    metricName=ErrorCount,metricNamespace=MLBStats,metricValue=1
```

**Cloud Logging (GCP):**
```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=mlb-stats" --limit 50 --format json
```

### Uptime Monitoring

**AWS CloudWatch Synthetics:**
```python
# canary.py
def handler(event, context):
    import requests
    response = requests.get('https://your-app.com/_stcore/health', timeout=10)
    assert response.status_code == 200
    return {'statusCode': 200}
```

**UptimeRobot (FREE):**
1. Sign up at uptimerobot.com
2. Add HTTP(s) monitor
3. URL: `https://your-app.com/_stcore/health`
4. Interval: 5 minutes
5. Alert contacts: your email

---

## Security Hardening

### 1. HTTPS/SSL

**AWS ALB with ACM Certificate:**
```bash
# Request certificate
aws acm request-certificate \
  --domain-name mlbstats.yourdomain.com \
  --validation-method DNS

# Create ALB with HTTPS listener
aws elbv2 create-load-balancer \
  --name mlb-stats-alb \
  --subnets subnet-xxx subnet-yyy \
  --security-groups sg-xxx

aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:... \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:...
```

### 2. Environment Secrets

**AWS Secrets Manager:**
```bash
# Store secrets
aws secretsmanager create-secret \
  --name mlb-stats/sentry-dsn \
  --secret-string "your-sentry-dsn"

# Grant ECS task access
aws iam attach-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite
```

### 3. Rate Limiting

**Add to streamlit_app.py:**
```python
from functools import wraps
from datetime import datetime, timedelta

request_counts = {}

def rate_limit(max_requests=10, window_seconds=60):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = datetime.now()
            client_id = st.session_state.get('client_id', 'default')
            
            if client_id not in request_counts:
                request_counts[client_id] = []
            
            # Remove old requests
            request_counts[client_id] = [
                req_time for req_time in request_counts[client_id]
                if now - req_time < timedelta(seconds=window_seconds)
            ]
            
            if len(request_counts[client_id]) >= max_requests:
                st.error(f"Rate limit exceeded. Try again in {window_seconds} seconds.")
                return None
            
            request_counts[client_id].append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(max_requests=10, window_seconds=60)
def handle_query(query):
    # Your query handling code
    pass
```

### 4. Security Headers

**Add to Dockerfile:**
```dockerfile
# Install nginx for reverse proxy
FROM nginx:alpine
COPY nginx.conf /etc/nginx/nginx.conf
```

**nginx.conf:**
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self' 'unsafe-inline' 'unsafe-eval'; img-src 'self' data:;" always;
```

---

## Performance Optimization

### 1. Caching Strategy

```python
# Aggressive caching for production
CACHE_TTL_HOURS=168  # 7 days instead of 24
AI_CACHE_TTL_DAYS=90  # 3 months instead of 30
```

### 2. Connection Pooling

```python
# In data_fetcher.py
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(total=3, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=20)
session.mount('http://', adapter)
session.mount('https://', adapter)
```

### 3. Resource Limits

**Docker:**
```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 512M
```

### 4. CDN for Static Assets

Use CloudFront (AWS) or Cloud CDN (GCP) for static files.

---

## Troubleshooting

### Common Issues

#### 1. Container Won't Start

```bash
# Check logs
docker logs mlb-stats-web

# Common fixes:
# - Missing environment variables
# - Permission issues
# - Port already in use
docker run -e ENVIRONMENT=production ...
```

#### 2. High Memory Usage

```bash
# Monitor memory
docker stats mlb-stats-web

# Solutions:
# - Increase memory limit
# - Clear cache more frequently
# - Optimize data structures
```

#### 3. Slow Queries

```bash
# Enable timing logs
LOG_LEVEL=DEBUG
ENABLE_TIMING_LOGS=true

# Check cache hit rate in UI
# Clear old cache: docker exec mlb-stats-web rm -rf /app/data/cache/*
```

#### 4. API Rate Limiting

```bash
# Check MLB API response headers
# Implement exponential backoff (already done)
# Increase cache TTL
```

### Health Check Endpoints

```bash
# Streamlit health
curl http://localhost:8501/_stcore/health

# Custom health endpoint (add to streamlit_app.py)
curl http://localhost:8501/api/health
```

### Log Analysis

```bash
# Search for errors
docker logs mlb-stats-web 2>&1 | grep ERROR

# Count requests per minute
docker logs mlb-stats-web 2>&1 | grep "API Request" | tail -100 | wc -l

# Find slow queries
docker logs mlb-stats-web 2>&1 | grep "took" | sort -k 5 -n
```

---

## Production Checklist

### Before Deployment
- [ ] All tests passing
- [ ] Security scan clean
- [ ] Performance benchmarks met
- [ ] Monitoring configured
- [ ] Backups configured
- [ ] Rollback plan documented

### After Deployment
- [ ] Health checks passing
- [ ] Logs reviewed
- [ ] Metrics baseline established
- [ ] Alerts configured
- [ ] Documentation updated
- [ ] Team notified

### Weekly Maintenance
- [ ] Review error logs
- [ ] Check dependency updates
- [ ] Monitor resource usage
- [ ] Review Sentry errors
- [ ] Clear old cache if needed

---

## Support

- **Documentation:** See `docs/` folder
- **Issues:** GitHub Issues
- **Security:** See `SECURITY.md`
- **Monitoring:** Sentry dashboard

---

## Next Steps

1. ✅ Complete pre-deployment checklist
2. 🐳 Build and test Docker image locally
3. ☁️ Choose cloud platform
4. 📊 Configure monitoring
5. 🔒 Harden security
6. 🚀 Deploy to production
7. 📈 Monitor and optimize

**Your app is production-ready!** 🎉
