# 🚀 GitHub Actions Workflow Deployment Guide

**How to deploy the 4 autonomous arm workflows to GitHub**

## The 4 Workflows

All workflow files are ready in `.github/workflows/`:

1. **`archon_daily_report.yml`** - Daily intelligence reports (9 AM EST)
2. **`phoenix_weekly_scan.yml`** - Weekly global scans (Monday 10 AM EST)
3. **`devils_eye_monthly_audit.yml`** - Monthly quality audits (1st of month 8 AM EST)
4. **`sentinel_continuous_monitor.yml`** - Continuous monitoring (real-time)

## Why They're Not Pushed Yet

GitHub blocks workflow file creation/updates through GitHub Apps without explicit `workflows` permission. This is a security feature to prevent unauthorized automation.

## Deployment Options

### Option 1: Manual Upload via GitHub UI (Easiest)

**Step-by-step:**

1. Go to https://github.com/onlyecho822-source/Echo

2. Navigate to `.github/workflows/` directory
   - If it doesn't exist, create it: Click "Add file" → "Create new file"
   - Name it `.github/workflows/README.md` (to create the directory)

3. For each workflow file:
   - Click "Add file" → "Create new file"
   - Name it (e.g., `archon_daily_report.yml`)
   - Copy content from local file in `/home/ubuntu/Echo/.github/workflows/`
   - Paste into GitHub editor
   - Commit with message: "Add [workflow name] automation"

4. Repeat for all 4 workflows

**Pros:**
- No permission changes needed
- Works immediately
- Full control over each workflow

**Cons:**
- Manual process (4 files)
- Can't push workflow updates via git

### Option 2: Grant Workflow Permissions (Recommended for Automation)

**Step-by-step:**

1. Go to https://github.com/onlyecho822-source/Echo/settings/actions

2. Scroll to **"Workflow permissions"** section

3. Select **"Read and write permissions"**

4. Check **"Allow GitHub Actions to create and approve pull requests"**

5. Click **"Save"**

6. Then push workflows via git:
   ```bash
   cd /home/ubuntu/Echo
   git add .github/workflows/*.yml
   git commit -m "🤖 Add 4 autonomous arm workflows"
   git push origin feature/illinois-unclaimed-property-scanner
   ```

**Pros:**
- Future workflow updates can be pushed via git
- Enables full automation
- Workflows can self-update

**Cons:**
- Grants broader permissions to GitHub Actions
- Requires repository settings access

### Option 3: Use GitHub CLI (Alternative)

**Prerequisites:**
- GitHub CLI (`gh`) installed and authenticated
- Repository access

**Commands:**

```bash
cd /home/ubuntu/Echo

# For each workflow file
gh api repos/onlyecho822-source/Echo/contents/.github/workflows/archon_daily_report.yml \
  --method PUT \
  --field message="Add Archon daily report workflow" \
  --field content=@<(base64 -w 0 .github/workflows/archon_daily_report.yml)

gh api repos/onlyecho822-source/Echo/contents/.github/workflows/phoenix_weekly_scan.yml \
  --method PUT \
  --field message="Add Phoenix weekly scan workflow" \
  --field content=@<(base64 -w 0 .github/workflows/phoenix_weekly_scan.yml)

gh api repos/onlyecho822-source/Echo/contents/.github/workflows/devils_eye_monthly_audit.yml \
  --method PUT \
  --field message="Add Devil's Eye monthly audit workflow" \
  --field content=@<(base64 -w 0 .github/workflows/devils_eye_monthly_audit.yml)

gh api repos/onlyecho822-source/Echo/contents/.github/workflows/sentinel_continuous_monitor.yml \
  --method PUT \
  --field message="Add Sentinel continuous monitor workflow" \
  --field content=@<(base64 -w 0 .github/workflows/sentinel_continuous_monitor.yml)
```

**Pros:**
- Scriptable
- No manual copying
- Works from command line

**Cons:**
- Requires GitHub CLI setup
- Still subject to API rate limits

### Option 4: Create Pull Request with Workflows

**Step-by-step:**

1. Create a new branch specifically for workflows:
   ```bash
   cd /home/ubuntu/Echo
   git checkout -b add-autonomous-workflows
   ```

