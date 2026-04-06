# fly.toml Configuration Reference

Complete reference for fly.toml configuration options based on Fly.io documentation.

## Basic Structure

```toml
app = "app-name"                    # Required: unique app name
primary_region = "atl"              # Primary deployment region
kill_signal = "SIGINT"              # Signal to send on shutdown
kill_timeout = "5s"                 # Grace period before forced shutdown
```

## Build Configuration

### Using Dockerfile
```toml
[build]
  dockerfile = "Dockerfile"
  ignorefile = ".dockerignore"
  args = { BUILD_ENV = "production" }
```

### Using Pre-built Image
```toml
[build]
  image = "ghcr.io/username/app:latest"
```

### Build Arguments
```toml
[build.args]
  NODE_VERSION = "18"
  PYTHON_VERSION = "3.11"
```

## Environment Variables

```toml
[env]
  PORT = "8080"
  ENVIRONMENT = "production"
  LOG_LEVEL = "info"
```

**Note:** Use `fly secrets set` for sensitive values (API keys, passwords)

## HTTP Service Configuration

### Basic HTTP Service
```toml
[http_service]
  internal_port = 8080              # Port app listens on
  force_https = true                # Redirect HTTP to HTTPS
  auto_stop_machines = true         # Stop when idle
  auto_start_machines = true        # Start on request
  min_machines_running = 0          # Minimum running machines
  processes = ["app"]               # Which processes this applies to
```

### Advanced HTTP Options
```toml
[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = "stop"       # or "suspend" for faster wake
  auto_start_machines = true
  min_machines_running = 1
  
  [http_service.concurrency]
    type = "requests"               # or "connections"
    hard_limit = 100
    soft_limit = 80
```

### TLS Configuration
```toml
[http_service.tls_options]
  alpn = ["h2", "http/1.1"]
  versions = ["TLSv1.2", "TLSv1.3"]
  default_self_signed = false
```

## Health Checks

```toml
[[http_service.checks]]
  grace_period = "10s"              # Time before first check
  interval = "30s"                  # Time between checks
  method = "GET"
  timeout = "5s"
  path = "/health"
  
  [http_service.checks.headers]
    Authorization = "Bearer xxx"
```

### Multiple Health Checks
```toml
[[http_service.checks]]
  grace_period = "5s"
  interval = "15s"
  method = "GET"
  path = "/health"

[[http_service.checks]]
  grace_period = "10s"
  interval = "60s"
  method = "GET"
  path = "/metrics"
```

## Process Groups

Define multiple processes within one app:

```toml
[processes]
  web = "gunicorn main:app --bind 0.0.0.0:8080"
  worker = "celery -A tasks worker --loglevel=info"
  scheduler = "celery -A tasks beat"
```

### Process-Specific Services
```toml
[[http_service]]
  processes = ["web"]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
```

## Volumes (Persistent Storage)

```toml
[[mounts]]
  source = "data"                   # Volume name
  destination = "/data"             # Mount path
  processes = ["app"]               # Optional: specific processes
```

### Creating Volumes
```bash
fly volumes create data --size 10  # 10GB volume
fly volumes list
```

## VM Configuration

```toml
[[vm]]
  size = "shared-cpu-1x"            # VM size
  memory = "256mb"                  # Or 512, 1024, 2048, etc.
  cpu_kind = "shared"               # or "performance"
  cpus = 1
```

### Available VM Sizes
- `shared-cpu-1x` - 1 shared CPU, 256MB RAM (default)
- `shared-cpu-2x` - 2 shared CPUs
- `shared-cpu-4x` - 4 shared CPUs
- `shared-cpu-8x` - 8 shared CPUs
- `performance-1x` - 1 dedicated CPU
- `performance-2x` - 2 dedicated CPUs

## Multi-Region Deployment

```toml
primary_region = "atl"
```

```bash
# Add regions via CLI
fly scale count 2 --region atl,ord,sjc
fly regions add lax iad
fly regions list
```

## Metrics

```toml
[metrics]
  port = 9091
  path = "/metrics"
```

### Process-Specific Metrics
```toml
[[metrics]]
  port = 9394
  path = "/metrics"
  processes = ["web"]

[[metrics]]
  port = 9113
  path = "/metrics"
  processes = ["worker"]
```

## Deploy Configuration

```toml
[deploy]
  release_command = "python manage.py migrate"
  strategy = "rolling"              # rolling, immediate, canary, bluegreen
```

## Experimental Features

```toml
[experimental]
  auto_rollback = true
  enable_consul = false
  private_network = true
```

## Swap Memory

Add virtual memory:

```toml
swap_size_mb = 512                  # Add 512MB swap
```

## Complete Example: Python Web App + Worker

```toml
app = "data-pipeline"
primary_region = "atl"
kill_signal = "SIGTERM"
kill_timeout = "30s"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8080"
  WORKER_CONCURRENCY = "4"

[processes]
  web = "gunicorn app:app --bind 0.0.0.0:8080 --workers 2"
  worker = "celery -A tasks worker --loglevel=info"

[[http_service]]
  processes = ["web"]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
  
  [http_service.concurrency]
    type = "requests"
    soft_limit = 80
    hard_limit = 100

[[http_service.checks]]
  grace_period = "10s"
  interval = "30s"
  method = "GET"
  timeout = "5s"
  path = "/health"

[[mounts]]
  source = "data_volume"
  destination = "/data"
  processes = ["worker"]

[[vm]]
  size = "shared-cpu-1x"
  memory = "512mb"

[deploy]
  release_command = "python manage.py migrate"
  strategy = "rolling"

[metrics]
  port = 9090
  path = "/metrics"
```

## Regional Codes Reference

Common regions:
- `atl` - Atlanta, Georgia (US East)
- `ord` - Chicago, Illinois (US Central)
- `sjc` - San Jose, California (US West)
- `lax` - Los Angeles, California (US West)
- `iad` - Ashburn, Virginia (US East)
- `lhr` - London (Europe)
- `ams` - Amsterdam (Europe)
- `fra` - Frankfurt (Europe)
- `nrt` - Tokyo (Asia)
- `syd` - Sydney (Australia)

Full list: `fly platform regions`
