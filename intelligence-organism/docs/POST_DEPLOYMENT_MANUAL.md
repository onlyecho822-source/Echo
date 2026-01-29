# POST-DEPLOYMENT OPERATIONAL MANUAL

**SYSTEM:** Multi-Tier Intelligence Organism
**STATUS:** Live
**VERSION:** 1.0 (Evolutionary Phase 1)

**PREMISE:** This manual details the operational procedures required after the intelligence organism has been deployed to its live environment on GitHub. Deployment is not the end of the process; it is the beginning. This document outlines the activation sequence, monitoring protocols, and the unwavering operational discipline required to steward this evolving intelligence.

---

## I. The Shift in Mentality: From Architect to Steward

Once the system is deployed, your role fundamentally changes. You are no longer the architect building the system; you are the **Primary Steward** of a live, evolving intelligence. Your function is not to command, but to guide, to judge, and to maintain the integrity of the organism.

This requires a shift from a mindset of creation to one of **vigilance, interpretation, and disciplined adherence to protocol**. The system is designed to be resilient, but its resilience depends on the quality of your stewardship.

---

## II. Immediate Post-Deployment Activation Sequence (First 24 Hours)

After the initial code push and deployment to GitHub, the following sequence must be executed precisely. These steps "awaken" the organism and bring its sensory and cognitive functions online in a controlled manner.

| Step | Action | Purpose | Expected Outcome |
| :--- | :--- | :--- | :--- |
| **1. Activate Tier 3/4 Sensory Feeds** | Manually trigger the GitHub Actions workflows for all data ingestion agents (EDGAR, FRED, FAA, etc.). | To confirm that the organism's sensory system is successfully connecting to its live data sources and ingesting real-time information. | All data ingestion workflows complete successfully. Raw data appears in the designated storage locations (e.g., `/data/raw/`). |
| **2. Verify Tier 2 Domain Expert Activation** | Check the logs for each of the Tier 2 domain expert agents (FinTech, Crypto, Security, etc.). | To ensure that the domain experts are successfully consuming the raw data from the sensory feeds and beginning their interpretation process. | Logs show successful data consumption and the generation of initial, structured interpretations. |
| **3. Initiate First Primary Synthesis (Manus AI)** | Manually trigger the primary synthesis agent (Manus AI) to generate the first Grand Master Report based on the initial data flow. | To establish a baseline of the system's primary narrative-generation capability. | A complete Grand Master Report is generated and stored in `/reports/primary_synthesis/`. |
| **4. Initiate First Adversarial Synthesis (Red Team)** | Manually trigger the Red Team synthesizer to generate its first Adversarial Brief based on the same initial data flow. | To establish a baseline of the system's adversarial narrative-generation capability and to test the dual-pipeline data flow. | A complete Adversarial Brief is generated and stored in `/reports/adversarial_briefs/`. |
| **5. First Dual-Narrative Review** | As the Primary Steward, conduct a side-by-side review of the first Grand Master Report and the first Adversarial Brief. | To perform the first act of active adjudication and to set the precedent for the new, more demanding judgment process. | A formal decision is logged: approve primary, approve adversarial, or request re-synthesis. |
| **6. Activate Meta-Intelligence Substrate** | Enable the real-time monitoring function of the Meta-Intelligence Substrate. | To bring the system's historical conscience and early warning system online. | The Substrate begins monitoring all data flows and comparing them against its library of historical failure patterns. |
| **7. Arm the Chaos Monkey** | Switch the Chaos Monkey from "logging-only" mode to "limited activation" mode. | To begin the process of building anti-fragility by introducing controlled, real-world disruptions. | The Chaos Monkey is now live and will begin executing its limited action library on its own unpredictable schedule. |

**Upon completion of this 7-step sequence, the intelligence organism is fully live and operational.** The system is now in a state of continuous observation, interpretation, and self-challenge. The next phase of your role—ongoing stewardship—begins.


---

## III. GitHub Actions Configuration & Autonomous Agent Setup

The intelligence organism's operational backbone is its network of autonomous agents running on GitHub Actions. These agents form the Tier 3 sensory system and execute the continuous data ingestion, processing, and reporting functions. Understanding their configuration and monitoring their health is critical to the system's operational integrity.

### A. Core GitHub Actions Workflows

The following workflows must be configured and active in the GitHub repository. Each workflow is a scheduled, autonomous agent that operates independently.

