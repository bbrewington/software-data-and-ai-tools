# Python Deployment Examples for Fly.io

Framework-specific deployment patterns and best practices.

## FastAPI Application

### Project Structure
```
fastapi-app/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── routers/
├── requirements.txt
├── Dockerfile
└── fly.toml
```

### main.py
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from Fly.io"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

### requirements.txt
```
fastapi[standard]==0.115.0
uvicorn[standard]==0.32.0
```

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### fly.toml
```toml
app = "my-fastapi-app"
primary_region = "atl"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8080"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[http_service.checks]]
  grace_period = "10s"
  interval = "30s"
  method = "GET"
  path = "/health"
  timeout = "5s"
```

## Flask Application with Gunicorn

### Project Structure
```
flask-app/
├── app/
│   ├── __init__.py
│   └── routes.py
├── wsgi.py
├── requirements.txt
├── Dockerfile
└── fly.toml
```

### wsgi.py
```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
```

### app/__init__.py
```python
from flask import Flask

def create_app():
    app = Flask(__name__)
    
    @app.route("/")
    def index():
        return {"message": "Hello from Fly.io"}
    
    @app.route("/health")
    def health():
        return {"status": "healthy"}
    
    return app
```

### requirements.txt
```
Flask==3.0.0
gunicorn==21.2.0
```

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "wsgi:app"]
```

## Django Application

### Project Structure
```
django-app/
├── myproject/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
├── Dockerfile
└── fly.toml
```

### settings.py additions
```python
import os

# Fly.io specific settings
ALLOWED_HOSTS = ['.fly.dev', 'localhost', '127.0.0.1']

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Database - Use Fly Postgres
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DATABASE_NAME', 'myapp'),
        'USER': os.environ.get('DATABASE_USER', 'postgres'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', ''),
        'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
        'PORT': os.environ.get('DATABASE_PORT', '5432'),
    }
}
```

### requirements.txt
```
Django==5.0
gunicorn==21.2.0
psycopg2-binary==2.9.9
whitenoise==6.6.0
```

### Dockerfile
```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "myproject.wsgi:application"]
```

### fly.toml
```toml
app = "django-app"
primary_region = "atl"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8080"
  DJANGO_SETTINGS_MODULE = "myproject.settings"

[deploy]
  release_command = "python manage.py migrate --noinput"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true

[[http_service.checks]]
  grace_period = "10s"
  interval = "30s"
  method = "GET"
  path = "/health"
```

## Data Engineering / dbt Project

### Project Structure
```
dbt-pipeline/
├── dbt_project.yml
├── profiles.yml
├── models/
├── scripts/
│   └── run_dbt.sh
├── requirements.txt
├── Dockerfile
└── fly.toml
```

### run_dbt.sh
```bash
#!/bin/bash
set -e

echo "Running dbt..."
dbt deps
dbt run --profiles-dir /app
dbt test --profiles-dir /app

echo "dbt run completed successfully"
```

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dbt and dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make script executable
RUN chmod +x scripts/run_dbt.sh

# For scheduled runs, use cron or Fly Machines API
CMD ["./scripts/run_dbt.sh"]
```

### fly.toml (for scheduled execution)
```toml
app = "dbt-pipeline"
primary_region = "atl"

[build]
  dockerfile = "Dockerfile"

[env]
  DBT_PROFILES_DIR = "/app"

# Run as a one-off machine (trigger via API or scheduler)
[[vm]]
  size = "shared-cpu-2x"
  memory = "1024mb"
```

### Triggering via Fly Machines API
```python
import requests
import os

FLY_API_TOKEN = os.getenv("FLY_API_TOKEN")
APP_NAME = "dbt-pipeline"

response = requests.post(
    f"https://api.machines.dev/v1/apps/{APP_NAME}/machines",
    headers={"Authorization": f"Bearer {FLY_API_TOKEN}"},
    json={
        "config": {
            "image": f"{APP_NAME}:latest",
            "auto_destroy": True,  # Destroy after completion
        }
    }
)
```

## Python App with Celery Worker

### Project Structure
```
celery-app/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── tasks.py
├── requirements.txt
├── Dockerfile
└── fly.toml
```

### tasks.py
```python
from celery import Celery

app = Celery('tasks', broker='redis://redis-app.internal:6379')

@app.task
def process_data(data):
    # Long-running task
    return {"status": "processed"}
```

### requirements.txt
```
fastapi[standard]==0.115.0
celery==5.3.4
redis==5.0.1
```

### fly.toml (Multi-process)
```toml
app = "celery-app"
primary_region = "atl"

[build]
  dockerfile = "Dockerfile"

[processes]
  web = "uvicorn app.main:app --host 0.0.0.0 --port 8080"
  worker = "celery -A app.tasks worker --loglevel=info"

[[http_service]]
  processes = ["web"]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true

[[vm]]
  size = "shared-cpu-1x"
  memory = "512mb"
```

### Deployment
```bash
# Create Redis
fly redis create

# Deploy app with both web and worker processes
fly deploy

# Scale workers independently
fly scale count web=2 worker=3
```

## Environment-Specific Configurations

### Using .env for local development
```python
# app/config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./local.db")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Setting secrets on Fly.io
```bash
fly secrets set DATABASE_URL=postgres://user:pass@host/db
fly secrets set REDIS_URL=redis://redis-app.internal:6379
fly secrets set API_KEY=your-secret-key
```

## Best Practices

1. **Always include health checks** - Helps Fly.io know when your app is ready
2. **Use gunicorn/uvicorn** - Production WSGI/ASGI servers, not Flask dev server
3. **Set appropriate timeouts** - `kill_timeout` should match your app's shutdown time
4. **Leverage auto-scaling** - `auto_stop_machines` saves costs for low-traffic apps
5. **Multi-region for high availability** - Deploy in 2+ regions for redundancy
6. **Use volumes for persistent data** - Databases, file uploads, etc.
7. **Monitor with metrics** - Expose Prometheus metrics endpoint
8. **Implement graceful shutdown** - Handle SIGTERM/SIGINT properly
