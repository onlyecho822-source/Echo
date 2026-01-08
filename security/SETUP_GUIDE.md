# Security Monitoring Setup Guide

**Complete instructions for configuring automated daily security vulnerability scanning and email reporting.**

---

## Quick Start (5 minutes)

### Step 1: Generate Gmail App Password

1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer" (or your device)
3. Click "Generate"
4. Copy the 16-character password

### Step 2: Add GitHub Secrets

1. Go to your repository: https://github.com/onlyecho822-source/Echo
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add:

| Name | Value |
|------|-------|
| `RECIPIENT_EMAIL` | `npoinsette@gmail.com` |
| `SMTP_SERVER` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SENDER_EMAIL` | `your-email@gmail.com` |
| `SENDER_PASSWORD` | `your-16-char-app-password` |

### Step 3: Verify Workflow

1. Go to **Actions** tab
2. Find "Daily Security Vulnerability Scan"
3. Verify it's enabled
4. Click **Run workflow** to test

✅ **Done!** Reports will be sent daily at 8:00 AM EST.

---

## Detailed Configuration

### Gmail Setup

**Prerequisites:**
- Gmail account
- 2-Factor Authentication enabled

**Steps:**

1. **Enable 2-Factor Authentication**
   - Go to https://myaccount.google.com/security
   - Click "2-Step Verification"
   - Follow the setup wizard

2. **Generate App Password**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Google will generate a 16-character password
   - Copy this password (you'll use it as `SENDER_PASSWORD`)

3. **Note Your Email**
   - Your Gmail address is your `SENDER_EMAIL`
   - Example: `nathan.poinsette@gmail.com`

### GitHub Secrets Configuration

**Access GitHub Secrets:**

1. Navigate to: https://github.com/onlyecho822-source/Echo/settings/secrets/actions
2. Click "New repository secret"
3. Add each secret one by one

**Required Secrets:**

```
RECIPIENT_EMAIL = npoinsette@gmail.com
SMTP_SERVER = smtp.gmail.com
SMTP_PORT = 587
SENDER_EMAIL = your-gmail@gmail.com
SENDER_PASSWORD = your-16-char-app-password
```

**Example Screenshot:**
```
Name: RECIPIENT_EMAIL
Value: npoinsette@gmail.com
[Add secret button]
```

### Workflow Configuration

The workflow is already configured in `.github/workflows/daily-security-scan.yml`

**Schedule:** 8:00 AM EST (13:00 UTC) daily

**To change the schedule:**
1. Edit `.github/workflows/daily-security-scan.yml`
2. Change the cron expression:
   ```yaml
   schedule:
     - cron: '0 13 * * *'  # Change this line
   ```
3. Commit and push

**Cron Format:** `minute hour day month weekday`

Examples:
- `0 13 * * *` - 8:00 AM EST daily
- `0 9 * * 1-5` - 4:00 AM EST weekdays only
- `0 13 * * 0` - 8:00 AM EST Sundays only

---

## Testing the Setup

### Test 1: Manual Workflow Trigger

1. Go to **Actions** → **Daily Security Vulnerability Scan**
2. Click **Run workflow** → **Run workflow**
3. Wait for it to complete
4. Check your email for the report

### Test 2: Test Email Sending

Run this Python script to test email configuration:

```python
#!/usr/bin/env python3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your-email@gmail.com"
SENDER_PASSWORD = "your-app-password"
RECIPIENT_EMAIL = "npoinsette@gmail.com"

try:
    # Create message
    msg = MIMEMultipart()
    msg["Subject"] = "Test Email from Echo Universe"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL

    body = "This is a test email from the Echo Universe security monitoring system."
    msg.attach(MIMEText(body, "plain"))

    # Send email
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())

    print("✅ Test email sent successfully!")

except Exception as e:
    print(f"❌ Error: {e}")
```

### Test 3: Run Security Scans Locally

```bash
cd /home/ubuntu/Echo
./security/run_security_scans.sh
```

Check the output in `security/scans/` and `security/reports/`

---

## Troubleshooting

### Problem: Email Not Received

**Check 1: Verify Secrets**
```bash
# Go to GitHub Settings → Secrets
# Verify all 5 secrets are present and correct
```

**Check 2: Check Workflow Logs**
1. Go to **Actions** → **Daily Security Vulnerability Scan**
2. Click the latest run
3. Click "send-email-report" step
4. Look for error messages

**Check 3: Test SMTP Connection**
```python
import smtplib
try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("your-email@gmail.com", "your-app-password")
    print("✅ Connection successful!")
except Exception as e:
    print(f"❌ Error: {e}")
