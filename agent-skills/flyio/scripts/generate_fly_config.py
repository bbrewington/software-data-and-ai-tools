#!/usr/bin/env python3
"""
Generate a customized fly.toml configuration file based on user requirements.

Usage:
    python generate_fly_config.py --app my-app --region atl --output fly.toml
"""

import argparse
from typing import Optional


def generate_fly_toml(
    app_name: str,
    primary_region: str = "atl",
    internal_port: int = 8080,
    auto_scale: bool = True,
    min_machines: int = 0,
    vm_size: str = "shared-cpu-1x",
    vm_memory: str = "256mb",
    health_check_path: str = "/health",
    has_postgres: bool = False,
    has_redis: bool = False,
    has_volumes: bool = False,
    release_command: Optional[str] = None,
) -> str:
    """Generate a fly.toml configuration file."""
    
    config = f"""# Fly.io App Configuration
# Generated automatically - customize as needed

app = "{app_name}"
primary_region = "{primary_region}"

kill_signal = "SIGTERM"
kill_timeout = "30s"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "{internal_port}"

[http_service]
  internal_port = {internal_port}
  force_https = true
  auto_stop_machines = {str(auto_scale).lower()}
  auto_start_machines = {str(auto_scale).lower()}
  min_machines_running = {min_machines}

[[http_service.checks]]
  grace_period = "10s"
  interval = "30s"
  method = "GET"
  timeout = "5s"
  path = "{health_check_path}"

[[vm]]
  size = "{vm_size}"
  memory = "{vm_memory}"
"""

    if release_command:
        config += f"""
[deploy]
  release_command = "{release_command}"
  strategy = "rolling"
"""

    if has_volumes:
        config += """
[[mounts]]
  source = "data_volume"
  destination = "/data"
"""

    return config


def main():
    parser = argparse.ArgumentParser(
        description="Generate fly.toml configuration file"
    )
    parser.add_argument("--app", required=True, help="App name")
    parser.add_argument(
        "--region", default="atl", help="Primary region (default: atl)"
    )
    parser.add_argument(
        "--port", type=int, default=8080, help="Internal port (default: 8080)"
    )
    parser.add_argument(
        "--no-auto-scale",
        action="store_true",
        help="Disable auto-scaling (machines always running)",
    )
    parser.add_argument(
        "--min-machines",
        type=int,
        default=0,
        help="Minimum running machines (default: 0)",
    )
    parser.add_argument(
        "--vm-size",
        default="shared-cpu-1x",
        help="VM size (default: shared-cpu-1x)",
    )
    parser.add_argument(
        "--vm-memory", default="256mb", help="VM memory (default: 256mb)"
    )
    parser.add_argument(
        "--health-path",
        default="/health",
        help="Health check path (default: /health)",
    )
    parser.add_argument(
        "--postgres", action="store_true", help="Include Postgres configuration"
    )
    parser.add_argument(
        "--redis", action="store_true", help="Include Redis configuration"
    )
    parser.add_argument(
        "--volumes", action="store_true", help="Include volume mounts"
    )
    parser.add_argument(
        "--release-command", help="Command to run before deployment"
    )
    parser.add_argument(
        "--output", default="fly.toml", help="Output file (default: fly.toml)"
    )

    args = parser.parse_args()

    config = generate_fly_toml(
        app_name=args.app,
        primary_region=args.region,
        internal_port=args.port,
        auto_scale=not args.no_auto_scale,
        min_machines=args.min_machines,
        vm_size=args.vm_size,
        vm_memory=args.vm_memory,
        health_check_path=args.health_path,
        has_postgres=args.postgres,
        has_redis=args.redis,
        has_volumes=args.volumes,
        release_command=args.release_command,
    )

    with open(args.output, "w") as f:
        f.write(config)

    print(f"✅ Generated {args.output}")
    print(f"   App: {args.app}")
    print(f"   Region: {args.region}")
    print(f"   Port: {args.port}")


if __name__ == "__main__":
    main()
