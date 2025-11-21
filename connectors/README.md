# Echo Connectors

## Overview
Echo Connectors provide pre-built integrations with popular business systems, enabling seamless data flow and automation.

## Available Connectors

### CRM Systems (`crm/`)

#### Salesforce
**File:** `salesforce_connector.py`

**Features:**
- Lead management
- Opportunity tracking
- Account management
- SOQL queries
- Contact synchronization

**Usage:**
```python
from connectors.crm import SalesforceConnector

connector = SalesforceConnector({
    "client_id": "your_client_id",
    "client_secret": "your_secret",
    "username": "user@example.com",
    "password": "password",
    "security_token": "token"
})

await connector.connect()

# Create lead
lead = await connector.create_lead({
    "FirstName": "John",
    "LastName": "Doe",
    "Company": "Tech Corp",
    "Email": "john@techcorp.com"
})
```

#### HubSpot
- Contact management
- Deal pipeline
- Email tracking
- Marketing automation

---

### Communication (`communication/`)

#### Slack
**File:** `slack_connector.py`

**Features:**
- Send messages and DMs
- File uploads
- Channel management
- Emoji reactions
- User information

**Usage:**
```python
from connectors.communication import SlackConnector

connector = SlackConnector(bot_token="xoxb-your-token")
await connector.connect()

# Send message
await connector.send_message(
    channel="#general",
    text="Workflow completed! ✅"
)

# Send rich message
await connector.send_message(
    channel="#alerts",
    text="System Alert",
    blocks=[{
        "type": "section",
        "text": {"type": "mrkdwn", "text": "*Alert:* High CPU usage"}
    }]
)
```

#### Microsoft Teams
- Team messaging
- Channel notifications
- Adaptive cards
- Meeting integration

#### Discord
- Server management
- Channel messaging
- Webhook integration
- Rich embeds

---

### Database (`database/`)

#### PostgreSQL
**File:** `postgresql_connector.py`

**Features:**
- Query execution
- CRUD operations
- Bulk operations
- Table management

**Usage:**
```python
from connectors.database import PostgreSQLConnector

connector = PostgreSQLConnector(
    "postgresql://user:pass@localhost:5432/dbname"
)

await connector.connect()

# Insert data
user = await connector.insert("users", {
    "email": "user@example.com",
    "name": "John Doe"
})

# Query data
results = await connector.execute_query(
    "SELECT * FROM users WHERE active = $1",
    (True,)
)
```

#### MongoDB
- Document operations
- Collection management
- Aggregation pipelines
- Index management

#### Redis
- Key-value operations
- Caching
- Pub/Sub messaging
- Session storage

---

### Cloud Providers (`cloud/`)

#### AWS
**Services:**
- S3: File storage
- Lambda: Serverless functions
- SQS: Message queuing
- DynamoDB: NoSQL database
- SES: Email service

**Usage:**
```python
from connectors.cloud import AWSConnector

connector = AWSConnector({
    "access_key_id": "AKIA...",
    "secret_access_key": "...",
    "region": "us-east-1"
})

# Upload to S3
await connector.s3_upload("bucket-name", "file.txt", content)

# Send email via SES
await connector.ses_send_email(
    from_email="noreply@example.com",
    to_emails=["user@example.com"],
    subject="Welcome!",
    body="Welcome to our platform"
)
```

#### Azure
- Blob Storage
- Functions
- Service Bus
- Cosmos DB

#### Google Cloud Platform
- Cloud Storage
- Cloud Functions
- Pub/Sub
- Firestore

---

### Payment Processing (`payment/`)

#### Stripe
**File:** `stripe_connector.py`

**Features:**
- Customer management
- Payment intents
- Subscriptions
- Refunds
- Webhooks

**Usage:**
```python
from connectors.payment import StripeConnector

connector = StripeConnector(api_key="sk_test_...")
await connector.connect()

# Create customer
customer = await connector.create_customer(
    email="customer@example.com"
)

# Create payment
payment_intent = await connector.create_payment_intent(
    amount=5000,  # $50.00
    currency="usd",
    customer_id=customer["id"]
)

# Create subscription
subscription = await connector.create_subscription(
    customer_id=customer["id"],
    price_id="price_xxxxx",
    trial_days=14
)
```

#### Square
- Point of sale
- Online payments
- Invoicing
- Catalog management

---

## Business Integration Examples

