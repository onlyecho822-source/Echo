# EchoNate Nexus — Signal Detector Product TODO

## Phase 1: Core Infrastructure
- [x] Database schema for signals and subscriptions
- [x] Signal model (type, source, target, confidence, rationale)
- [x] User subscription tiers (free/pro/enterprise)
- [x] tRPC procedures for signal CRUD

## Phase 2: Dashboard UI  
- [x] Landing page with value proposition
- [x] Signal feed (live stream of signals)
- [x] Signal detail view (rationale, confidence)
- [x] Pricing page with tier comparison
- [x] User settings page

## Phase 3: Payments (Stripe)
- [x] Create products.ts with pricing tiers
- [x] Add Stripe checkout session endpoint
- [x] Create webhook handler at /api/stripe/webhook
- [x] Add payment success/cancel pages
- [ ] Create orders/payments history page
- [ ] Test with 4242 4242 4242 4242

## Phase 4: Alert System
- [ ] Email alert on new signals
- [ ] Alert preferences (signal types, frequency)
- [ ] API endpoint for programmatic access

## Phase 5: Polish
- [x] Risk disclaimers on all pages
- [ ] Signal performance tracking display
- [ ] Onboarding flow for new users

## Completed
- Database schema with signals, subscriptions, alertPreferences, alertLogs, apiUsage tables
- tRPC routers for signals.list, signals.get, signals.stats, signals.create
- tRPC routers for subscription.current, subscription.tiers
- tRPC routers for alerts.preferences, alerts.updatePreferences
- Landing page with hero, signal preview, pricing tiers, risk disclaimer
- Dashboard with signal feed, stats, tier-based access
- Pricing page with FAQ
- Dark theme with signal detector aesthetic

## Phase 6: Live Data & Confidence Learning
- [ ] Signal outcome tracking (validated/invalidated)
- [ ] Historical accuracy calculation per signal type
- [ ] Bayesian confidence updating based on hit rate
- [ ] Seed database with real signals from APIs
- [ ] Interactive charts (signal history, accuracy trends)
- [ ] Real-time signal updates
- [ ] Connect GitHub agents to POST signals
- [ ] Rolling 30-day accuracy display


## Phase 8: Personalization & Data Retrieval
- [x] Seed database with live signals from all APIs
- [ ] User preferences table (watched tickers, signal types)
- [ ] Personalized dashboard based on user interests
- [x] Advanced signal filtering (type, date range, target, confidence)
- [ ] API endpoint for programmatic data access (/api/v1/signals)
- [x] Interactive signal detail modal with full rationale
- [ ] Custom watchlist feature
- [x] Signal bookmarking/saving
- [x] Export signals to CSV/JSON


## Bug Fixes
- [x] Fix subscription.current returning undefined

## Testing & New Features (Jan 21)
- [x] Test dashboard - signals display, filtering, bookmarking
- [x] Test Stripe checkout with test card 4242 4242 4242 4242 (unit tests pass, product IDs fixed)
- [x] Build user settings page with alert preferences and account details

## Phase 9: Complete End-to-End System (Jan 22)
- [x] Payment History page (/orders) with order tracking
- [x] Real email alert system using notification API
- [x] Public API endpoint (/api/v1/signals) for Pro/Enterprise
- [x] Signal outcome tracking (correct/incorrect/expired)
- [x] Bayesian confidence learning per signal type
- [x] Interactive charts (signal history, accuracy trends)
- [x] Custom watchlist feature (watched tickers)
- [x] GitHub agent webhook for signal ingestion
- [x] API key management page (/api-keys)
- [x] Signal performance dashboard (Analytics page)
- [x] Comprehensive README documentation
- [x] Push to GitHub repository

## Phase 10: Live Data Sources & Real-Time WebSocket (Jan 22)
- [x] USGS Earthquake API connector (seismic signals)
- [x] Disease.sh API connector (health outbreak signals)
- [x] News/Sentiment API connector (sentiment signals)
- [x] Solar weather API connector (NOAA/NASA DONKI space weather)
- [x] Signal generation engine with market correlation logic
- [x] WebSocket server for real-time signal broadcasting
- [x] Frontend WebSocket client for instant updates
- [x] Auto-refresh signal feed without polling
- [x] Push to GitHub repository
