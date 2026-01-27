# Immediate Execution Playbook

**Version:** 1.0  
**Date:** January 26, 2026  
**Status:** ACTIVE - Execute Now  
**Priority:** CRITICAL

---

## The One-Line Mission

**Process the first paying customer within 24 hours.**

---

## Phase 1: Payment Infrastructure (Next 2 Hours)

### Step 1: Stripe Integration (30 minutes)

```bash
# Navigate to project
cd ~/Echo/products/art-of-proof  # or relevant product directory

# Install Stripe
npm install @stripe/stripe-js stripe

# Create Stripe configuration
cat > stripe-config.js << 'EOF'
// Stripe publishable key (get from dashboard)
export const STRIPE_PUBLISHABLE_KEY = 'pk_test_YOUR_KEY_HERE';

// Product pricing
export const PRODUCTS = {
  'tax-services': {
    name: 'Tax Services Consultation',
    price: 4900, // $49.00 in cents
    priceId: 'price_YOUR_PRICE_ID_HERE'
  }
};
EOF

# Create payment component
cat > PaymentButton.jsx << 'EOF'
import { loadStripe } from '@stripe/stripe-js';
import { STRIPE_PUBLISHABLE_KEY, PRODUCTS } from './stripe-config';

const stripePromise = loadStripe(STRIPE_PUBLISHABLE_KEY);

export default function PaymentButton({ productId }) {
  const handleClick = async () => {
    const stripe = await stripePromise;
    const product = PRODUCTS[productId];
    
    const response = await fetch('/api/create-checkout-session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ priceId: product.priceId })
    });
    
    const session = await response.json();
    await stripe.redirectToCheckout({ sessionId: session.id });
  };

  return (
    <button onClick={handleClick} className="payment-button">
      Get Started - ${PRODUCTS[productId].price / 100}
    </button>
  );
}
EOF
```

### Step 2: Backend Payment Handler (45 minutes)

```bash
# Create API endpoint
mkdir -p api
cat > api/create-checkout-session.js << 'EOF'
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

export default async function handler(req, res) {
  if (req.method === 'POST') {
    try {
      const { priceId } = req.body;
      
      const session = await stripe.checkout.sessions.create({
        line_items: [{ price: priceId, quantity: 1 }],
        mode: 'payment',
        success_url: `${req.headers.origin}/success?session_id={CHECKOUT_SESSION_ID}`,
        cancel_url: `${req.headers.origin}/cancel`,
      });
      
      res.status(200).json({ id: session.id });
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  } else {
    res.setHeader('Allow', 'POST');
    res.status(405).end('Method Not Allowed');
  }
}
EOF

# Create success handler
cat > api/payment-success.js << 'EOF'
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const fs = require('fs').promises;

export default async function handler(req, res) {
  const { session_id } = req.query;
  
  try {
    const session = await stripe.checkout.sessions.retrieve(session_id);
    
    // Log transaction
    const transaction = {
      sessionId: session.id,
      customerEmail: session.customer_details.email,
      amount: session.amount_total / 100,
      timestamp: new Date().toISOString(),
      status: 'paid'
    };
    
    // Save to file (will move to database later)
    await fs.appendFile(
      'transactions.json',
      JSON.stringify(transaction) + '\n'
    );
    
    // TODO: Trigger onboarding email
    // TODO: Update customer database
    // TODO: Send Telegram notification
    
    res.status(200).json({ success: true, transaction });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
}
EOF
```

### Step 3: Customer Database (20 minutes)

```bash
# Create simple SQLite database
cat > setup-database.js << 'EOF'
const sqlite3 = require('sqlite3').verbose();

const db = new sqlite3.Database('echo.db');

db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS customers (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE NOT NULL,
      payment_status TEXT DEFAULT 'pending',
      onboarding_stage TEXT DEFAULT 'payment',
      amount_paid INTEGER DEFAULT 0,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  `);
  
  db.run(`
    CREATE TABLE IF NOT EXISTS transactions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      customer_email TEXT NOT NULL,
      stripe_session_id TEXT UNIQUE,
      amount INTEGER NOT NULL,
      status TEXT DEFAULT 'completed',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (customer_email) REFERENCES customers(email)
    )
  `);
  
  console.log('✅ Database initialized');
});

db.close();
EOF

