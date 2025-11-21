# Echo Examples

## Overview
This directory contains practical examples demonstrating how to use Echo for various business scenarios.

## Available Examples

### 1. E-commerce Automation (`ecommerce_automation.py`)
**Use Case:** Automated order processing for e-commerce platforms

**Features:**
- Order validation
- Payment processing (Stripe integration)
- Inventory management
- Shipment creation
- Customer notifications
- Team alerts (Slack)

**Run:**
```bash
python examples/ecommerce_automation.py
```

**Key Learnings:**
- Building complex workflows with EchoCore
- Integrating multiple business systems
- Error handling and rollback strategies
- Real-time notifications

---

### 2. Content Generation (`content_generation.py`)
**Use Case:** AI-powered content creation for marketing

**Features:**
- Blog post generation with SEO optimization
- Social media content for multiple platforms
- Email marketing campaigns
- Follow-up sequences

**Run:**
```bash
python examples/content_generation.py
```

**Key Learnings:**
- Using EchoFree for creative generation
- Multi-platform content adaptation
- SEO optimization techniques
- Campaign automation

---

### 3. Legal & Compliance (`legal_compliance.py`)
**Use Case:** Automated legal document analysis and compliance checking

**Features:**
- Contract analysis and risk assessment
- Multi-framework compliance checking (GDPR, CCPA, HIPAA)
- Privacy policy generation
- Risk scoring and recommendations

**Run:**
```bash
python examples/legal_compliance.py
```

**Key Learnings:**
- Using EchoLex for legal operations
- Compliance automation
- Risk assessment frameworks
- Document generation

---

## Quick Start

### Prerequisites

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your API keys and credentials
```

3. **Initialize Echo:**
```bash
python -c "from echo_vault.secrets import SecretsManager; from cryptography.fernet import Fernet; print(f'Master Key: {Fernet.generate_key().decode()}')"
```

### Running Examples

Each example can be run independently:

```bash
# E-commerce automation
python examples/ecommerce_automation.py

# Content generation
python examples/content_generation.py

# Legal compliance
python examples/legal_compliance.py
```

## Example Structure

Each example follows this pattern:

```python
# 1. Import Echo components
from echo_engines.echo_core import EchoCoreEngine
from connectors.payment import StripeConnector

# 2. Initialize system
class MyAutomation:
    def __init__(self):
        self.engine = EchoCoreEngine()
        self.connector = StripeConnector(api_key="...")

# 3. Setup workflows
async def setup(self):
    await self.connector.connect()
    self.engine.register_workflow("my_workflow", {...})

# 4. Execute operations
async def process(self, data):
    result = await self.engine.execute_workflow("my_workflow", data)
    return result

# 5. Run example
if __name__ == "__main__":
    asyncio.run(main())
```

## Customization

### Modify Workflows

```python
# Add custom steps to workflows
workflow_definition = {
    "name": "My Custom Workflow",
    "steps": [
        {"name": "Step 1", "type": "validation", "action": my_function},
        {"name": "Step 2", "type": "processing", "action": my_other_function},
        # Add more steps
    ]
}
```

### Add Connectors

```python
# Initialize additional connectors
slack = SlackConnector(bot_token="xoxb-...")
salesforce = SalesforceConnector({...})

# Use in workflows
await slack.send_message("#channel", "Message")
await salesforce.create_lead({...})
```

### Configure Engines

```python
# EchoFree configuration
echo_free = EchoFreeEngine()
echo_free.set_mode("creative")  # creative, analytical, experimental
echo_free.add_constraint("length: short")

# EchoCore configuration
echo_core = EchoCoreEngine(config={
    "max_concurrent_tasks": 10,
    "timeout_seconds": 300
})
```

## Business Scenarios

### Scenario 1: SaaS Customer Onboarding
```python
# Combine multiple examples
async def onboard_customer(customer_data):
    # 1. Generate personalized content
    welcome = await content_generator.generate_email_campaign(...)

    # 2. Process payment
    payment = await ecommerce.process_payment(...)

    # 3. Setup account
    account = await create_account(...)

    # 4. Send notifications
    await notify_team(...)
```

### Scenario 2: Automated Compliance Reporting
```python
async def daily_compliance_check():
    # Check multiple frameworks
    results = await legal_system.check_compliance(
        content=get_daily_data(),
        frameworks=["GDPR", "CCPA", "SOC2"]
    )

    # Generate report
    report = generate_report(results)

    # Alert if issues found
    if has_issues(results):
        await alert_compliance_team(report)
```

### Scenario 3: Marketing Automation
```python
async def launch_campaign(campaign_data):
    # Generate content
    content = await generator.generate_blog_post(...)
    social = await generator.generate_social_media_content(...)

    # Schedule posts
    await schedule_posts(social)

    # Track performance
    await setup_analytics(campaign_data)
```

## Integration Patterns

### Pattern 1: Webhook Handler
```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/webhook/order")
async def handle_order_webhook(order: Order):
    result = await ecommerce.process_order(order.dict())
    return {"status": "processing", "id": result["order_id"]}
```

### Pattern 2: Scheduled Job
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', hour=9)
async def daily_content_generation():
    topics = get_trending_topics()
    for topic in topics:
        post = await generator.generate_blog_post(topic, keywords=[])
        await publish_post(post)

scheduler.start()
```

### Pattern 3: Event-Driven
```python
from echo_os.core import EchoOrchestrator

orchestrator = EchoOrchestrator()

@orchestrator.on_event("order.created")
async def handle_order_created(event):
    await ecommerce.process_order(event.data)

@orchestrator.on_event("customer.registered")
async def handle_customer_registered(event):
    await send_welcome_email(event.data)
```

## Testing

Run tests for examples:

```bash
pytest examples/tests/
```

## Performance Tips

1. **Use batch operations:**
```python
# Instead of processing one at a time
for item in items:
    await process(item)

# Process in batches
await core_engine.process_batch(items, process)
```

2. **Enable caching:**
```python
echo_free = EchoFreeEngine()
echo_free.config["cache_enabled"] = True
```

3. **Use connection pooling:**
```python
db = PostgreSQLConnector(
    connection_string,
    pool_size=20
)
```

## Troubleshooting

### Issue: Import errors
**Solution:** Ensure you're in the Echo root directory
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

### Issue: Connection failures
**Solution:** Check credentials in .env file
```bash
# Verify environment variables
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('STRIPE_API_KEY'))"
```

### Issue: Rate limiting
**Solution:** Implement backoff strategy
```python
from tenacity import retry, wait_exponential

@retry(wait=wait_exponential(multiplier=1, min=4, max=10))
async def make_api_call():
    # Your API call
    pass
```

## Contributing

To add a new example:

1. Create new file: `examples/my_example.py`
2. Follow the standard structure
3. Add documentation
4. Update this README
5. Add tests: `examples/tests/test_my_example.py`

## Resources

- [Getting Started Guide](../docs/GETTING_STARTED.md)
- [API Documentation](../docs/api/API_REFERENCE.md)
- [Business Guide](../docs/BUSINESS_GUIDE.md)
- [Architecture Overview](../ARCHITECTURE.md)

## Support

- GitHub Issues: [github.com/echo/issues](https://github.com)
- Discord: [discord.gg/echo](https://discord.gg)
- Email: support@echo.ai