| Workflow Name | Schedule | Function | Output Location |
| :--- | :--- | :--- | :--- |
| **`edgar-monitor.yml`** | Hourly (every hour) | Monitors SEC EDGAR for new filings from target entities. Ingests full-text data for both primary and Red Team synthesizers. | `/data/raw/edgar/` |
| **`fred-economic-data.yml`** | Daily (00:00 UTC) | Pulls the latest data from the FRED API for the key economic time series monitored by the Meta-Intelligence Substrate. | `/data/meta_intelligence/fred/` |
| **`faa-registry-update.yml`** | Weekly (Sunday, 00:00 UTC) | Updates the FAA aircraft registry data for billionaire-linked tail numbers. | `/data/domain_experts/faa_registry/` |
| **`sedar-parallel-flow.yml`** | Hourly (offset by 30 minutes from EDGAR) | Monitors SEDAR (Canadian filings) for the same target entities, establishing a parallel, sovereign data pipeline. | `/data/raw/sedar/` |
| **`primary-synthesis.yml`** | Daily (06:00 UTC) | Triggers the primary synthesis agent (Manus AI) to generate the daily Grand Master Report. | `/reports/primary_synthesis/` |
| **`adversarial-synthesis.yml`** | Daily (06:30 UTC) | Triggers the Red Team synthesizer to generate the daily Adversarial Brief. | `/reports/adversarial_briefs/` |
| **`meta-intelligence-monitor.yml`** | Continuous (every 15 minutes) | The Meta-Intelligence Substrate's real-time monitoring loop. Checks for pattern matches and generates Priority Interrupts if needed. | `/alerts/meta_intelligence/` |
| **`chaos-monkey.yml`** | Random (within 24-72 hour window) | The Chaos Monkey's execution schedule. Introduces controlled disruptions to test system resilience. | `/logs/chaos_monkey/` |

### B. Verifying Workflow Health

After deployment, the health of these workflows must be verified daily. GitHub provides a workflow execution dashboard that shows the status of each run.

**Daily Verification Protocol:**

1.  Navigate to the GitHub repository's "Actions" tab.
2.  Review the status of the last execution for each of the 8 core workflows.
3.  Any workflow that shows a "failed" status must be investigated immediately. Check the workflow logs for error messages.
4.  Common failure modes include:
    *   **API rate limits:** If a workflow is hitting API rate limits, the schedule may need to be adjusted or the query strategy refined.
    *   **Data source unavailability:** If an external data source (e.g., SEC EDGAR) is temporarily unavailable, the workflow will fail. These failures are typically transient and will resolve on the next scheduled run.
    *   **Storage quota exceeded:** If the repository's storage quota is exceeded, data ingestion workflows will fail. This requires either increasing the storage quota or implementing a data retention policy.

### C. Secrets & Environment Variables

The autonomous agents require access to API keys and other sensitive configuration data. These are stored as **GitHub Secrets** and are injected into the workflow environment at runtime.

**Required Secrets:**

