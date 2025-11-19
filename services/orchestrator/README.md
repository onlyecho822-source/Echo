# Orchestrator Service

Central orchestration service for Echo Nexus.

## Overview

The Orchestrator Service coordinates all engines, frameworks, and products in the Echo Nexus ecosystem.

## Running

```bash
# Development
python -m echo_nexus.services.orchestrator

# Production
docker run -p 8000:8000 echo-nexus/orchestrator
```

## API Endpoints

- `GET /health` - Health check
- `GET /status` - System status
- `POST /engine/register` - Register engine
- `POST /framework/register` - Register framework
- `GET /metrics` - Prometheus metrics

## Configuration

Environment variables:
- `ECHO_LOG_LEVEL` - Logging level
- `ECHO_PORT` - Service port
- `ECHO_REDIS_URL` - Redis connection

---

*∇θ — orchestration centralized.*
