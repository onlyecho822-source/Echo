# 🚀 Product Bloom Engine v1.2
**Commercial Foundation Edition**

AI-powered digital product generation platform built with Next.js 14, Prisma, PostgreSQL, Stripe, and OpenAI.

---

## 🏗️ Architecture

**Stack:**
- Next.js 14 (App Router)
- TypeScript
- Prisma ORM
- PostgreSQL
- NextAuth.js (Authentication)
- Stripe (Payments)
- OpenAI API (Generation)
- Zod (Validation)
- TailwindCSS

**Features:**
- ✅ User authentication (email/password)
- ✅ AI-powered product generation
- ✅ Product dashboard
- ✅ Stripe payment integration
- ✅ Secure API routes
- ✅ Input validation
- ✅ Responsive UI

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- PostgreSQL database
- OpenAI API key
- Stripe account (for payments)

### Installation

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# Initialize database
npx prisma migrate dev

# Generate Prisma client
npx prisma generate

# Run development server
npm run dev
```

Visit `http://localhost:3000`

---

## 🔐 Environment Variables

Create a `.env` file with:

```env
DATABASE_URL="postgresql://user:password@localhost:5432/productbloom"
OPENAI_API_KEY="sk-..."
STRIPE_SECRET_KEY="sk_test_..."
AUTH_SECRET="generate-with-openssl-rand-base64-32"
NEXTAUTH_URL="http://localhost:3000"
NEXT_PUBLIC_URL="http://localhost:3000"
```

Generate `AUTH_SECRET`:
```bash
openssl rand -base64 32
```

---

## 📁 Project Structure

```
product-bloom/
├── prisma/
│   └── schema.prisma          # Database schema
├── src/
│   ├── app/
│   │   ├── page.tsx           # Homepage (product generator)
│   │   ├── dashboard/         # User dashboard
│   │   ├── auth/              # Login/register pages
│   │   └── api/               # API routes
│   ├── lib/
│   │   ├── openai.ts          # OpenAI integration
│   │   ├── prisma.ts          # Database client
│   │   ├── stripe.ts          # Stripe client
│   │   └── auth.ts            # Auth configuration
│   ├── components/            # Reusable UI components
│   └── utils/
│       └── validators.ts      # Zod schemas
├── package.json
├── tsconfig.json
└── tailwind.config.js
```

---

## 🛣️ Routes

### Pages
- `/` - Product generation form
- `/dashboard` - User products list
- `/auth/login` - Sign in
- `/auth/register` - Create account

### API Endpoints
- `POST /api/generate` - Generate product
- `GET /api/products` - List user products
- `POST /api/checkout` - Create Stripe session
- `POST /api/auth/register` - User registration
- `POST /api/auth/[...nextauth]` - NextAuth handler

---

## 🔧 Commands

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Lint code

npx prisma studio           # Open database GUI
npx prisma migrate dev      # Create migration
npx prisma generate         # Generate client
```

---

## 🚢 Deployment

### Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Railway
```bash
# Install Railway CLI
npm i -g @railway/cli

# Deploy
railway up
```

**Environment Variables:**
Add all `.env` variables to your deployment platform.

**Database:**
Use managed PostgreSQL (Supabase, Railway, Neon).

---

## 🔒 Security Features

- ✅ Password hashing (bcrypt)
- ✅ JWT sessions
- ✅ Input validation (Zod)
- ✅ Protected API routes
- ✅ SQL injection prevention (Prisma)
- ✅ XSS protection

---

## 📊 Database Schema

**User**
- id (String, PK)
- email (String, unique)
- password (String, hashed)
- products (Product[])
- createdAt (DateTime)

**Product**
- id (String, PK)
- title (String)
- niche (String)
- audience (String)
- format (String)
- content (Text)
- userId (String, FK)
- createdAt (DateTime)

---

## 🎯 Usage Flow

1. User registers/logs in
2. Fills product generation form (title, niche, audience, format)
3. Submits to `/api/generate`
4. OpenAI generates product content
5. Product saved to database
6. User views product in dashboard

---

## 🧪 Testing

```bash
# Register a user
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Generate a product (requires auth)
curl -X POST http://localhost:3000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Fitness Guide",
    "niche": "Health",
    "audience": "Beginners",
    "format": "PDF"
  }'
```

---

## 📝 License

MIT License - Nathan Poinsette

---

## 🔗 Part of Echo Civilization

This engine is part of the **Echo Civilization** framework — a lawful, harmonic, multi-agent intelligence ecosystem.

**Echo Engines:**
- Product Bloom Engine (this repo)
- EchoClaim Engine (coming soon)
- EchoLex Engine (coming soon)

**Author:**
∇θ Operator: Nathan Poinsette
Founder • Archivist • Systems Engineer
