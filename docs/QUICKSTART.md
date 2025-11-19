# Echo Life OS - Quick Start Guide

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/Echo.git
   cd Echo
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Basic Usage

### Initialize the System

```python
from src.echo import create_echo

# Create and initialize Echo Life OS
echo = create_echo(password="your-secure-password")
echo.initialize("your-secure-password")

# Check status
print(echo.get_status())
```

### Query the Council

```python
# Ask a question
result = echo.query("Should I invest in index funds?")
print(result['judgment'])

# With context
result = echo.query(
    "How can I reduce my monthly expenses?",
    context={
        'monthly_income': 5000,
        'goals': ['save for house', 'reduce debt']
    }
)
```

### Track Finances

```python
# Add a transaction
echo.financial.add_transaction(
    amount=45.50,
    category='food',
    description='Grocery shopping',
    transaction_type='expense'
)

# Get monthly summary
summary = echo.financial.get_monthly_summary()
print(f"Savings rate: {summary['savings_rate']:.1f}%")

# Get optimization suggestions
suggestions = echo.financial.get_optimization_suggestions()
for s in suggestions:
    print(f"- {s['description']}")
```

### Security Features

```python
# Check if an action is allowed
result = echo.security.check_action("delete user data")
if not result['allowed']:
    print(f"Blocked: {result['threats']}")

# Lock the system
echo.security.lock()

# Emergency lockdown
echo.security.emergency_lockdown()
```

### Memory Storage

```python
# Store encrypted data
echo.memory.store('my_notes', {'text': 'Important info'}, category='notes')

# Retrieve data
notes = echo.memory.retrieve('my_notes')

# Set preferences
echo.memory.set_preference('theme', 'dark')
```

## Context Manager Usage

```python
from src.echo import EchoLifeOS

with EchoLifeOS() as echo:
    echo.initialize("password")
    result = echo.query("What's my financial health?")
    print(result)
# Automatically closes and saves state
```

## Example: Complete Workflow

```python
from src.echo import create_echo

# Initialize
echo = create_echo()
echo.initialize("secure-password-123")

# Set a financial goal
echo.financial.set_goal(
    name="Emergency Fund",
    target_amount=10000,
    deadline="2024-12-31",
    category="savings"
)

# Track some transactions
transactions = [
    (3500, 'income', 'Salary', 'income'),
    (1200, 'housing', 'Rent', 'expense'),
    (300, 'food', 'Groceries', 'expense'),
    (100, 'utilities', 'Electric bill', 'expense'),
]

for amount, category, desc, t_type in transactions:
    echo.financial.add_transaction(amount, category, desc, t_type)

# Get financial health
health = echo.financial.get_financial_health()
print(f"Financial Health Score: {health['overall_score']:.0f}/100")

# Get council recommendations
result = echo.query(
    "How can I reach my emergency fund goal faster?",
    context={'goals': ['build emergency fund']}
)

for rec in result.get('judgment', {}).get('recommendations', []):
    print(f"Recommendation: {rec}")

# Cleanup
echo.close()
```

## Security Best Practices

1. **Use a strong master password** - At least 12 characters with mixed case, numbers, and symbols
2. **Don't share your password** - The system cannot recover it
3. **Regular backups** - Use `memory.export_backup()` regularly
4. **Review security events** - Check `security.get_events()` periodically

## Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) for system design details
- Explore individual modules in `src/`
- Check configuration options in `config/default.yaml`
