# Getting Started with Echo

## What is Echo?

Echo is a hybrid intelligence framework that integrates AI-powered systems, ethical design, and adaptive engineering into a unified platform. It enables businesses to:

- Automate workflows and business processes
- Generate creative content and analyze documents
- Integrate with existing business systems (CRM, payment, communication)
- Ensure legal compliance and risk management
- Build custom AI-powered applications

## Quick Start

### Prerequisites

- Python 3.9 or higher
- Docker (optional, for containerized deployment)
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-org/Echo.git
cd Echo
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Basic Setup

1. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your settings
```

Required environment variables:
```bash
# Echo Vault
ECHO_VAULT_MASTER_KEY=<your-master-key>
ECHO_VAULT_SECRET_KEY=<jwt-secret>

# API Configuration
ECHO_API_HOST=0.0.0.0
ECHO_API_PORT=8000

# Optional: AI Provider API Keys
OPENAI_API_KEY=<your-key>
ANTHROPIC_API_KEY=<your-key>
```

2. **Initialize Echo Vault**
```python
from echo_vault.secrets import SecretsManager
from cryptography.fernet import Fernet

# Generate master key
master_key = Fernet.generate_key()
print(f"Master Key: {master_key.decode()}")

# Save this key securely!
```

### Start the API Server

```bash
# Development mode
uvicorn api.rest.server:app --reload

# Production mode
uvicorn api.rest.server:app --host 0.0.0.0 --port 8000 --workers 4
```

Visit:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Your First Echo Application

### Example 1: Generate Creative Content

```python
from echo_engines.echo_free import EchoFreeEngine

# Initialize engine
engine = EchoFreeEngine()

# Generate content
result = await engine.generate(
    "Create a marketing campaign for sustainable tech products"
)

print(result["generated_content"])
```

### Example 2: Process Workflow

```python
from echo_engines.echo_core import EchoCoreEngine

# Initialize engine
engine = EchoCoreEngine()

# Register workflow
engine.register_workflow("customer_onboarding", {
    "name": "Customer Onboarding",
    "steps": [
        {"name": "Verify Email", "type": "validation"},
        {"name": "Create Account", "type": "database"},
        {"name": "Send Welcome Email", "type": "notification"}
    ]
})

# Execute workflow
result = await engine.execute_workflow(
    "customer_onboarding",
    {"email": "customer@example.com", "name": "John Doe"}
)

print(f"Status: {result['status']}")
```

### Example 3: Analyze Legal Document

```python
from echo_engines.echo_lex import EchoLexEngine, ComplianceFramework

# Initialize engine
engine = EchoLexEngine(config={"jurisdiction": "US"})

# Analyze contract
analysis = await engine.analyze_contract(
    contract_text="[Your contract text here]"
)

print(f"Key Terms: {analysis['key_terms']}")
print(f"Risks: {analysis['risks']}")
```

### Example 4: Use REST API

```bash
# Get API key first (or use your existing key)
export API_KEY="echo_your_api_key"

# Generate content
curl -X POST http://localhost:8000/engines/echo-free/generate \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Generate ideas for a sustainable business",
    "engine": "echo-free"
  }'
```

## Next Steps

### Integrate with Business Systems

**Connect to Slack:**
```python
from connectors.communication import SlackConnector

slack = SlackConnector(bot_token="xoxb-your-token")
await slack.connect()
await slack.send_message("#general", "Echo is online! 🚀")
```

**Connect to Stripe:**
```python
from connectors.payment import StripeConnector

stripe = StripeConnector(api_key="sk_test_...")
await stripe.connect()

customer = await stripe.create_customer(
    email="customer@example.com"
)
```

**Connect to Salesforce:**
```python
from connectors.crm import SalesforceConnector

sf = SalesforceConnector({
    "client_id": "...",
    "client_secret": "...",
    "username": "user@example.com",
    "password": "password",
    "security_token": "token"
})

await sf.connect()
lead = await sf.create_lead({
    "FirstName": "John",
    "LastName": "Doe",
    "Company": "Tech Corp"
})
```

### Build Custom Workflows

```python
from echo_engines.echo_core import EchoCoreEngine
from connectors.payment import StripeConnector
from connectors.communication import SlackConnector

async def automated_billing_workflow(customer_data):
    """Example: Automated billing with notifications"""

    # Initialize
    core = EchoCoreEngine()
    stripe = StripeConnector(api_key="sk_...")
    slack = SlackConnector(bot_token="xoxb-...")

    await stripe.connect()
    await slack.connect()

    # Process payment
    payment = await stripe.create_payment_intent(
        amount=customer_data["amount"],
        currency="usd",
        customer_id=customer_data["customer_id"]
    )

    # Notify team
    await slack.send_message(
        "#billing",
        f"Payment processed: ${customer_data['amount']/100}"
    )

    return payment
```

## Architecture Overview

```
Echo/
├── echo-os/          # Core orchestration system
├── echo-vault/       # Security and secrets management
├── echo-engines/     # Processing engines (Free, Lex, Core)
├── api/              # REST/GraphQL/WebSocket APIs
├── connectors/       # Business system integrations
├── plugins/          # Custom plugins
├── docs/             # Documentation
└── examples/         # Example applications
```

## Configuration

### Echo OS Configuration
```yaml
# config/echo-os.yaml
orchestrator:
  max_agents: 20
  event_queue_size: 5000
  log_level: INFO
```

### Engine Configuration
```yaml
# config/engines.yaml
echo-free:
  creativity: 0.8
  max_tokens: 2000

echo-lex:
  jurisdiction: US
  frameworks: [GDPR, CCPA]

echo-core:
  max_concurrent_tasks: 10
  timeout_seconds: 300
```

## Deployment

### Docker Deployment

```bash
# Build image
docker build -t echo:latest .

# Run container
docker run -p 8000:8000 \
  -e ECHO_VAULT_MASTER_KEY=$MASTER_KEY \
  echo:latest
```

### Docker Compose

```bash
docker-compose up -d
```

### Kubernetes

```bash
kubectl apply -f k8s/
```

## Common Use Cases

### 1. Customer Support Automation
Automate responses, ticket routing, and knowledge base integration.

### 2. Document Processing
Extract data, analyze contracts, ensure compliance.

### 3. E-commerce Automation
Order processing, inventory management, customer communication.

### 4. Marketing Automation
Content generation, campaign management, analytics.

### 5. Financial Services
Compliance checking, risk assessment, transaction processing.

## Troubleshooting

### API Key Issues
```python
# Generate new API key
from echo_vault.auth import AuthManager

auth = AuthManager(secret_key="your-secret")
api_key = auth.generate_api_key(
    user_id="your_id",
    permissions=["read", "write"]
)
```

### Connection Issues
- Check network connectivity
- Verify credentials in Echo Vault
- Review connector logs

### Performance Issues
- Increase worker count
- Enable caching
- Use batch operations

## Getting Help

- **Documentation:** `/docs/`
- **API Reference:** http://localhost:8000/docs
- **GitHub Issues:** https://github.com/your-org/Echo/issues
- **Community:** https://discord.gg/echo

## What's Next?

- [Architecture Guide](./architecture/ARCHITECTURE.md)
- [API Documentation](./api/API_REFERENCE.md)
- [Connector Guide](../connectors/README.md)
- [Examples](../examples/README.md)
- [Best Practices](./guides/BEST_PRACTICES.md)
