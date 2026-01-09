# EchoDNS: 72-Hour Launch & Deployment Guide

**Objective:** Deploy EchoDNS to production and secure the first paying customer within 72 hours.

**Project Manager:** Manus AI
**Founder & Executor:** Nathan Poinsette
**Date:** December 18, 2025

---

## 🚀 Part 1: The 4-Hour Production Deployment

This is a tactical, step-by-step guide to get EchoDNS from `localhost` to a live, customer-ready application.

### Prerequisites

- [ ] **Domain Name:** A registered domain for the service (e.g., `app.echodns.io`).
- [ ] **Hosting Provider Accounts:** Vercel (frontend), Railway or Render (backend), and Neon (database).
- [ ] **GitHub Repository:** `onlyecho822-source/Echo` with the `sherlock-hub` directory containing the EchoDNS code.

### The 4-Hour Countdown

#### **Hour 1: Infrastructure Setup (60 mins)**

1.  **Provision Production Database (20 mins)**
    *   Go to [Neon](https://neon.tech/).
    *   Create a new project.
    *   Create a new PostgreSQL database.
    *   Copy the **Connection String (URL)**. This is your `DATABASE_URL`.

2.  **Configure DNS (15 mins)**
    *   In your domain registrar, point your nameservers to Vercel.
    *   Create a subdomain for the backend API (e.g., `api.echodns.io`). You will point this to your Railway/Render service later.

3.  **Set Up Hosting Projects (25 mins)**
    *   Go to [Vercel](https://vercel.com/) and create a new project linked to your `onlyecho822-source/Echo` GitHub repository.
        *   Set the **Root Directory** to `sherlock-hub/frontend`.
        *   Vercel will automatically detect it's a Vite/React project.
    *   Go to [Railway](https://railway.app/) or [Render](https://render.com/) and create a new project for the backend.
        *   Link it to the same GitHub repository.
        *   Specify the `Dockerfile` path as `sherlock-hub/backend/Dockerfile`.

---

#### **Hour 2: Backend Deployment (60 mins)**

1.  **Configure Environment Variables (20 mins)**
    *   In your Railway/Render project dashboard, go to the "Variables" section.
    *   Add the following secrets:
        *   `DATABASE_URL`: The connection string from Neon.
        *   `SECRET_KEY`: Generate a new strong secret key (`openssl rand -hex 32`).
        *   `ALGORITHM`: `HS256`
        *   `ACCESS_TOKEN_EXPIRE_MINUTES`: `30`
        *   `GODADDY_API_KEY`: Your GoDaddy API key.
        *   `GODADDY_API_SECRET`: Your GoDaddy API secret.
        *   `NAMECHEAP_API_USER`, `NAMECHEAP_API_KEY`, `NAMECHEAP_CLIENT_IP`

2.  **Deploy the Backend Container (30 mins)**
    *   Trigger a new deployment in Railway/Render.
    *   The service will build the `Dockerfile` from `sherlock-hub/backend/` and deploy the FastAPI application.
    *   Once deployed, Railway/Render will provide a public URL (e.g., `echodns-backend-prod.up.railway.app`).

3.  **Map Custom Domain (10 mins)**
    *   In your Railway/Render project, add a custom domain: `api.echodns.io`.
    *   Follow their instructions to add the CNAME record to your DNS settings.

---

#### **Hour 3: Frontend Deployment (60 mins)**

1.  **Configure Frontend Environment (20 mins)**
    *   In your Vercel project dashboard, go to "Environment Variables".
    *   Add the following variable:
        *   `VITE_API_URL`: `https://api.echodns.io` (your production backend URL).

2.  **Deploy the Frontend (40 mins)**
    *   Trigger a new deployment in Vercel from the `main` branch.
    *   Vercel will build the React app and deploy it to its global CDN.
    *   Add your custom domain (e.g., `app.echodns.io`) in the Vercel project settings.

---

#### **Hour 4: Final Testing & Go-Live (60 mins)**

1.  **End-to-End Testing (30 mins)**
    *   Navigate to `https://app.echodns.io`.
    *   Create a new user account.
    *   Log in and log out.
    *   Connect to a registrar API.
    *   Perform a bulk domain operation.
    *   Verify the audit log is working.

2.  **Set Up Monitoring (15 mins)**
    *   Go to [UptimeRobot](https://uptimerobot.com/).
    *   Add new monitors for `https://app.echodns.io` and `https://api.echodns.io/health`.
    *   Set up email/SMS alerts for downtime.

3.  **Go-Live (15 mins)**
    *   Confirm all systems are operational.
    *   Prepare for the first outreach emails.
    *   **The system is now live.**

---

## 🎯 Part 2: The 72-Hour Customer Sprint

### **Day 1 (Hours 0-24): Deployment & Outreach**

*   **[0-4 hours]** Execute the 4-hour deployment plan above.
*   **[4-6 hours]** Send personalized outreach emails to the 10 identified MSP prospects. Use the templates I will provide in the next step.
*   **Goal:** Book 3+ demos.

### **Day 2 (Hours 24-48): Demos & Feedback**

*   Follow up with prospects who haven't responded.
*   Conduct the first demos using the script I will provide.
*   Listen carefully to objections and feedback. Refine the pitch.
*   **Goal:** Secure 1 verbal commitment ("We want this").

### **Day 3 (Hours 48-72): Close First Customer**

*   Send a simple contract and a Stripe payment link to the committed prospect.
*   Once payment is received, onboard the customer.
*   Provide them with their login and initial support.
*   **Goal:** **First Revenue Received.**

---

## 📈 Success Metrics for This Sprint

- [ ] **EchoDNS Deployed to Production:** `app.echodns.io` is live.
- [ ] **10 Outreach Emails Sent:** All prospects contacted.
- [ ] **3+ Demos Booked:** Confirmed meetings in the calendar.
- [ ] **1 Paying Customer:** Contract signed and payment received.
- [ ] **First Revenue in Bank:** Money transferred to your CashApp/Santa Cruz account.

This plan is aggressive but 100% achievable. Let's execute.