### Example 1: E-commerce Order Processing
```python
from echo_engines.echo_core import EchoCoreEngine
from connectors.payment import StripeConnector
from connectors.database import PostgreSQLConnector
from connectors.communication import SlackConnector

async def process_order(order_data):
    # Initialize connectors
    stripe = StripeConnector(api_key="sk_...")
    db = PostgreSQLConnector("postgresql://...")
    slack = SlackConnector(bot_token="xoxb-...")

    await stripe.connect()
    await db.connect()
    await slack.connect()

    # Process payment
    payment = await stripe.create_payment_intent(
        amount=order_data["amount"],
        currency="usd"
    )

    # Save order to database
    order = await db.insert("orders", {
        "customer_id": order_data["customer_id"],
        "amount": order_data["amount"],
        "payment_id": payment["id"],
        "status": "processing"
    })

    # Notify team
    await slack.send_message(
        channel="#orders",
        text=f"New order #{order['id']} - ${order_data['amount']/100}"
    )

    return order
```

### Example 2: CRM Lead Enrichment
```python
from connectors.crm import SalesforceConnector
from echo_engines.echo_free import EchoFreeEngine

async def enrich_lead(lead_data):
    # Initialize
    sf = SalesforceConnector({...})
    echo_free = EchoFreeEngine()

    await sf.connect()

    # Generate personalized outreach
    outreach = await echo_free.generate(
        f"Create personalized email for {lead_data['industry']} company"
    )

    # Create lead in Salesforce
    lead = await sf.create_lead({
        **lead_data,
        "custom_outreach": outreach["generated_content"]
    })

    return lead
```

### Example 3: Automated Compliance Reporting
```python
from echo_engines.echo_lex import EchoLexEngine, ComplianceFramework
from connectors.database import PostgreSQLConnector
from connectors.cloud import AWSConnector

async def generate_compliance_report():
    # Initialize
    echo_lex = EchoLexEngine()
    db = PostgreSQLConnector("postgresql://...")
    aws = AWSConnector({...})

    await db.connect()

    # Get user data
    users = await db.execute_query("SELECT * FROM users")

    # Check GDPR compliance
    compliance = await echo_lex.check_compliance(
        str(users),
        ComplianceFramework.GDPR
    )

    # Generate report
    report = f"Compliance Report\n{compliance}"

    # Upload to S3
    await aws.s3_upload("compliance-reports", "report.txt", report)

    return compliance
```

## Creating Custom Connectors

### Connector Template
```python
from typing import Dict, Any
from datetime import datetime

class CustomConnector:
    """Connector for [Service Name]"""

    def __init__(self, credentials: Dict[str, str]):
        self.credentials = credentials
        self.connected = False

    async def connect(self) -> bool:
        """Establish connection"""
        # Initialize connection
        self.connected = True
        return True

    async def disconnect(self):
        """Close connection"""
        self.connected = False

    async def your_method(self, params) -> Dict[str, Any]:
        """Your connector method"""
        if not self.connected:
            raise Exception("Not connected")

        # Your logic here
        return {"status": "success"}
```

## Environment Variables

Store credentials securely using Echo Vault:

```python
from echo_vault.secrets import SecretsManager, CredentialsStore

sm = SecretsManager()
creds = CredentialsStore(sm)

# Store credentials
creds.store_api_credentials("stripe", api_key="sk_...")
creds.store_oauth_credentials("salesforce", client_id="...", client_secret="...")

# Retrieve credentials
stripe_creds = creds.get_api_credentials("stripe")
sf_creds = creds.get_oauth_credentials("salesforce")
```

## Error Handling

```python
from connectors.exceptions import ConnectorError

try:
    await connector.connect()
    result = await connector.some_operation()
except ConnectorError as e:
    logger.error(f"Connector error: {e}")
    # Handle error
```

## Dependencies

```bash
# CRM
pip install simple-salesforce hubspot-api-client

# Communication
pip install slack-sdk python-teams-webhook

# Database
pip install asyncpg motor redis

# Cloud
pip install boto3 azure-storage-blob google-cloud-storage

# Payment
pip install stripe square
```

## Testing

```bash
# Run connector tests
pytest tests/connectors/

# Test specific connector
pytest tests/connectors/test_stripe_connector.py
```

## Contributing

To add a new connector:

1. Create connector file in appropriate directory
2. Implement standard interface (connect, disconnect, etc.)
3. Add documentation
4. Write tests
5. Update this README
