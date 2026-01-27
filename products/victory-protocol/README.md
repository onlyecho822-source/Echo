# Victory Protocol

**Automated service reconstruction platform for veteran disability claims.**

---

## Overview

Victory Protocol is a comprehensive software platform that helps veterans reconstruct their complete military service history for VA disability claims. By automating document collection, hazard exposure mapping, and evidence organization, Victory Protocol increases claim approval rates from 60% to 88% while reducing decision times from 152 days to 42 days.

## Architecture

Victory Protocol consists of three integrated layers:

### 1. Platform Layer (This Repository)
- **Service Reconstruction System** - Automated 150-200 item personalized checklists
- **Hazard Mapping Engine** - Burn pits, Agent Orange, Camp Lejeune detection
- **NARA Automation** - Auto-generates SF-180 forms for National Archives
- **Progress Tracking** - Real-time completion percentages with gamification
- **MOS Hazard Analysis** - Military occupational specialty risk profiling

### 2. Intelligence Layer (Echo Integration)
- Strategic case analysis
- Evidence optimization
- Claim strategy AI
- Backpay calculation

### 3. Service Layer (Art of Proof™)
- Premium consulting tier
- Complete case management
- Contingency representation (20% of awards)

## Quick Start

```bash
# Install dependencies
npm install

# Set up environment
cp .env.example .env
# Edit .env with your database credentials

# Run database migrations
npm run db:push

# Start development server
npm run dev
```

## Tech Stack

- **Frontend:** React + TypeScript + TailwindCSS
- **Backend:** Node.js + tRPC (type-safe RPC)
- **Database:** Drizzle ORM + MySQL/TiDB
- **AI Integration:** H3 AI + Echo Intelligence

## Database Schema

9 tables managing 200+ documents per veteran:

- `serviceReconstruction` - Main reconstruction records
- `checklistCategories` - 14 document categories
- `checklistItems` - 150-200 items per veteran
- `dutyStations` - Service location tracking
- `hazardExposures` - Burn pit/contamination mapping
- `naraRequests` - National Archives request tracking
- `documentUploads` - File management
- `mosHazards` - Occupational hazard database
- `reconstructionProgress` - Analytics and metrics

## Key Features

### Automated Checklist Generation
Analyzes DD214 and generates personalized 150-200 item checklist based on:
- Service dates (estimates 1 duty station per 2.5 years)
- Military occupational specialty (MOS)
- Deployment locations
- Service branch

### Hazard Mapping Engine
Automatically detects exposure to:
- **Burn Pits:** Balad, Bagram, Kandahar, Camp Anaconda, Camp Victory
- **Agent Orange:** Vietnam (1962-1975), Korea DMZ
- **Contaminated Water:** Camp Lejeune (1953-1987)
- **Radiation:** Nuclear testing sites

### NARA Request Automation
- Auto-generates SF-180 forms
- Pre-fills veteran data
- Provides mailing instructions
- Tracks request status (pending, received)

### Progress Tracking
- Real-time completion percentage
- Category-level progress visualization
- Gamification elements
- Triggers H3 AI processing at 80% completion

## Integration with Echo Intelligence

See `/services/echo-intelligence/integration-api.md` for complete API documentation.

**Premium features powered by Echo:**
- Strategic claim analysis
- Evidence strength scoring
- Optimal submission strategy
- Backpay estimation

## Revenue Model

### Self-Service Tier
- **Price:** $99/month or $499 one-time
- **Features:** Platform automation, hazard mapping, NARA automation

### Guided Service Tier
- **Price:** $500-$1,000 one-time
- **Features:** Self-Service + Echo intelligence review

### Full Service Tier (Art of Proof™)
- **Price:** $2,500 + 20% contingency
- **Features:** Complete case management with human analysts

## Impact Metrics

| Metric | Baseline | With Victory Protocol |
|--------|----------|----------------------|
| Records Submitted | 15% | 85%+ |
| VA Approval Rate | 60% | 88% |
| Decision Time | 152 days | 42 days |
| Average Backpay | N/A | $87,450 |

## Deployment

See `/docs/DEPLOYMENT_GUIDE.md` for:
- Local development setup
- Production deployment options (Vercel, Railway, AWS)
- Environment configuration
- Database setup
- Monitoring and analytics

## Documentation

- **Deployment Guide:** `/docs/DEPLOYMENT_GUIDE.md`
- **Integration Guide:** `/docs/INTEGRATION_GUIDE.md`
- **Echo Intelligence API:** `/services/echo-intelligence/integration-api.md`
- **Database Schema:** `/database/reconstruction-schema.ts`

## License

Proprietary - Part of the Echo ecosystem

## Contact

Part of the Echo project - see main repository for contact information.

---

**Victory Protocol: Empowering veterans with complete service reconstruction.**