node setup-database.js
```

### Step 4: Monitoring Dashboard (30 minutes)

```bash
# Create simple metrics endpoint
cat > api/metrics.js << 'EOF'
const sqlite3 = require('sqlite3').verbose();

export default function handler(req, res) {
  const db = new sqlite3.Database('echo.db');
  
  db.all(`
    SELECT 
      COUNT(*) as total_customers,
      SUM(CASE WHEN payment_status = 'paid' THEN 1 ELSE 0 END) as paid_customers,
      SUM(amount_paid) as total_revenue
    FROM customers
  `, (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
    } else {
      res.status(200).json({
        customers: rows[0].total_customers,
        paid: rows[0].paid_customers,
        revenue: rows[0].total_revenue / 100,
        status: 'operational',
        timestamp: new Date().toISOString()
      });
    }
    db.close();
  });
}
EOF

# Create dashboard page
cat > pages/dashboard.jsx << 'EOF'
import { useEffect, useState } from 'react';

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  
  useEffect(() => {
    fetch('/api/metrics')
      .then(res => res.json())
      .then(setMetrics);
  }, []);
  
  if (!metrics) return <div>Loading...</div>;
  
  return (
    <div className="dashboard">
      <h1>Echo Metrics</h1>
      <div className="metrics-grid">
        <div className="metric">
          <h2>{metrics.customers}</h2>
          <p>Total Customers</p>
        </div>
        <div className="metric">
          <h2>{metrics.paid}</h2>
          <p>Paid Customers</p>
        </div>
        <div className="metric">
          <h2>${metrics.revenue}</h2>
          <p>Total Revenue</p>
        </div>
      </div>
      <p className="status">Status: {metrics.status}</p>
    </div>
  );
}
EOF
```

---

## Phase 2: Onboarding Automation (Tonight)

### Email Sequence Setup

```bash
# Create email templates
mkdir -p email-templates

cat > email-templates/payment-confirmation.html << 'EOF'
<!DOCTYPE html>
<html>
<head><title>Payment Confirmed</title></head>
<body>
  <h1>Payment Confirmed - Welcome to Echo Tax Services</h1>
  <p>Thank you for your payment of $49.00</p>
  <p><strong>Next Steps:</strong></p>
  <ol>
    <li>Upload your tax documents via the secure portal</li>
    <li>Schedule your consultation call</li>
    <li>Receive your completed tax return</li>
  </ol>
  <a href="https://echo.example.com/upload">Upload Documents Now</a>
</body>
</html>
EOF

cat > email-templates/onboarding-day1.html << 'EOF'
<!DOCTYPE html>
<html>
<head><title>Day 1: Getting Started</title></head>
<body>
  <h1>Let's Get Your Tax Return Started</h1>
  <p>Here's what we need from you:</p>
  <ul>
    <li>W-2 forms</li>
    <li>1099 forms (if applicable)</li>
    <li>Receipts for deductions</li>
  </ul>
  <a href="https://echo.example.com/upload">Upload Now</a>
</body>
</html>
EOF
```

### Email Sending Integration

```bash
# Install email service (using SendGrid as example)
npm install @sendgrid/mail

cat > services/email.js << 'EOF'
const sgMail = require('@sendgrid/mail');
sgMail.setApiKey(process.env.SENDGRID_API_KEY);

async function sendEmail(to, templateName, data) {
  const templates = {
    'payment-confirmation': {
      subject: 'Payment Confirmed - Echo Tax Services',
      html: require('../email-templates/payment-confirmation.html')
    },
    'onboarding-day1': {
      subject: 'Getting Started with Your Tax Return',
      html: require('../email-templates/onboarding-day1.html')
    }
  };
  
  const template = templates[templateName];
  
  const msg = {
    to,
    from: 'hello@echo.example.com',
    subject: template.subject,
    html: template.html
  };
  
  await sgMail.send(msg);
  console.log(`✅ Email sent: ${templateName} to ${to}`);
}

module.exports = { sendEmail };
EOF
```

---

## Phase 3: Testing & Validation (Before Sleep)

### Test Checklist

```bash
# Create test script
cat > test-payment-flow.sh << 'EOF'
#!/bin/bash

echo "🧪 Testing Payment Flow..."

