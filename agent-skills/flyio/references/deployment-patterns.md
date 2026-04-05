# Common Deployment Patterns on Fly.io

Architectural patterns and best practices for deploying on Fly.io.

## Pattern 1: Simple Web Application

**Use case:** Single web app, low to moderate traffic, cost-conscious

```toml
app = "simple-web-app"
primary_region = "atl"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true      # Stop when idle
  auto_start_machines = true      # Wake on request
  min_machines_running = 0        # Zero cost when idle
```

**Characteristics:**
- Single region deployment
- Auto-scaling to zero for cost savings
- Quick wake-up on incoming requests
- Ideal for side projects, demos, low-traffic apps

## Pattern 2: High-Availability Web App

**Use case:** Production app requiring 99.9% uptime

```toml
app = "production-app"
primary_region = "atl"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = false
  min_machines_running = 2         # Always 2 machines minimum
```

```bash
# Deploy in multiple regions
fly scale count 2 --region atl,ord
```

**Characteristics:**
- Multi-region for redundancy (2+ regions)
- Minimum 2 machines always running
- Anycast routing to nearest region
- Zero-downtime deployments with rolling strategy

## Pattern 3: Web App + Background Workers

**Use case:** App with async job processing (emails, data processing, etc.)

```toml
app = "app-with-workers"
primary_region = "atl"

[processes]
  web = "gunicorn main:app"
  worker = "celery -A tasks worker"

[[http_service]]
  processes = ["web"]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

# Workers don't stop - always processing
[[services]]
  processes = ["worker"]
```

```bash
# Scale web and workers independently
fly scale count web=2 worker=3
fly scale memory 1024 --process worker  # More memory for workers
```

**Characteristics:**
- Separate web and worker processes
- Web scales down, workers stay running
- Independent scaling and resource allocation
- Requires message queue (Redis, RabbitMQ)

## Pattern 4: Multi-Region with Database

**Use case:** Global application with data persistence

```bash
# Create Postgres cluster
fly postgres create --name myapp-db --region atl

# Attach to app
fly postgres attach myapp-db

# Create read replicas in other regions
fly postgres create --name myapp-db-replica --region ord --fork-from myapp-db
```

```toml
app = "global-app"
primary_region = "atl"

[env]
  DATABASE_URL = ""  # Set by fly postgres attach

[http_service]
  internal_port = 8080
  force_https = true
  min_machines_running = 1
```

```bash
# Deploy app to multiple regions
fly scale count 3 --region atl,ord,lhr
```

**Characteristics:**
- Primary database in one region
- Read replicas for global reads
- App instances in multiple regions
- Fly-replay for writes to primary region

## Pattern 5: Static Site with Dynamic API

**Use case:** React/Next.js frontend + Python/Node backend

**Option A: Separate apps**
```bash
# Frontend app
cd frontend
fly launch --name myapp-frontend

# Backend API
cd ../backend
fly launch --name myapp-api
```

**Option B: Single app with process groups**
```toml
[processes]
  web = "node server.js"          # Serves static files
  api = "gunicorn api:app"        # API endpoints

[[http_service]]
  processes = ["web"]
  internal_port = 3000
  
[[http_service]]
  processes = ["api"]
  internal_port = 8080
```

## Pattern 6: Scheduled Jobs / Cron

**Use case:** Periodic data processing, backups, reports

**Option A: Using Supercronic**
```dockerfile
FROM python:3.11-slim

# Install supercronic
RUN curl -fsSL https://github.com/aptible/supercronic/releases/latest/download/supercronic-linux-amd64 \
    -o /usr/local/bin/supercronic \
    && chmod +x /usr/local/bin/supercronic

COPY crontab /etc/crontab
CMD ["supercronic", "/etc/crontab"]
```

**crontab**
```
# Run daily at 2 AM UTC
0 2 * * * /app/scripts/daily_report.py
```

**Option B: Using Fly Machines API**
```python
# GitHub Actions workflow or external scheduler
import requests
import os

def trigger_job():
    response = requests.post(
        f"https://api.machines.dev/v1/apps/{APP_NAME}/machines",
        headers={"Authorization": f"Bearer {FLY_API_TOKEN}"},
        json={
            "config": {
                "image": f"{APP_NAME}:latest",
                "auto_destroy": True,
                "env": {"JOB_TYPE": "daily_report"}
            }
        }
    )
    return response.json()
```

## Pattern 7: Data Pipeline / ETL

**Use case:** dbt, Airflow, data transformations