```

**Check 4: Verify Gmail Settings**
- 2-Factor Authentication is enabled
- App Password is generated (not regular password)
- App Password is 16 characters
- Less secure apps are not being blocked

### Problem: Workflow Not Running

**Check 1: Workflow is Enabled**
1. Go to **Actions** tab
2. Click "Daily Security Vulnerability Scan"
3. Verify it shows "This workflow is active"

**Check 2: Check Cron Schedule**
1. Edit `.github/workflows/daily-security-scan.yml`
2. Verify cron expression: `0 13 * * *`
3. Note: GitHub Actions may have a 5-10 minute delay

**Check 3: Manual Trigger**
1. Go to **Actions** → **Daily Security Vulnerability Scan**
2. Click **Run workflow** → **Run workflow**
3. Check if it runs immediately

### Problem: Scans Not Completing

**Check 1: Missing Tools**
- npm: `npm --version`
- pip-audit: `pip-audit --version`
- GitHub CLI: `gh --version`

**Check 2: Missing Files**
- `sherlock-hub/frontend/package.json`
- `sherlock-hub/backend/requirements.txt`

**Check 3: Check Workflow Logs**
1. Go to **Actions** → Latest run
2. Click each step to see detailed logs
3. Look for error messages

---

## Advanced Configuration

### Send to Multiple Recipients

Edit `.github/workflows/daily-security-scan.yml`:

```yaml
- name: Send email report
  run: |
    REPORT_FILE="security/reports/security_report_$(date -u +%Y-%m-%d).json"
    python3 security/send_email_report.py "$REPORT_FILE" "email1@example.com"
    python3 security/send_email_report.py "$REPORT_FILE" "email2@example.com"
```

### Use Different SMTP Server

Change GitHub Secrets:
- `SMTP_SERVER`: Your SMTP server (e.g., `smtp.office365.com` for Outlook)
- `SMTP_PORT`: Your SMTP port (usually 587 or 25)
- `SENDER_EMAIL`: Your email address
- `SENDER_PASSWORD`: Your email password

### Custom Scan Schedule

Edit cron expression in `.github/workflows/daily-security-scan.yml`:

```yaml
schedule:
  - cron: '0 9,17 * * *'  # 4 AM and 12 PM EST
```

### Add Custom Scans

1. Create new scan script in `security/`
2. Add to `run_security_scans.sh`
3. Update GitHub Actions workflow

---

## Monitoring & Maintenance

### Daily Checks

- [ ] Check email for daily security report
- [ ] Review vulnerability summary
- [ ] Act on critical issues if any

### Weekly Checks

- [ ] Review vulnerability trends
- [ ] Check GitHub Actions logs
- [ ] Verify email delivery

### Monthly Checks

- [ ] Update scanning tools
- [ ] Review and update security policies
- [ ] Check GitHub Actions quota usage

---

## Email Report Contents

Each daily email includes:

1. **Vulnerability Summary**
   - Critical count
   - High count
   - Moderate count
   - Low count

2. **Recommendations**
   - Prioritized actions
   - Severity-based response times
   - Links to detailed information

3. **Scan Results**
   - NPM audit results
   - Python audit results
   - GitHub Dependabot results

4. **Links**
   - GitHub repository
   - Security settings
   - Detailed reports

---

## Security Best Practices

1. **Protect Secrets**
   - Never commit secrets to git
   - Use GitHub Secrets for sensitive data
   - Rotate app passwords regularly

2. **Review Reports**
   - Check email daily
   - Act on critical vulnerabilities immediately
   - Document all fixes

3. **Keep Tools Updated**
   - Update npm regularly
   - Update Python packages
   - Update scanning tools

4. **Monitor Trends**
   - Track vulnerability patterns
   - Identify recurring issues
   - Plan preventive measures

---

## Support

**For help with setup:**
- Email: contact@nathanpoinsette.com
- GitHub Issues: https://github.com/onlyecho822-source/Echo/issues

**For Gmail issues:**
- Gmail Help: https://support.google.com/mail
- App Passwords: https://support.google.com/accounts/answer/185833

**For GitHub issues:**
- GitHub Docs: https://docs.github.com
- GitHub Support: https://support.github.com

---

## Checklist

- [ ] Gmail 2-Factor Authentication enabled
- [ ] Gmail App Password generated
- [ ] GitHub Secrets configured (5 secrets)
- [ ] Workflow enabled in Actions tab
- [ ] Manual test run completed
- [ ] Email received successfully
- [ ] Scheduled workflow verified
- [ ] Documentation reviewed

---

**Built with ❤️ by Nathan Poinsette**
**Powered by Manus AI**
**Veteran-owned. Open Source. Always.**

**Last Updated:** December 18, 2025
**Status:** ✅ Ready for Configuration