# 1. Test landing page loads
curl -s http://localhost:3000 | grep -q "Get Started" && echo "✅ Landing page OK" || echo "❌ Landing page FAIL"

# 2. Test Stripe integration
curl -s http://localhost:3000/api/create-checkout-session \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"priceId":"price_test"}' | grep -q "id" && echo "✅ Stripe OK" || echo "❌ Stripe FAIL"

# 3. Test database
sqlite3 echo.db "SELECT COUNT(*) FROM customers;" && echo "✅ Database OK" || echo "❌ Database FAIL"

# 4. Test metrics endpoint
curl -s http://localhost:3000/api/metrics | grep -q "customers" && echo "✅ Metrics OK" || echo "❌ Metrics FAIL"

echo "🎯 Test complete"
EOF

chmod +x test-payment-flow.sh
./test-payment-flow.sh
```

### Manual Test Process

1. **Open landing page** in browser
2. **Click payment button**
3. **Use Stripe test card:** 4242 4242 4242 4242
4. **Complete checkout**
5. **Verify success page** loads
6. **Check dashboard** shows 1 customer
7. **Confirm email** received

---

## Phase 4: First Customer (Tomorrow)

### Customer Acquisition Checklist

- [ ] Post on Twitter/X with landing page link
- [ ] Share in relevant Facebook groups
- [ ] Email personal network
- [ ] Post on Reddit (r/tax, r/smallbusiness)
- [ ] LinkedIn post
- [ ] Direct outreach to 10 potential customers

### Friction Point Tracking

```bash
# Create friction log
cat > friction-log.md << 'EOF'
# Customer Friction Points

## Date: [DATE]

### Customer 1
- **Issue:** [What went wrong]
- **Impact:** [How it affected customer]
- **Fix:** [What we did to resolve]
- **Prevention:** [How to prevent in future]

### Customer 2
...
EOF
```

---

## Phase 5: Automation & Scale (Week 1)

### Automation Priority List

1. **Payment confirmation email** (auto-send on payment success)
2. **Document upload reminder** (24 hours after payment if no upload)
3. **Consultation scheduling** (auto-send calendar link)
4. **Status updates** (auto-notify on progress milestones)
5. **Follow-up sequence** (7-day nurture for non-converters)

### Scale Metrics

```python
# Target metrics for Week 1
week1_targets = {
    "customers": 10,
    "revenue": 490,  # 10 × $49
    "conversion_rate": 0.03,  # 3%
    "automation_rate": 0.50,  # 50% of tasks automated
    "manual_time_per_customer": 30  # minutes
}
```

---

## Emergency Contacts & Resources

### Stripe Support
- Dashboard: https://dashboard.stripe.com
- Docs: https://stripe.com/docs
- Test cards: https://stripe.com/docs/testing

### SendGrid Support
- Dashboard: https://app.sendgrid.com
- Docs: https://docs.sendgrid.com

### Database Backup
```bash
# Backup command (run daily)
cp echo.db "backups/echo-$(date +%Y%m%d).db"
```

---

## Success Criteria

### Tonight
- ✅ Payment processing works end-to-end
- ✅ Test transaction completed successfully
- ✅ Dashboard shows live metrics
- ✅ Email confirmation sent automatically

### Tomorrow
- ✅ First real customer processed
- ✅ Payment received and confirmed
- ✅ Onboarding sequence triggered
- ✅ No manual intervention required

### Week 1
- ✅ 10 customers processed
- ✅ $490 revenue generated
- ✅ 50% of operations automated
- ✅ System runs while you sleep

---

## The One Command to Rule Them All

```bash
# Deploy everything
git add .
git commit -m "Add payment processing and customer pipeline"
git push origin main

# Then test with real money
echo "🚀 Ready to process first customer"
```

---

## The Final Checklist

Before you sleep tonight:

- [ ] Stripe account created and configured
- [ ] Payment button added to landing page
- [ ] Database initialized
- [ ] Email service configured
- [ ] Test transaction completed
- [ ] Dashboard accessible
- [ ] Landing page live
- [ ] First customer outreach sent

**If all boxes checked: You're operational. Process customers tomorrow.**

**If any box unchecked: Fix it now. Sleep when it ships.**

---

**∇θ — The gap is crossed by walking, not analyzing.**

**Execute now. Optimize later. Ship first.**