```toml
app = "data-pipeline"
primary_region = "atl"

[build]
  dockerfile = "Dockerfile"

[[mounts]]
  source = "data_volume"
  destination = "/data"

[[vm]]
  size = "shared-cpu-4x"
  memory = "2048mb"
```

```bash
# Create volume for persistent data
fly volumes create data_volume --size 10

# Run on-demand via API or schedule
```

**Characteristics:**
- Larger VMs for compute-intensive tasks
- Persistent volumes for data
- Run on-demand or scheduled
- Auto-destroy after completion

## Pattern 8: Microservices Architecture

**Use case:** Multiple services communicating over private network

```bash
# Service 1: User service
fly apps create user-service
fly deploy --app user-service

# Service 2: Order service  
fly apps create order-service
fly deploy --app order-service

# Service 3: Payment service
fly apps create payment-service
fly deploy --app payment-service
```

**Internal communication:**
```python
# Services communicate via .internal domain
import requests

# From user-service to order-service
response = requests.get("http://order-service.internal:8080/orders")
```

**Characteristics:**
- Each service as separate Fly app
- Private networking via `.internal` domains
- Independent scaling and deployment
- Shared resources via Fly Postgres, Redis

## Pattern 9: GPU Workloads (AI/ML)

**Use case:** Machine learning inference, image processing

```toml
app = "ml-inference"
primary_region = "ord"  # GPU regions: ord, iad

[[vm]]
  size = "a10"
  gpu_kind = "a10"
  memory = "32gb"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
```

```bash
# Deploy with GPU
fly deploy --vm-gpu-kind a10
```

**Characteristics:**
- GPU-enabled machines for ML workloads
- Auto-scaling for cost efficiency
- Fast cold starts for inference
- Available GPU types: a10, l40s, a100-40gb, a100-80gb

## Pattern 10: Development/Staging/Production

**Use case:** Multiple environments with different configurations

```bash
# Production
fly apps create myapp-prod
fly secrets set --app myapp-prod ENV=production DATABASE_URL=...

# Staging
fly apps create myapp-staging
fly secrets set --app myapp-staging ENV=staging DATABASE_URL=...

# Deploy to specific environment
fly deploy --app myapp-staging
fly deploy --app myapp-prod
```

**fly.staging.toml**
```toml
app = "myapp-staging"
primary_region = "atl"

[http_service]
  auto_stop_machines = true
  min_machines_running = 0
```

**fly.production.toml**
```toml
app = "myapp-prod"
primary_region = "atl"

[http_service]
  auto_stop_machines = false
  min_machines_running = 2
```

```bash
# Deploy with specific config
fly deploy --config fly.staging.toml
fly deploy --config fly.production.toml
```

## Deployment Strategy Comparison

| Strategy | Use Case | Downtime | Risk |
|----------|----------|----------|------|
| `rolling` | Default, most scenarios | Minimal | Low |
| `immediate` | Quick updates, maintenance windows | Yes | Medium |
| `canary` | High-traffic apps, risk mitigation | None | Very Low |
| `bluegreen` | Zero-downtime critical apps | None | Low |

## Cost Optimization Patterns

### Pattern: Auto-scaling for variable traffic
```toml
[http_service]
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
```

### Pattern: Right-sized VMs
```bash
# Start small
fly scale vm shared-cpu-1x

# Scale up as needed
fly scale vm shared-cpu-2x
fly scale memory 1024
```

### Pattern: Regional optimization
```bash
# Deploy only in regions with users
fly regions add atl ord
fly regions remove sjc lax lhr
```

## Monitoring and Observability

### Export metrics
```toml
[metrics]
  port = 9090
  path = "/metrics"
```

### Structured logging
```python
import logging
import json

logger = logging.getLogger(__name__)
logger.info(json.dumps({
    "event": "request_processed",
    "user_id": user_id,
    "duration_ms": duration
}))
```

### Health checks
```toml
[[http_service.checks]]
  grace_period = "10s"
  interval = "30s"
  method = "GET"
  path = "/health"
```

## Security Best Practices

1. **Use secrets for sensitive data**
   ```bash
   fly secrets set API_KEY=xxx DATABASE_PASSWORD=yyy
   ```

2. **Enable private networking for internal services**
   ```bash
   # Services communicate via .internal domain
   ```

3. **Force HTTPS**
   ```toml
   [http_service]
     force_https = true
   ```

4. **Implement rate limiting and authentication**
5. **Regular security updates via Dockerfile rebuilds**
6. **Use volumes for persistent data, not ephemeral storage**
