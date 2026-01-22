# EchoNate Nexus - Alternative Data Signal Detection Platform

A sophisticated market signal detection platform that correlates alternative data sources (seismic activity, health outbreaks, social sentiment, solar weather, forex movements, crypto trends, and geopolitical events) with potential market impacts.

## Overview

EchoNate Nexus transforms unconventional data streams into actionable trading signals using correlation analysis and Bayesian confidence scoring. The platform provides real-time alerts, historical accuracy tracking, and programmatic API access for quantitative traders and institutional investors.

## Features

### Live Data Source Connectors
- **USGS Earthquake API**: Real-time seismic activity monitoring (M4.5+ events)
- **Disease.sh Health API**: Global health outbreak tracking (COVID-19, epidemics)
- **NASA DONKI Solar Weather**: Solar flares and geomagnetic storm detection
- **News Sentiment Analysis**: Social and news sentiment correlation

### Real-Time WebSocket Streaming
- **Sub-second signal delivery**: New signals pushed instantly to connected clients
- **Subscription-based filtering**: Subscribe to specific signal types
- **Auto-reconnection**: Resilient connection with exponential backoff
- **Heartbeat monitoring**: Connection health verification every 30 seconds

### Core Signal Detection
- **7 Signal Types**: Seismic, Health, Sentiment, Solar/Weather, Forex, Crypto, Geopolitical
- **Real-time Correlation Engine**: Detects patterns between alternative data and market movements
- **Confidence Scoring**: Each signal includes strength (0-100%) and confidence (0-100%) metrics
- **Direction Prediction**: Bullish, Bearish, or Neutral market direction forecasts

### User Features
- **Tiered Access**:
  - **Free**: 7-day delayed signals, basic dashboard
  - **Pro** ($49/mo): Real-time signals, full history, API access (100 calls/day)
  - **Enterprise** ($199/mo): Unlimited API, webhooks, custom configurations
- **Custom Watchlists**: Track specific tickers with personalized alert thresholds
- **Bookmarking**: Save signals for later review
- **Export**: Download signals as JSON for external analysis

### Analytics & Accuracy
- **Bayesian Accuracy Tracking**: Uses Beta-Binomial model for robust accuracy estimation
- **95% Confidence Intervals**: Quantifies uncertainty in accuracy metrics
- **Signal Type Performance**: Track which signal types perform best
- **Outcome Validation**: Record and track signal outcomes over time

### API Access
- **RESTful API**: Programmatic access to signals for Pro/Enterprise users
- **API Key Management**: Create, revoke, and monitor API keys
- **Rate Limiting**: Tier-based rate limits (100/day Pro, unlimited Enterprise)
- **Webhook Ingestion**: Accept signals from external sources (GitHub agents)

### Payments & Subscriptions
- **Stripe Integration**: Secure payment processing
- **Subscription Management**: Upgrade, downgrade, cancel subscriptions
- **Order History**: View past purchases and invoices
- **Promo Codes**: Support for discount codes

## Tech Stack

### Frontend
- **React 19** with TypeScript
- **Tailwind CSS 4** for styling
- **shadcn/ui** component library
- **Wouter** for routing
- **tRPC** for type-safe API calls

### Backend
- **Express 4** server
- **tRPC 11** for API procedures
- **Drizzle ORM** for database operations
- **MySQL/TiDB** database
- **Stripe** for payments

### Infrastructure
- **Manus OAuth** for authentication
- **S3** for file storage
- **Built-in notification system** for alerts

## Project Structure

```
echonate-nexus/
├── client/
│   ├── src/
│   │   ├── pages/           # Page components
│   │   │   ├── Home.tsx     # Landing page
│   │   │   ├── Dashboard.tsx # Main signal dashboard
│   │   │   ├── Pricing.tsx  # Subscription plans
│   │   │   ├── Settings.tsx # User preferences
│   │   │   ├── Watchlist.tsx # Custom watchlists
│   │   │   ├── Analytics.tsx # Performance metrics
│   │   │   ├── ApiKeys.tsx  # API key management
│   │   │   └── Orders.tsx   # Payment history
│   │   ├── components/      # Reusable UI components
│   │   ├── contexts/        # React contexts
│   │   └── lib/            # Utilities and tRPC client
│   └── public/             # Static assets
├── server/
│   ├── _core/              # Framework internals
│   ├── routers.ts          # tRPC procedures
│   ├── db.ts               # Database queries
│   ├── api.ts              # Public REST API
│   ├── products.ts         # Stripe products
│   ├── stripeWebhook.ts    # Payment webhooks
│   └── emailAlerts.ts      # Notification service
├── drizzle/
│   └── schema.ts           # Database schema
└── shared/                 # Shared types and constants
```

