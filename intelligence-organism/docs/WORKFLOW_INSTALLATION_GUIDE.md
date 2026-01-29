# GitHub Actions Workflows - Installation Guide

**Status:** Manual Installation Required  
**Reason:** GitHub App permission restriction on workflow creation

## Overview

The Intelligence Organism requires 6 GitHub Actions workflows to operate autonomously. Due to permission restrictions, these workflows must be added manually through the GitHub web interface.

## Installation Steps

### Step 1: Navigate to GitHub Actions

1. Go to your repository: https://github.com/onlyecho822-source/Echo
2. Click on the "Actions" tab
3. Click "New workflow" or "set up a workflow yourself"

### Step 2: Create Each Workflow

For each of the 6 workflows below, create a new file in `.github/workflows/` with the exact filename and content provided.

---

## Workflow 1: EDGAR Monitor

**Filename:** `.github/workflows/edgar-monitor.yml`

```yaml
name: EDGAR Monitor - SEC Filings Ingestion

on:
  schedule:
    - cron: '0 * * * *'  # Every hour
  workflow_dispatch:

jobs:
  edgar-monitor:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          pip install requests beautifulsoup4 pandas
          
      - name: Run EDGAR monitor
        env:
          SEC_USER_AGENT: ${{ secrets.SEC_USER_AGENT }}
        run: |
          python intelligence-organism/agents/edgar_monitor.py
          
      - name: Commit and push data
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add intelligence-organism/data/raw/edgar/
          git diff --quiet && git diff --staged --quiet || git commit -m "EDGAR data update: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
          git push
```

---

## Workflow 2: FRED Economic Data

**Filename:** `.github/workflows/fred-economic-data.yml`

```yaml
name: FRED Economic Data - Meta-Intelligence Feed

on:
  schedule:
    - cron: '0 0 * * *'  # Daily at 00:00 UTC
  workflow_dispatch:

jobs:
  fred-data:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          pip install requests pandas
          
      - name: Fetch FRED data
        env:
          FRED_API_KEY: ${{ secrets.FRED_API_KEY }}
        run: |
          python intelligence-organism/agents/fred_monitor.py
          
      - name: Commit and push data
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add intelligence-organism/data/meta_intelligence/fred/
          git diff --quiet && git diff --staged --quiet || git commit -m "FRED data update: $(date -u +%Y-%m-%d)"
          git push
```

---

## Workflow 3: Primary Synthesis

**Filename:** `.github/workflows/primary-synthesis.yml`

```yaml
name: Primary Synthesis - Grand Master Report Generation

on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 06:00 UTC
  workflow_dispatch:

jobs:
  primary-synthesis:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          pip install openai requests pandas
          
      - name: Generate Grand Master Report
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          python intelligence-organism/agents/primary_synthesizer.py
          
      - name: Commit and push report
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add intelligence-organism/reports/primary_synthesis/
          git diff --quiet && git diff --staged --quiet || git commit -m "Primary Synthesis Report: $(date -u +%Y-%m-%d)"
          git push
```

---

## Workflow 4: Adversarial Synthesis

**Filename:** `.github/workflows/adversarial-synthesis.yml`

```yaml
name: Adversarial Synthesis - Red Team Report Generation

on:
  schedule:
    - cron: '30 6 * * *'  # Daily at 06:30 UTC
  workflow_dispatch:

jobs:
  adversarial-synthesis:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          pip install openai requests pandas
          
      - name: Generate Adversarial Brief
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          python intelligence-organism/agents/adversarial_synthesizer.py
          
      - name: Commit and push report
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add intelligence-organism/reports/adversarial_briefs/
          git diff --quiet && git diff --staged --quiet || git commit -m "Adversarial Brief: $(date -u +%Y-%m-%d)"
          git push
```

---

## Workflow 5: Meta-Intelligence Monitor

**Filename:** `.github/workflows/meta-intelligence-monitor.yml`

```yaml
name: Meta-Intelligence Monitor - Pattern Detection & Priority Interrupts

on:
  schedule:
    - cron: '*/15 * * * *'  # Every 15 minutes
  workflow_dispatch:

jobs:
  meta-intelligence:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          pip install requests pandas numpy scipy
          
      - name: Run Meta-Intelligence Substrate
        env:
          FRED_API_KEY: ${{ secrets.FRED_API_KEY }}
        run: |
          python intelligence-organism/agents/meta_intelligence.py
          
      - name: Commit and push alerts
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add intelligence-organism/alerts/meta_intelligence/
          git diff --quiet && git diff --staged --quiet || git commit -m "Meta-Intelligence Update: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
          git push
```

---

## Workflow 6: Chaos Monkey

**Filename:** `.github/workflows/chaos-monkey.yml`

```yaml
name: Chaos Monkey - Resilience Testing Protocol

on:
  schedule:
    - cron: '37 3 * * *'   # Random time 1
    - cron: '23 15 * * *'  # Random time 2
  workflow_dispatch:

jobs:
  chaos-monkey:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          pip install requests pyyaml
          
      - name: Execute Chaos Monkey
        run: |
          python intelligence-organism/agents/chaos_monkey.py
          
      - name: Commit and push logs
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add intelligence-organism/logs/chaos_monkey/
          git diff --quiet && git diff --staged --quiet || git commit -m "Chaos Monkey Execution: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
          git push
```

---

## Step 3: Configure Secrets

After creating all workflows, configure the required secrets:

1. Go to Settings → Secrets and variables → Actions
2. Add the following secrets:

| Secret Name | Description | How to Obtain |
|-------------|-------------|---------------|
| `FRED_API_KEY` | Federal Reserve Economic Data API key | Register at https://fred.stlouisfed.org/docs/api/api_key.html |
| `OPENAI_API_KEY` | OpenAI API key for synthesis agents | Get from https://platform.openai.com/api-keys |
| `SEC_USER_AGENT` | SEC EDGAR user agent string | Format: `YourName your.email@example.com` |

## Step 4: Enable Workflows

1. Go to the "Actions" tab
2. You may see a message about workflows needing approval
3. Click "I understand my workflows, go ahead and enable them"

## Step 5: Test the Deployment

1. Go to Actions → Select any workflow
2. Click "Run workflow" → "Run workflow"
3. Monitor the execution to ensure it completes successfully

## Verification Checklist

- [ ] All 6 workflow files created in `.github/workflows/`
- [ ] All 3 secrets configured
- [ ] Workflows enabled in Actions tab
- [ ] At least one workflow tested successfully
- [ ] Data directories populated after first runs

## Troubleshooting

**Issue:** Workflow fails with "permission denied"
- **Solution:** Ensure the repository has Actions enabled and workflows have write permissions

**Issue:** API rate limits
- **Solution:** Adjust cron schedules to reduce frequency

**Issue:** Secrets not found
- **Solution:** Double-check secret names match exactly (case-sensitive)

---

Once all workflows are installed and tested, the Intelligence Organism will be fully operational and autonomous.
