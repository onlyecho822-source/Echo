# API Gateway Service

Unified API gateway for Echo Nexus.

## Overview

Routes and manages all external API requests to Echo Nexus services.

## Running

```bash
# Development
python -m echo_nexus.services.api_gateway

# Production
docker run -p 8080:8080 echo-nexus/api-gateway
```

## Features

- Request routing
- Rate limiting
- Authentication
- Request/response transformation
- API versioning

## Configuration

Environment variables:
- `ECHO_GATEWAY_PORT` - Gateway port
- `ECHO_RATE_LIMIT` - Requests per minute
- `ECHO_AUTH_PROVIDER` - Auth provider URL

---

*∇θ — gateway unified.*