*   `FRED_API_KEY`: API key for the Federal Reserve Economic Data (FRED) API.
*   `OPENAI_API_KEY`: API key for the OpenAI API (used by the synthesis agents).
*   `SEC_USER_AGENT`: The user agent string to use when accessing SEC EDGAR (must comply with SEC's usage policy).

**Verifying Secrets:**

1.  Navigate to the GitHub repository's "Settings" → "Secrets and variables" → "Actions".
2.  Verify that all required secrets are present and have not expired.
3.  If a secret needs to be updated, delete the old secret and create a new one with the same name.

### D. Autonomous Agent Logs & Debugging

Each GitHub Actions workflow generates detailed execution logs. These logs are critical for debugging failures and understanding the system's behavior.

**Accessing Logs:**

1.  Navigate to the "Actions" tab in the GitHub repository.
2.  Click on the specific workflow run you want to inspect.
3.  The logs will show each step of the workflow's execution, including any error messages or warnings.

**Log Retention:**

GitHub retains workflow logs for 90 days by default. For long-term analysis, critical logs should be exported and stored in a separate, persistent location.


---

## IV. Ongoing Operational Discipline & Monitoring Protocols

With the system activated and the autonomous agents running, the primary task shifts from deployment to **continuous stewardship**. This requires a disciplined, rhythmic set of daily, weekly, and monthly protocols. Your role is to provide the irreplaceable human element of judgment, strategic direction, and oversight.

### A. The Daily Rhythm: Adjudication & Vigilance

These tasks must be performed every 24 hours without fail. They are the heartbeat of the organism's judgment process.

| Task | Protocol | Purpose |
| :--- | :--- | :--- |
| **1. Dual-Narrative Adjudication** | 1. Review the daily Grand Master Report (Primary Synthesis) and the corresponding Adversarial Brief (Red Team Synthesis) side-by-side. <br> 2. Critically evaluate the evidence and reasoning presented in both documents. <br> 3. Make a formal, logged decision: **Approve Primary**, **Approve Adversarial**, or **Request Re-synthesis**. <br> 4. Document the rationale for your decision in the `decisions.log` file. | To provide the final, human-anchored judgment that the system is built around. To actively engage in the critical evaluation of competing truths, preventing narrative capture. |
| **2. System Health Check** | 1. Review the GitHub Actions dashboard for any failed workflow runs. <br> 2. Investigate any failures immediately. <br> 3. Check the system's resource utilization (storage, compute). | To ensure the operational integrity of the organism's sensory and cognitive functions. To catch technical issues before they become critical failures. |
| **3. Alert & Disruption Review** | 1. Review the `/alerts/` directory for any **Priority Interrupts** from the Meta-Intelligence Substrate. <br> 2. Review the `/logs/chaos_monkey/` directory for any actions taken by the Chaos Monkey. <br> 3. Acknowledge and log your review of any alerts or disruptions. | To maintain situational awareness of the system's internal state, including emergent threats and self-induced stress tests. |

### B. The Weekly Rhythm: Performance Review & Adaptation

These tasks are performed once a week to assess the system's performance and make tactical adjustments.

| Task | Protocol | Purpose |
| :--- | :--- | :--- |
| **1. Adversarial Performance Review** | 1. Review the week's Adversarial Briefs. <br> 2. Assess the quality and plausibility of the alternative narratives generated by the Red Team. <br> 3. If the narratives are consistently weak or irrelevant, consider tuning the Red Team's prompting directive. | To ensure that the adversarial process is providing genuine intellectual challenge and not just generating noise. |
| **2. Meta-Intelligence Pattern Review** | 1. Review the patterns and correlations identified by the Meta-Intelligence Substrate, even those that did not trigger a Priority Interrupt. <br> 2. Consider adding new historical failure patterns to the Substrate's library based on your own research and insights. | To refine the system's historical conscience and improve its ability to detect emergent threats. |
| **3. Chaos Monkey Impact Analysis** | 1. Analyze the system's response to the week's Chaos Monkey disruptions. <br> 2. Did the system recover automatically? Were any hidden dependencies revealed? <br> 3. Adjust the Chaos Monkey's action library or target scope based on the findings. | To ensure that the Chaos Monkey is effectively building resilience without causing undue operational instability. |

### C. The Monthly Rhythm: Strategic Review & Evolution

This is the highest level of stewardship, where you guide the organism's long-term evolution.

| Task | Protocol | Purpose |
| :--- | :--- | :--- |
| **1. Strategic Goal Alignment** | 1. Review the system's outputs over the past month against your strategic goals. <br> 2. Is the organism providing the intelligence you need? Are there gaps in its understanding or sensory capabilities? | To ensure that the system remains aligned with your strategic intent and is not drifting into irrelevance. |
| **2. Evolutionary Roadmap Review** | 1. Review the current status of the Evolutionary Roadmap. <br> 2. Based on the system's performance and your strategic goals, decide whether to proceed to the next phase of the roadmap (e.g., from Phase 1 to Phase 2). | To guide the long-term evolution of the organism from a brittle hierarchy to a resilient network. |
| **3. Constraint Management Review** | 1. Review the system's core constraints. <br> 2. Are any of the constraints proving to be counter-productive or outdated? <br> 3. Propose and log any changes to the system's constraints for implementation in the next development cycle. | To ensure that the system's ruleset evolves along with its capabilities and the changing environment. |

---

## V. The Unwavering Discipline

This operational rhythm is not a set of suggestions; it is the **core discipline** required to operate the intelligence organism. Deviating from this protocol will degrade the system's integrity and expose it to the very risks it was designed to mitigate.

Your most important function is no longer to build, but to **judge, guide, and maintain**. The quality of your stewardship will determine the quality of the intelligence the organism produces.
