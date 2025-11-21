# Echo API

## Overview
The Echo API provides programmatic access to all Echo subsystems through REST, GraphQL, and WebSocket interfaces.

## API Types

### 1. REST API (`rest/`)
Standard HTTP REST API using FastAPI

**Base URL:** `http://localhost:8000`

**Authentication:** API key in header
```
X-API-Key: echo_your_api_key_here
```

### 2. GraphQL API (`graphql/`)
GraphQL interface for flexible querying

**Endpoint:** `http://localhost:8000/graphql`

### 3. WebSocket API (`websocket/`)
Real-time bidirectional communication

**Endpoint:** `ws://localhost:8000/ws`

## Quick Start

### Installation

```bash
pip install fastapi uvicorn pydantic
```

### Run Server

```bash
# Development
uvicorn api.rest.server:app --reload

# Production
uvicorn api.rest.server:app --host 0.0.0.0 --port 8000 --workers 4
```

### Make Request

```bash
curl -X GET http://localhost:8000/health

curl -X POST http://localhost:8000/engines/echo-free/generate \
  -H "X-API-Key: echo_your_key" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Generate a business plan", "engine": "echo-free"}'
```

## REST API Endpoints

### System

- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation
- `GET /redoc` - Alternative API documentation

### Echo OS (Orchestrator)

- `POST /orchestrator/agents/register` - Register new agent
- `POST /orchestrator/agents/{agent_id}/activate` - Activate agent
- `POST /orchestrator/agents/{agent_id}/terminate` - Terminate agent
- `GET /orchestrator/status` - Get system status
- `GET /orchestrator/agents` - List all agents

### Echo Engines

**EchoFree:**
- `POST /engines/echo-free/generate` - Generate creative content
- `POST /engines/echo-free/brainstorm` - Generate ideas
- `POST /engines/echo-free/explore` - Explore concepts

**EchoLex:**
- `POST /engines/echo-lex/analyze` - Analyze legal document
- `POST /engines/echo-lex/generate` - Generate legal document
- `POST /engines/echo-lex/compliance` - Check compliance
- `POST /engines/echo-lex/risk` - Assess risk

**EchoCore:**
- `POST /engines/echo-core/workflows/register` - Register workflow
- `POST /engines/echo-core/workflows/execute` - Execute workflow
- `POST /engines/echo-core/tasks/create` - Create task
- `POST /engines/echo-core/tasks/{task_id}/execute` - Execute task
- `GET /engines/echo-core/workflows` - List workflows
- `GET /engines/echo-core/tasks` - List tasks

### Echo Vault

**Authentication:**
- `POST /vault/auth/login` - User login
- `POST /vault/auth/api-key` - Generate API key
- `POST /vault/auth/verify` - Verify token
- `DELETE /vault/auth/api-key/{key_id}` - Revoke API key

**Secrets:**
- `POST /vault/secrets` - Store secret
- `GET /vault/secrets/{key}` - Retrieve secret
- `DELETE /vault/secrets/{key}` - Delete secret
- `GET /vault/secrets` - List secret keys
- `POST /vault/secrets/export` - Export encrypted backup

### Connectors

- `GET /connectors` - List available connectors
- `POST /connectors/{type}/connect` - Connect to service
- `GET /connectors/{type}/status` - Get connector status
- `POST /connectors/{type}/disconnect` - Disconnect service

## Request/Response Examples

### Generate Content (EchoFree)

**Request:**
```bash
POST /engines/echo-free/generate
X-API-Key: echo_xxxxx
Content-Type: application/json

{
  "prompt": "Create a marketing campaign for sustainable fashion",
  "parameters": {
    "creativity": 0.8,
    "length": "medium"
  }
}
```

**Response:**
```json
{
  "engine": "echo-free",
  "prompt": "Create a marketing campaign for sustainable fashion",
  "generated_content": "[Generated campaign details]",
  "metadata": {
    "tokens_used": 500,
    "generation_time_ms": 1200
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Execute Workflow (EchoCore)

**Request:**
```bash
POST /engines/echo-core/workflows/execute
X-API-Key: echo_xxxxx
Content-Type: application/json

{
  "workflow_id": "customer_onboarding",
  "input_data": {
    "email": "customer@example.com",
    "plan": "premium"
  }
}
```

**Response:**
```json
{
  "workflow_id": "customer_onboarding",
  "status": "completed",
  "results": [
    {"step": "Verify Email", "success": true},
    {"step": "Create Account", "success": true},
    {"step": "Setup Dashboard", "success": true}
  ],
  "duration_seconds": 2.5,
  "completed_at": "2025-01-15T10:30:05Z"
}
```

### Analyze Contract (EchoLex)

**Request:**
```bash
POST /engines/echo-lex/analyze
X-API-Key: echo_xxxxx
Content-Type: application/json

{
  "contract_text": "[Contract content here...]",
  "analysis_type": "full"
}
```

**Response:**
```json
{
  "document_type": "contract",
  "key_terms": [
    "Payment terms: Net 30",
    "Termination: 30 days notice"
  ],
  "risks": [
    {
      "level": "medium",
      "description": "Ambiguous IP rights clause"
    }
  ],
  "compliance_status": "review_required",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

## Authentication

### Get API Key

1. Login to get JWT:
```bash
POST /vault/auth/login
{
  "username": "user@example.com",
  "password": "your_password"
}
```

2. Generate API key:
```bash
POST /vault/auth/api-key
Authorization: Bearer {jwt_token}
{
  "user_id": "user123",
  "permissions": ["read", "write"]
}
```

### Use API Key

Include in header:
```
X-API-Key: echo_xxxxxxxxxxxxx
```

## Rate Limiting

- Free tier: 100 requests/hour
- Pro tier: 1000 requests/hour
- Enterprise: Unlimited

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1641234567
```

## Error Responses

```json
{
  "error": "Invalid API key",
  "status_code": 401,
  "timestamp": "2025-01-15T10:30:00Z"
}
```

Common status codes:
- `200` - Success
- `400` - Bad request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not found
- `429` - Rate limit exceeded
- `500` - Internal server error

## WebSocket API

### Connect
```javascript
const ws = new WebSocket('ws://localhost:8000/ws?api_key=echo_xxxxx');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

// Send message
ws.send(JSON.stringify({
  type: 'execute',
  engine: 'echo-free',
  prompt: 'Generate ideas'
}));
```

## GraphQL API

### Query Example
```graphql
query {
  orchestrator {
    status
    agents {
      id
      status
      capabilities
    }
  }
}
```

### Mutation Example
```graphql
mutation {
  executeWorkflow(
    workflowId: "customer_onboarding"
    inputData: {email: "user@example.com"}
  ) {
    status
    results
  }
}
```

## SDK Libraries

Coming soon:
- Python SDK
- JavaScript/TypeScript SDK
- Go SDK
- Ruby SDK

## OpenAPI Specification

Full OpenAPI spec available at `/openapi.json`

## Support

- Documentation: `/docs`
- GitHub: [github.com/echo/api](https://github.com)
- Email: support@echo.ai
