---
name: flyio
description: Deploy and manage applications on Fly.io platform with Docker containers and Fly Machines. Use when helping users deploy apps to Fly.io, create or modify fly.toml configuration files, set up Dockerfiles for deployment, manage Fly.io resources (databases, volumes, secrets), debug deployment issues, configure multi-region deployments, or work with Fly Launch commands (fly launch, fly deploy). Particularly relevant for Python/Node.js/Rails/Django apps, CI/CD with GitHub Actions, and global edge deployment scenarios.
---

# Fly.io Deployment

Deploy applications globally using Fly.io's platform of hardware-virtualized containers (Fly Machines) with instant launch capabilities and edge networking.

## Quick Start

**Common workflows:**
- `fly launch` - Initialize and deploy new app (auto-generates fly.toml and Dockerfile)
- `fly deploy` - Deploy changes to existing app
- `fly status` - Check app health and machine status
- `fly logs` - View application logs
- `fly ssh console` - SSH into running machine

**Prerequisites:**
- flyctl CLI installed ([install instructions](https://fly.io/docs/flyctl/install/))
- Authenticated account: `fly auth login`

## Creating a New App

### 1. Initialize with fly launch

From your project directory:

```bash
fly launch
```

This command:
- Detects your framework (Python, Node.js, Rails, Django, etc.)
- Generates a Dockerfile (if not present)
- Creates fly.toml configuration
- Prompts for app name, region, and optional resources (Postgres, Redis)
- Optionally deploys immediately

**Customization flags:**
- `--no-deploy` - Configure without deploying
- `--name <app-name>` - Specify app name
- `--region <code>` - Set primary region (e.g., `atl` for Atlanta)
- `--org <org-name>` - Deploy to specific organization
- `--image <image>` - Use existing Docker image

### 2. Framework-Specific Guidance

**Python (Flask/FastAPI/Django):**
- Automatically detects if you have `requirements.txt` or `pyproject.toml`
- Creates Dockerfile with appropriate Python version
- Configures gunicorn or uvicorn as production server

**Node.js:**
- Detects `package.json`
- Configures proper build and start commands
- Handles npm/yarn/pnpm automatically

**For data engineering/dbt projects:**
- Use custom Dockerfile
- Consider scheduling with Fly Machines API
- Mount volumes for persistent data

## fly.toml Configuration

The `fly.toml` file controls app deployment. Key sections:

```toml
# App metadata
app = "my-app"
primary_region = "atl"

# Build configuration
[build]
  dockerfile = "Dockerfile"  # or use [build.image = "..."]

# Environment variables (non-sensitive)
[env]
  PORT = "8080"
  ENVIRONMENT = "production"

# HTTP service configuration
[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

# Health checks
[[http_service.checks]]
  grace_period = "10s"
  interval = "30s"
  method = "GET"
  timeout = "5s"
  path = "/health"

# Process groups (for multi-process apps)
[processes]
  web = "gunicorn main:app"
  worker = "celery -A tasks worker"

# Volume mounts (persistent storage)
[[mounts]]
  source = "data_volume"
  destination = "/data"

# VM resources
[[vm]]
  size = "shared-cpu-1x"
  memory = "256mb"
```

**Common configurations:**

**Auto-scaling for cost optimization:**
```toml
[http_service]
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0  # Stop all when idle
```

**Multiple regions:**
```bash
fly scale count 2 --region atl,ord
```

**Secrets management:**
```bash
fly secrets set API_KEY=xxx DATABASE_URL=yyy
fly secrets list
```

## Deployment Strategies

Specify strategy with `fly deploy --strategy <type>`:

- `rolling` (default) - Update machines sequentially
- `immediate` - Update all at once (brief downtime)
- `canary` - Deploy to one machine, verify, then roll out
- `bluegreen` - Deploy alongside existing, switch traffic when ready

## Common Tasks

### Deploy Changes
```bash
fly deploy
```

### View Logs
```bash
fly logs                    # Live logs
fly logs --region atl       # Specific region
```

### Scale Resources
```bash
fly scale count 3                          # Set machine count
fly scale memory 512                       # Increase RAM (MB)
fly scale vm shared-cpu-2x                 # Change VM size
fly scale count 2 --region atl,ord         # Multi-region
```

### Manage Volumes
```bash
fly volumes create data_volume --size 1    # Create 1GB volume
fly volumes list
```

### Database Setup
```bash
fly postgres create --name myapp-db        # Postgres
fly redis create                           # Redis (via Upstash)
```

### SSH Access
```bash
fly ssh console                            # Interactive shell
fly ssh console -C "python manage.py migrate"  # Run command
```

### Rollback
```bash
fly releases                               # List releases
fly deploy --image <app>:<release>         # Deploy specific release
```

## Python Application Pattern

**Typical structure:**

```
project/
├── app/
│   ├── __init__.py
│   └── main.py
├── requirements.txt
├── Dockerfile          # Generated by fly launch
├── fly.toml           # Generated by fly launch
└── .dockerignore
```

**Minimal Dockerfile for Python (if customizing):**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "app.main:app", "--bind", "0.0.0.0:8080"]
```

## GitHub Actions Integration

**Example workflow for automated deployments:**

```yaml
name: Deploy to Fly.io

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: superfly/flyctl-actions/setup-flyctl@master
      
      - run: flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

Generate token: `fly tokens create deploy`

## Multi-Process Apps (e.g., Web + Worker)

**In fly.toml:**

```toml
[processes]
  web = "gunicorn main:app"
  worker = "celery -A tasks worker"

# Different scaling per process
[[http_service]]
  processes = ["web"]
  internal_port = 8080

[[services]]
  processes = ["worker"]
  # No HTTP service for workers
```

**Deploy:**
```bash
fly deploy
fly scale count web=2 worker=1
```

## Debugging Common Issues

**Build failures:**
- Check Dockerfile syntax
- Verify dependencies in requirements.txt
- Review build logs: `fly logs --region atl`

**App won't start:**
- Verify `internal_port` matches your app's port
- Check health check path exists
- Review startup logs: `fly logs`

**Connection issues:**
- Verify public IP allocated: `fly ips list`
- Check firewall/security groups if using WireGuard
- Ensure health checks passing: `fly status`

**Performance issues:**
- Increase VM resources: `fly scale memory 1024`
- Add more regions: `fly regions add ord lax`
- Check machine utilization: `fly status`

## Resources

### references/
- `fly-toml-reference.md` - Complete fly.toml configuration options
- `deployment-patterns.md` - Common deployment architectures
- `python-examples.md` - Python-specific deployment examples

### assets/
- `fly.toml.template` - Starter templates for common app types
- `github-actions-workflow.yml` - CI/CD workflow template
