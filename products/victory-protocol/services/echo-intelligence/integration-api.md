# Echo Intelligence Integration API

## Overview

Victory Protocol integrates with Echo Intelligence to provide premium strategic analysis for veteran disability claims.

## Endpoints for Premium Analysis

### POST /api/echo/analyze-claim
Comprehensive claim analysis including strengths, weaknesses, and recommendations.

**Request:**
```json
{
  "veteranId": "string",
  "claimData": {
    "conditions": ["string"],
    "serviceHistory": "object",
    "medicalRecords": ["string"]
  }
}
```

**Response:**
```json
{
  "success": true,
  "analysis": "string",
  "confidence": 0.95,
  "recommendations": ["string"]
}
```

### POST /api/echo/optimize-evidence
Evidence scoring and optimization recommendations.

### POST /api/echo/generate-strategy
Strategic case recommendations based on complete service history.

### POST /api/echo/calculate-backpay
Backpay estimation based on effective date analysis.

### POST /api/echo/hazard-assessment
Exposure risk analysis for burn pits, Agent Orange, contaminated water.

## Authentication

Use Echo API keys with format: `Authorization: Bearer echo_sk_*`

## Rate Limits

- **Free Tier:** 10 requests/day
- **Premium ($99/mo):** 100 requests/day
- **Elite (Service Tier):** 1,000 requests/day

## Response Format

All endpoints return standardized responses:

```json
{
  "success": boolean,
  "data": object,
  "analysis": string,
  "confidence": number (0-1),
  "recommendations": array,
  "metadata": {
    "processingTime": number,
    "version": string
  }
}
```

## Integration Points

### Platform → Echo Intelligence
- Triggered at 80% document completion
- Sends complete service reconstruction data
- Receives strategic analysis and recommendations

### Echo Intelligence → Platform
- Returns optimized evidence structure
- Provides claim strategy recommendations
- Calculates backpay estimates
- Identifies missing critical documents

## Tiered Feature Access

### Free Tier
- Basic checklist generation
- Manual NARA requests
- No Echo intelligence

### Premium Tier ($99/mo)
- Automated checklist generation
- Hazard mapping
- NARA automation
- Basic Echo AI insights (100 requests/day)

### Elite Tier (Service - $2,500 + 20%)
- Everything in Premium
- Full Echo intelligence integration
- Strategic case management
- Human analyst review
- Unlimited API access