2. Add workflow files:
   ```bash
   git add .github/workflows/*.yml
   git commit -m "🤖 Add 4 autonomous arm workflows"
   git push origin add-autonomous-workflows
   ```

3. Create PR on GitHub:
   ```bash
   gh pr create \
     --title "Add 4 Autonomous Arm Workflows" \
     --body "Adds GitHub Actions workflows for Archon, Phoenix, Devil's Eye, and Sentinel autonomous arms"
   ```

4. Merge PR via GitHub UI

**Pros:**
- Review workflows before activation
- Clear audit trail
- Can discuss/modify before deployment

**Cons:**
- Extra step (PR review)
- Workflows don't run until merged to main

## Verifying Deployment

After deploying workflows, verify they're active:

1. Go to https://github.com/onlyecho822-source/Echo/actions

2. You should see 4 workflows listed:
   - ✅ Archon Daily Intelligence Report
   - ✅ Phoenix Weekly Global Scan
   - ✅ Devil's Eye Monthly Quality Audit
   - ✅ Sentinel Continuous Monitoring

3. Check workflow status:
   - Green checkmark = enabled
   - Yellow dot = scheduled but not run yet
   - Red X = error (check logs)

## Manual Trigger (Testing)

Each workflow has `workflow_dispatch` enabled for manual testing:

1. Go to https://github.com/onlyecho822-source/Echo/actions

2. Select a workflow (e.g., "Archon Daily Intelligence Report")

3. Click **"Run workflow"** button

4. Select branch (e.g., `feature/illinois-unclaimed-property-scanner`)

5. Click **"Run workflow"**

6. Watch execution in real-time

## Scheduled Execution Times

Once deployed, workflows will run automatically:

- **Archon**: Every day at 9:00 AM EST (14:00 UTC)
- **Phoenix**: Every Monday at 10:00 AM EST (15:00 UTC)
- **Devil's Eye**: 1st of every month at 8:00 AM EST (13:00 UTC)
- **Sentinel**: Real-time (on every issue, PR, comment, discussion event)

## Workflow Artifacts

Each workflow generates artifacts (reports) stored for:

- **Archon**: 90 days
- **Phoenix**: 365 days (1 year)
- **Devil's Eye**: 365 days (1 year)
- **Sentinel**: 30 days

Access artifacts:
1. Go to workflow run
2. Scroll to "Artifacts" section
3. Download report files

## Monitoring Workflow Execution

### GitHub Actions Dashboard

https://github.com/onlyecho822-source/Echo/actions

Shows:
- Recent workflow runs
- Success/failure status
- Execution duration
- Artifacts generated

### Email Notifications

GitHub sends email notifications for:
- Workflow failures
- First workflow run
- Scheduled runs (optional)

Configure in: Settings → Notifications → Actions

### Workflow Status Badge

Add to README.md:

```markdown
![Archon Daily Report](https://github.com/onlyecho822-source/Echo/actions/workflows/archon_daily_report.yml/badge.svg)
![Phoenix Weekly Scan](https://github.com/onlyecho822-source/Echo/actions/workflows/phoenix_weekly_scan.yml/badge.svg)
![Devil's Eye Audit](https://github.com/onlyecho822-source/Echo/actions/workflows/devils_eye_monthly_audit.yml/badge.svg)
![Sentinel Monitor](https://github.com/onlyecho822-source/Echo/actions/workflows/sentinel_continuous_monitor.yml/badge.svg)
```

## Troubleshooting

### Workflow Not Running

**Check:**
1. Workflow file syntax (YAML validation)
2. Cron schedule format (6-field format required)
3. Branch restrictions (workflows may be branch-specific)
4. Repository permissions (Actions enabled?)

**Fix:**
```bash
# Validate YAML syntax
yamllint .github/workflows/archon_daily_report.yml

# Check cron schedule
# Format: seconds minutes hours day-of-month month day-of-week
# Example: '0 14 * * *' = 14:00 UTC daily
```

### Permission Errors

**Error:** "refusing to allow a GitHub App to create or update workflow"

**Fix:** Use Option 1 (Manual Upload) or Option 2 (Grant Permissions)

