# Zapier Integration Test Suite

## What This Does
Tests your Zapier webhook connectivity to ensure the Sovereign OS can trigger automated actions.

---

## Prerequisites
- Python 3.7+ installed
- `requests` library: `pip install requests`
- Active Zapier account
- Zapier MCP connection re-authenticated (see below)

---

## STEP 1: Re-authenticate Zapier MCP

### Option A: Through Claude.ai Interface
1. Go to Claude.ai settings
2. Navigate to "Integrations" or "Connections"
3. Find "Zapier" in the list
4. Click "Reconnect" or "Re-authenticate"
5. Follow OAuth prompts
6. Confirm status shows "Active" or "Connected"

### Option B: Through Zapier.com
1. Go to https://zapier.com
2. Click your profile → "My Apps"
3. Find "Claude" or "Anthropic" integration
4. Click "Reconnect"
5. Complete authorization flow

**Checkpoint:** Make sure you see "Connected" status before proceeding.

---

## STEP 2: Create Your First Test Zap

### In Zapier:
1. Click **"Create Zap"**
2. **Trigger Setup:**
   - App: "Webhooks by Zapier"
   - Event: "Catch Hook"
   - Click "Continue"
   - **Copy the webhook URL** (looks like: `https://hooks.zapier.com/hooks/catch/123456/abcdef/`)
   
3. **Action Setup (Choose ONE):**
   
   **Option A - Email Test:**
   - App: "Gmail" or "Email by Zapier"
   - Action: "Send Email"
   - To: Your email address
   - Subject: "Zapier Test - Sovereign OS"
   - Body: `Test triggered at {{timestamp}}`
   
   **Option B - Google Sheets Test:**
   - App: "Google Sheets"
   - Action: "Create Spreadsheet Row"
   - Select your test spreadsheet
   - Map fields from webhook data

4. **Turn Zap ON**
5. **Name it:** "Sovereign OS - Test Webhook"

---

## STEP 3: Configure the Test Script

1. Open `zapier_config.json`
2. Replace `PASTE_YOUR_FEEDBACK_OS_WEBHOOK_URL_HERE` with your webhook URL
3. Save the file

### Example:
```json
{
  "zapier_webhooks": {
    "feedback_os": "https://hooks.zapier.com/hooks/catch/123456/abcdef/",
    "alerts": "PASTE_YOUR_ALERTS_WEBHOOK_URL_HERE",
    "logging": "PASTE_YOUR_LOGGING_WEBHOOK_URL_HERE"
  }
}
```

---

## STEP 4: Run the Test

```bash
python zapier_test.py
```

### Expected Output:
```
============================================================
ZAPIER INTEGRATION TESTER
============================================================

📋 TEST 1: Basic Connection
------------------------------------------------------------
🔄 Testing webhook: https://hooks.zapier.com/hooks/catch...
📦 Payload: {
  "event": "zapier_test",
  ...
}

✅ SUCCESS! Webhook triggered successfully.
   Status Code: 200
   Response: success

📋 TEST 2: Feedback OS Payload
------------------------------------------------------------
🧪 Testing Feedback OS payload format...
✅ Feedback OS format accepted!

============================================================
TEST SUMMARY
============================================================
Basic Test: ✅ PASS
Feedback OS Test: ✅ PASS

Next steps:
✅ All tests passed! Zapier integration is working.
✅ You can now connect Feedback OS to Zapier automation.
============================================================
```

---

## STEP 5: Verify Automation Works

### If you chose Email Test:
- Check your inbox
- You should receive 2 emails (one for each test)
- Subject: "Zapier Test - Sovereign OS"

### If you chose Google Sheets Test:
- Open your test spreadsheet
- You should see 2 new rows with test data

---

## Troubleshooting

### ❌ Test Failed with Connection Error
**Cause:** Can't reach Zapier webhook  
**Fix:** 
- Check internet connection
- Verify webhook URL is correct (no extra spaces)
- Make sure Zap is turned ON

### ❌ Test Failed with 404 Error
**Cause:** Webhook URL is invalid  
**Fix:**
- Double-check you copied the complete URL
- Verify the Zap still exists and is active
- Try creating a new Zap and getting a fresh webhook URL

### ❌ Webhook Triggers but No Email/Sheet Update
**Cause:** Action step in Zap is misconfigured  
**Fix:**
- Go to Zapier dashboard → "Zap History"
- Check if the Zap ran but the action failed
- Review action configuration in your Zap
- Test the action step manually

### ❌ Python Module Error
**Cause:** Missing `requests` library  
**Fix:**
```bash
pip install requests
```

---

## Next Steps After Success

Once tests pass, you can:

1. **Connect Feedback OS:**
   - Modify `feedback_minimal.py` to call this webhook
   - Every check-in triggers your Zap
   
2. **Create More Zaps:**
   - Alerts Zap: Send notifications on patterns
   - Logging Zap: Archive data to Google Sheets
   - Integration Zap: Connect to other services

3. **Build Automation:**
   - Morning check-in → Calendar block
   - Low energy detected → Adjust schedule
   - Pattern detected → Email yourself insights

---

## File Manifest

- `zapier_test.py` - Main test script
- `zapier_config.json` - Webhook URL configuration
- `README_ZAPIER.md` - This file

---

## Support

If you encounter issues:
1. Check Zapier dashboard → "Zap History" for error details
2. Verify webhook URL is exactly as Zapier provided
3. Ensure Zap is turned ON (toggle switch)
4. Test webhook manually in Zapier's interface first

---

## Success Criteria

✅ Python script runs without errors  
✅ Both tests show "PASS"  
✅ Email arrives or spreadsheet updates  
✅ Ready to integrate with Feedback OS

**Once all criteria met, Zapier fix is COMPLETE.**
