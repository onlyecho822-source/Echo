# EchoDispute Deployment Guide

## 🚀 Quick Start Deployment

### Prerequisites
1. GitHub account
2. Stripe account ([stripe.com](https://stripe.com))
3. OpenAI API account ([platform.openai.com](https://platform.openai.com))
4. Render.com account (free tier available) OR Heroku/Railway

---

## Option 1: Deploy to Render.com (RECOMMENDED)

### Step 1: Set Up API Keys

#### OpenAI API Key
1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Click "Create new secret key"
3. Copy the key (starts with `sk-`)
4. Save it securely

#### Stripe API Keys
1. Go to [dashboard.stripe.com/apikeys](https://dashboard.stripe.com/apikeys)
2. Copy your **Secret key** (starts with `sk_test_` or `sk_live_`)
3. Copy your **Publishable key** (starts with `pk_test_` or `pk_live_`)
4. For webhooks: Go to [dashboard.stripe.com/webhooks](https://dashboard.stripe.com/webhooks)
5. Click "Add endpoint"
6. Add URL: `https://your-app-name.onrender.com/webhook`
7. Select events: `checkout.session.completed`
8. Copy the webhook signing secret (starts with `whsec_`)

### Step 2: Deploy to Render

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Initial EchoDispute deployment"
   git push origin main
   ```

2. **Connect to Render**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Select the `Echo` repository

3. **Configure the service**
   - Name: `echodispute` (or your choice)
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `cd app && gunicorn app:app`

4. **Add Environment Variables**
   Click "Environment" and add:
   ```
   SECRET_KEY = [Generate random string]
   OPENAI_API_KEY = sk-your-openai-key
   STRIPE_SECRET_KEY = sk_test_your-stripe-key
   STRIPE_WEBHOOK_SECRET = whsec_your-webhook-secret
   DOMAIN = https://your-app-name.onrender.com
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait 5-10 minutes for first deploy
   - Your app will be live at `https://your-app-name.onrender.com`

### Step 3: Test Your Deployment

1. Visit your URL
2. Fill out the form with test data
3. Use Stripe test card: `4242 4242 4242 4242`
4. Any future expiry date, any 3-digit CVC
5. Complete purchase and verify PDF download works

---

## Option 2: Deploy to Heroku

```bash
# Install Heroku CLI
brew install heroku/brew/heroku  # Mac
# or download from heroku.com

# Login and create app
heroku login
heroku create your-app-name

# Set environment variables
heroku config:set OPENAI_API_KEY=sk-your-key
heroku config:set STRIPE_SECRET_KEY=sk_test_your-key
heroku config:set STRIPE_WEBHOOK_SECRET=whsec_your-secret
heroku config:set DOMAIN=https://your-app-name.herokuapp.com

# Deploy
git push heroku main

# Open your app
heroku open
```

---

## Option 3: Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repo
4. Add environment variables in the Variables tab
5. Railway will auto-detect Python and deploy

---

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | Any random string |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `STRIPE_SECRET_KEY` | Stripe secret key | `sk_test_...` |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook secret | `whsec_...` |
| `DOMAIN` | Your deployed URL | `https://yourapp.onrender.com` |

---

## Post-Deployment Checklist

### 1. Test the Full Flow
- [ ] Landing page loads correctly
- [ ] Form validation works
- [ ] Stripe checkout opens
- [ ] Payment processes (use test card)
- [ ] Success page shows
- [ ] PDF downloads correctly
- [ ] All letters are included

### 2. Configure Stripe
- [ ] Set up webhook endpoint
- [ ] Test webhook delivery
- [ ] Switch to live keys (when ready)
- [ ] Configure payment settings

### 3. Set Up Monitoring
- [ ] Check Render/Heroku logs
- [ ] Set up error alerts
- [ ] Monitor OpenAI API usage
- [ ] Track Stripe payments

### 4. Prepare for Launch
- [ ] Test on mobile devices
- [ ] Verify all email addresses
- [ ] Prepare marketing materials
- [ ] Set up customer support email

---

## Troubleshooting

### "Module not found" errors
```bash
# Make sure all dependencies are in requirements.txt
pip install -r requirements.txt
```

### PDF generation fails
- Check that `/tmp` directory is writable
- Verify ReportLab is installed correctly
- Check OpenAI API has sufficient credits

### Stripe checkout doesn't open
- Verify `STRIPE_SECRET_KEY` is set
- Check browser console for errors
- Ensure CORS is configured if using custom domain

### 502 Bad Gateway
- Check Render/Heroku logs
- Verify start command is correct
- Ensure all environment variables are set

---

## Costs Estimate

| Service | Free Tier | Paid |
|---------|-----------|------|
| Render.com | 750 hours/month free | $7/month for always-on |
| OpenAI GPT-4 | Pay-per-use | ~$0.03 per letter (2 letters) |
| Stripe | Free | 2.9% + $0.30 per transaction |

**Per customer cost:** ~$0.06 (OpenAI) + $2.48 (Stripe) = **~$2.54**
**Profit per customer:** $75 - $2.54 = **$72.46**

---

## Scaling Considerations

### For 10 customers/day (300/month):
- **Revenue:** $22,500
- **OpenAI costs:** ~$18
- **Stripe fees:** ~$742
- **Hosting:** $7
- **Net profit:** ~$21,733

### Performance optimizations:
1. Cache bureau addresses
2. Use GPT-3.5-turbo for cost savings (if quality acceptable)
3. Batch PDF generation
4. Consider Redis for session storage at scale

---

## Next Steps After Deployment

1. **Set up email delivery** (SendGrid, Mailgun, or AWS SES)
2. **Add analytics** (Google Analytics, Plausible)
3. **Implement email marketing** (ConvertKit, Mailchimp)
4. **Create refund workflow** in Stripe dashboard
5. **Build customer support system** (Help Scout, Intercom)

---

## Support

For technical issues:
- Check Render/Heroku logs first
- Review environment variables
- Test locally with `.env` file
- Contact support@echodispute.com

**You're now ready to launch! 🚀**