### Workflow Fails on First Run

**Common causes:**
1. Missing dependencies (check `pip install` step)
2. Python import errors (check file paths)
3. Git push failures (check commit permissions)

**Debug:**
1. Check workflow logs in Actions tab
2. Look for red X next to failed step
3. Expand step to see error details
4. Fix issue and re-run workflow

### Knowledge Base Not Updating

**Check:**
1. Git config set correctly (email/name)
2. Push permissions enabled
3. Knowledge JSON files exist
4. No merge conflicts

**Fix:**
```bash
# Ensure knowledge files exist
touch knowledge/{patterns,failures,optimizations,discoveries,strategies}.json
echo "[]" > knowledge/patterns.json
# Repeat for other files

# Commit and push
git add knowledge/*.json
git commit -m "Initialize knowledge base"
git push
```

## Advanced: Workflow Customization

### Change Schedule

Edit cron expression in workflow file:

```yaml
on:
  schedule:
    - cron: '0 14 * * *'  # Change this
```

**Cron format:** `seconds minutes hours day-of-month month day-of-week`

Examples:
- `'0 0 9 * * *'` = 9:00 AM UTC daily
- `'0 0 15 * * 1'` = 3:00 PM UTC every Monday
- `'0 0 8 1 * *'` = 8:00 AM UTC on 1st of month
- `'0 */30 * * * *'` = Every 30 minutes

### Add Email Notifications

Add step to workflow:

```yaml
- name: Send email report
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 587
    username: ${{ secrets.GMAIL_USERNAME }}
    password: ${{ secrets.GMAIL_APP_PASSWORD }}
    subject: Archon Daily Intelligence Report
    to: onlyecho822@gmail.com
    from: archon@echo.automation
    body: file://report.md
```

**Setup:**
1. Create Gmail app password
2. Add secrets to GitHub: Settings → Secrets → Actions
3. Add `GMAIL_USERNAME` and `GMAIL_APP_PASSWORD`

### Add Slack Notifications

```yaml
- name: Notify Slack
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
    payload: |
      {
        "text": "Archon Daily Report Complete",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Archon Daily Intelligence Report*\nExecution completed successfully."
            }
          }
        ]
      }
```

### Add Discord Notifications

```yaml
- name: Notify Discord
  uses: sarisia/actions-status-discord@v1
  with:
    webhook: ${{ secrets.DISCORD_WEBHOOK }}
    title: "Archon Daily Report"
    description: "Intelligence report generated successfully"
    color: 0x00ff00
```

## Security Considerations

### Secrets Management

**Never commit:**
- API keys
- Passwords
- Tokens
- Private keys

**Use GitHub Secrets:**
1. Settings → Secrets → Actions
2. Click "New repository secret"
3. Add secret name and value
4. Reference in workflow: `${{ secrets.SECRET_NAME }}`

### Workflow Permissions

**Principle of least privilege:**
- Only grant permissions workflows actually need
- Use `permissions:` block in workflow:

```yaml
permissions:
  contents: write  # For git push
  issues: write    # For creating issues
  pull-requests: read  # For reading PRs
```

### Code Injection Prevention

**Never use:**
```yaml
run: echo ${{ github.event.issue.title }}  # UNSAFE
```

**Instead use:**
```yaml
run: echo "$ISSUE_TITLE"
env:
  ISSUE_TITLE: ${{ github.event.issue.title }}
```

## Next Steps

1. **Choose deployment option** (recommend Option 1 or 2)
2. **Deploy all 4 workflows**
3. **Test with manual trigger**
4. **Monitor first scheduled run**
5. **Check artifacts and reports**
6. **Enable email notifications** (optional)
7. **Watch collective intelligence evolve!**

## Support

**Issues:**
- GitHub Actions documentation: https://docs.github.com/en/actions
- Workflow syntax: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions
- Cron syntax: https://crontab.guru/

**Questions:**
- Check workflow logs first
- Review this guide
- Examine working workflow examples in `.github/workflows/`

---

**Remember:** The octopus nervous system is already working locally. These workflows just deploy it to run automatically on GitHub's infrastructure. The intelligence is in the code, not the platform. 🐙