## Database Schema

### Core Tables
- `users` - User accounts with OAuth integration
- `subscriptions` - User subscription tiers and Stripe data
- `signals` - Detected market signals
- `alertPreferences` - User notification settings
- `alertLogs` - Alert delivery tracking

### Feature Tables
- `watchlists` - Custom ticker watchlists
- `bookmarks` - Saved signals
- `apiKeys` - API key management
- `orders` - Payment history

### Analytics Tables
- `signalAccuracy` - Bayesian accuracy tracking per signal type
- `signalValidations` - Outcome validation records
- `webhookEvents` - External signal ingestion log
- `apiUsage` - API call tracking

## WebSocket API

### Connection
```javascript
const ws = new WebSocket('wss://your-domain.com/ws');

ws.onmessage = (event) => {
  const { type, data, timestamp } = JSON.parse(event.data);
  if (type === 'signal') {
    console.log('New signal:', data.title);
  }
};
```

### Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `signal` | Server → Client | New signal detected |
| `stats` | Server → Client | Connection stats, last fetch time |
| `ping` | Client → Server | Heartbeat request |
| `pong` | Server → Client | Heartbeat response |
| `subscribe` | Client → Server | Subscribe to signal types |
| `unsubscribe` | Client → Server | Unsubscribe from signal types |

### Subscribe to Signal Types
```javascript
ws.send(JSON.stringify({
  type: 'subscribe',
  data: { signalTypes: ['seismic', 'health', 'solar'] },
  timestamp: Date.now()
}));
```

## REST API Reference

### Authentication
```bash
# Include API key in Authorization header
curl -H "Authorization: Bearer echo_your_api_key" \
  https://your-domain.com/api/v1/signals
```

### Endpoints

#### GET /api/v1/signals
List signals with optional filters.

Query Parameters:
- `limit` (number, default: 20): Max signals to return
- `offset` (number, default: 0): Pagination offset
- `signalType` (string): Filter by signal type
- `direction` (string): Filter by direction (bullish/bearish/neutral)
- `minConfidence` (number): Minimum confidence threshold

Response:
```json
{
  "signals": [...],
  "total": 150,
  "hasMore": true
}
```

#### GET /api/v1/signals/:id
Get detailed signal information.

#### GET /api/v1/signals/stats
Get aggregate statistics.

### Webhook Ingestion

POST signals from external sources:
```bash
curl -X POST https://your-domain.com/api/v1/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "source": "github-agent",
    "eventType": "signal.detected",
    "secret": "your-webhook-secret",
    "payload": {
      "signalType": "seismic",
      "title": "Major earthquake detected",
      ...
    }
  }'
```

## Bayesian Accuracy Methodology

The platform uses Bayesian inference for accuracy tracking:

1. **Prior**: Each signal type starts with Beta(1,1) - uniform prior
2. **Update**: On each outcome, update α (successes) or β (failures)
3. **Posterior Mean**: Accuracy = α / (α + β)
4. **Confidence Interval**: 95% credible interval from Beta distribution

Benefits:
- Accounts for uncertainty with small samples
- Regularizes toward 50% with limited data
- Confidence intervals narrow as data accumulates
- Resistant to overfitting

## Development

### Prerequisites
- Node.js 22+
- pnpm
- MySQL/TiDB database

### Setup
```bash
# Install dependencies
pnpm install

# Push database schema
pnpm db:push

# Start development server
pnpm dev
```

### Testing
```bash
# Run all tests
pnpm test

# Run specific test file
pnpm test server/signals.test.ts
```

### Environment Variables
Required environment variables are automatically injected by the Manus platform:
- `DATABASE_URL` - Database connection string
- `JWT_SECRET` - Session signing secret
- `STRIPE_SECRET_KEY` - Stripe API key
- `STRIPE_WEBHOOK_SECRET` - Stripe webhook verification

## Deployment

The application is deployed on the Manus platform with:
- Automatic SSL/TLS
- CDN distribution
- Database hosting
- File storage (S3)

To deploy:
1. Create a checkpoint: `webdev_save_checkpoint`
2. Click "Publish" in the Manus Management UI

## License

Proprietary - All rights reserved.

## Support

For support inquiries, contact the development team or submit issues through the GitHub repository.
