# EchoLex Documentation

## Global Legal Research Engine

EchoLex is a comprehensive legal research platform providing case analysis, judge analytics, and predictive models for legal outcomes.

---

## ⚠️ IMPORTANT DISCLAIMER

**FOR RESEARCH PURPOSES ONLY**

This system provides legal information and analytics for research purposes. It does **NOT** constitute legal advice.

Always consult a licensed attorney for legal matters in your jurisdiction.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [API Reference](#api-reference)
6. [Models](#models)
7. [Predictions](#predictions)
8. [Judge Analytics](#judge-analytics)
9. [Live Updates](#live-updates)

---

## Overview

EchoLex is designed to provide legal researchers, academics, and policy analysts with comprehensive data-driven insights into the legal system. It covers:

- **All case types**: From traffic infractions to capital murder
- **Global jurisdictions**: Federal, state, local, and international courts
- **Predictive analytics**: ML-powered outcome predictions
- **Judge profiling**: Comprehensive bench metrics and scorecards

---

## Features

### Case Analysis
- Search across millions of cases
- Filter by type, severity, jurisdiction, outcome
- Timeline visualization
- Related case identification

### Judge Scorecards
- Proforma follow rates
- Sentencing pattern analysis
- Motion grant rates
- Appeal reversal rates
- Temporal trends

### Predictions
- Case outcome prediction
- Sentencing range prediction
- Appeal likelihood and success
- Confidence scoring

### Live Updates
- Real-time case status updates
- New ruling notifications
- Jurisdiction news
- WebSocket streaming

---

## Installation

### Requirements
- Python 3.10+
- PostgreSQL 14+
- Redis 6+

### Setup

```bash
# Clone repository
git clone https://github.com/echo-civilization/echolex.git
cd echolex

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run database migrations
alembic upgrade head

# Start the server
echolex serve
```

---

## Quick Start

### CLI Usage

```bash
# Start the API server
echolex serve --host 0.0.0.0 --port 8000

# Predict case outcome
echolex predict dui_dwi --severity misdemeanor

# List case types
echolex case-types

# List severity levels
echolex severities

# System information
echolex info
```

### API Usage

```python
import httpx

# Search cases
response = httpx.get(
    "http://localhost:8000/api/v1/cases",
    params={"case_type": "dui_dwi", "limit": 10}
)
cases = response.json()

# Get judge scorecard
response = httpx.get(
    f"http://localhost:8000/api/v1/judges/{judge_id}/scorecard"
)
scorecard = response.json()

# Predict outcome
response = httpx.post(
    "http://localhost:8000/api/v1/predictions/case-outcome",
    json=case_data
)
prediction = response.json()
```

---

## API Reference

### Base URL
```
http://localhost:8000
```

### Authentication
API keys required for production. Pass in header:
```
Authorization: Bearer <api_key>
```

### Endpoints

#### Cases
- `GET /api/v1/cases` - Search cases
- `GET /api/v1/cases/{id}` - Get case details
- `GET /api/v1/cases/{id}/timeline` - Get case timeline

#### Judges
- `GET /api/v1/judges` - Search judges
- `GET /api/v1/judges/{id}` - Get judge details
- `GET /api/v1/judges/{id}/scorecard` - Get judge scorecard
- `GET /api/v1/judges/compare` - Compare judges

#### Predictions
- `POST /api/v1/predictions/case-outcome` - Predict outcome
- `POST /api/v1/predictions/sentence` - Predict sentence
- `POST /api/v1/predictions/appeal` - Predict appeal

#### Analytics
- `GET /api/v1/analytics/cases` - Case analytics
- `GET /api/v1/analytics/jurisdictions/{id}` - Jurisdiction stats

#### WebSocket
- `WS /ws/{client_id}` - Live updates

---

## Models

### Case Types

```python
# Traffic & Vehicle
TRAFFIC_INFRACTION, TRAFFIC_MISDEMEANOR, DUI_DWI,
RECKLESS_DRIVING, VEHICULAR_MANSLAUGHTER

# Property Crimes
PETTY_THEFT, GRAND_THEFT, BURGLARY, ROBBERY,
ARMED_ROBBERY, ARSON

# Drug Offenses
DRUG_POSSESSION, DRUG_DISTRIBUTION,
DRUG_TRAFFICKING, DRUG_MANUFACTURING

# Violent Crimes
SIMPLE_ASSAULT, AGGRAVATED_ASSAULT, BATTERY,
DOMESTIC_VIOLENCE, KIDNAPPING

# Homicide
INVOLUNTARY_MANSLAUGHTER, VOLUNTARY_MANSLAUGHTER,
MURDER_2, MURDER_1, CAPITAL_MURDER

# White Collar
FRAUD, EMBEZZLEMENT, TAX_EVASION,
MONEY_LAUNDERING, SECURITIES_FRAUD
```

### Severity Levels

```python
INFRACTION          # Parking tickets, minor violations
PETTY_OFFENSE       # Minor traffic violations
MISDEMEANOR         # Class A, B, C misdemeanors
GROSS_MISDEMEANOR   # Enhanced misdemeanors
FELONY_4            # 4th degree felony
FELONY_3            # 3rd degree felony
FELONY_2            # 2nd degree felony
FELONY_1            # 1st degree felony
CAPITAL             # Capital murder, death penalty eligible
```

---

## Predictions

### How Predictions Work

EchoLex uses machine learning models trained on historical case data to predict:

1. **Case Outcomes**: Probability distribution across:
   - Convicted
   - Guilty plea
   - Dismissed
   - Acquitted

2. **Sentencing**: Ranges for:
   - Incarceration (months)
   - Probation (months)
   - Fines (amount)
   - Special outcomes (death penalty, LWOP)

3. **Appeals**: Analysis of:
   - Appeal likelihood
   - Success probability
   - Potential grounds

### Factors Considered

- Case severity and charges
- Judge historical patterns
- Jurisdiction norms
- Evidence strength
- Prior record
- Defense quality

### Confidence Scoring

Each prediction includes a confidence score (0-1) based on:
- Sample size
- Data quality
- Pattern strength

---

## Judge Analytics

### Scorecard Metrics

#### Proforma Follow Rates
- Sentencing guidelines follow rate
- Plea agreement acceptance rate
- Motion grant rate
- Continuance grant rate
- Bail guidelines follow rate

#### Sentencing Patterns
- Average deviation from guidelines
- Probation preference rate
- Alternative sentencing rate
- Enhancement application rate

#### Trial Behavior
- Average trial duration
- Jury vs bench trial preference
- Mistrial rate

#### Appeal Metrics
- Reversal rate
- Partial reversal rate
- Affirmed rate

### Pattern Identification

EchoLex automatically identifies notable patterns:
- "Consistently lenient sentencing (20%+ below guidelines)"
- "High motion grant rate (70%+)"
- "Strong preference for probation over incarceration"

---

## Live Updates

### WebSocket Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/client123');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Update:', data);
};

// Subscribe to case updates
ws.send(JSON.stringify({
    action: 'subscribe',
    topic: 'case',
    id: 'case-uuid-here'
}));

// Subscribe to judge rulings
ws.send(JSON.stringify({
    action: 'subscribe',
    topic: 'judge',
    id: 'judge-uuid-here'
}));

// Subscribe to broadcasts
ws.send(JSON.stringify({
    action: 'subscribe',
    topic: 'broadcast'
}));
```

### Update Types

- `case_update` - Case status changes, new events
- `judge_ruling` - New judge decisions
- `jurisdiction_news` - Legal news, law changes
- `prediction_update` - Updated predictions
- `broadcast` - System announcements

---

## Support

For issues and questions:
- GitHub Issues: [Link to issues]
- Documentation: [Link to full docs]

---

## License

MIT License

Copyright (c) 2024 Echo Civilization

---

## Acknowledgments

EchoLex is part of the Echo Civilization framework for ethical AI systems.

---

**Remember: This system is for RESEARCH PURPOSES ONLY. Always consult a licensed attorney for legal matters.**
