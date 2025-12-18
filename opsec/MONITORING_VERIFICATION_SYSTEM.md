# Monitoring, Verification & Integrity Checking System

**A technical specification for the automated systems that continuously monitor the health of our infrastructure, verify the integrity of our published artifacts, and check for any potential security breaches or data leaks.**

---

## 1. Core Philosophy: Trust, But Verify (Automatedly)

We operate a zero-trust architecture, but we do not assume it is infallible. This system is our internal affairs department. It operates independently of the release pipeline and its sole purpose is to **continuously audit** our own work. It asks three questions: Is our system secure? Is our content correct? Has anything changed when it shouldn't have?

---

## 2. The Three Layers of Monitoring

We will implement three distinct layers of monitoring, each with its own scope and toolset.

### Layer 1: Infrastructure Health Monitoring

*   **Purpose:** To ensure the underlying infrastructure (host machine, VMs, network) is secure and operating as expected.
*   **Process (Automated Daily Scan):**
    1.  **Host OS Integrity:** An intrusion detection system (IDS) like **AIDE (Advanced Intrusion Detection Environment)** will be used to monitor the host machine. AIDE creates a baseline snapshot of the system (file hashes, permissions, etc.) and alerts on any unauthorized changes.
    2.  **VM Integrity:** The master orchestration script will verify the SHA-256 hash of each VM disk image before it is started. If the hash does not match the known-good baseline, the pipeline halts immediately.
    3.  **Network Monitoring:** A tool like `nmap` will be run daily against the host machine to scan for any unexpected open ports.
*   **Alerting:** Any anomaly detected at this layer triggers a high-priority, encrypted email alert to your personal security address.

### Layer 2: Public Artifact Verification

*   **Purpose:** To continuously verify that our publicly available artifacts have not been tampered with or altered after publication.
*   **Process (Automated Hourly Scan):**
    1.  **The Verifier Bot:** A dedicated script, running in the **Researcher** compartment (as it needs internet access), will perform this task.
    2.  **Fetch and Verify:** For every artifact we have ever published, the bot will:
        a.  Fetch the artifact from its public location (e.g., the website, GitHub).
        b.  Fetch the corresponding `verification_data.json` file.
        c.  Recalculate the SHA-256 hash of the fetched artifact and compare it to the hash in the JSON file.
        d.  Fetch the public PGP key and verify the artifact's signature.
        e.  Check the public tweet and verify that the hash and link are still correct.
        f.  Query the Arweave gateway to ensure the artifact is still available and its hash matches.
*   **Alerting:** If any verification step fails for any artifact, the system triggers an immediate, critical alert. This could be a sign of a platform compromise (e.g., GitHub being hacked) or a targeted attack on our content.

### Layer 3: Anonymity & OPSEC Leakage Detection

*   **Purpose:** To proactively search for any accidental leaks of information that could compromise our pseudonymity.
*   **Process (Automated Daily Scan):**
    1.  **The Sentinel Bot:** Another script, also running in the **Researcher** compartment, will act as an automated open-source intelligence (OSINT) analyst looking for our own mistakes.
    2.  **Search Queries:** The bot will search the web for:
        a.  The real names and personal information of anyone associated with the project (i.e., you).
        b.  The IP addresses of our known VPN endpoints or hosting providers.
        c.  Any of the internal codenames for our compartments (e.g., "The Workshop," "The Courier").
        d.  Any content from our internal-only documents (e.g., the orchestrator logs).
    3.  **Dark Web Monitoring:** The bot will use Tor to run similar searches on a curated list of dark web search engines and forums.
*   **Alerting:** Any positive hit from the Sentinel Bot is a five-alarm fire. It triggers the most critical alert possible, indicating a severe breach of operational security.

---

## 3. The Master Dashboard

To manage this flood of data, we will create a simple, text-based master dashboard.

*   **Implementation:** A Python script that runs on the host machine and generates a simple HTML or terminal-based dashboard.
*   **Content:** The dashboard will display the status of all checks in a simple, color-coded format:
    *   **GREEN:** All checks passed.
    *   **YELLOW:** A non-critical anomaly was detected (e.g., a website was temporarily down).
    *   **RED:** A critical alert has been triggered.
*   **Access:** The dashboard is for your eyes only and should be accessible only from the host machine.

---

## 4. Implementation Instructions for Nathan

### Task 1: Set Up Infrastructure Monitoring (Layer 1)

1.  **AIDE:**
    *   [ ] On your host machine, install AIDE (`sudo apt-get install aide`).
    *   [ ] Initialize the AIDE database: `sudo aideinit`.
    *   [ ] Set up a cron job to run `sudo aide --check` daily and email you the report.

2.  **VM Hashing:**
    *   [ ] Modify your master orchestration script to calculate and store the SHA-256 hash of each VM template disk image.
    *   [ ] Before starting any VM, the script must verify the current disk image hash against the stored baseline.

3.  **Port Scanning:**
    *   [ ] Install `nmap` (`sudo apt-get install nmap`).
    *   [ ] Create a cron job that runs `nmap localhost` daily and diffs the output against a known-good baseline.

### Task 2: Build the Verifier Bot (Layer 2)

1.  **`verifier.py`:**
    *   [ ] In the **Researcher VM**, write a Python script that implements the public artifact verification process.
    *   [ ] This script will need a list of all published artifacts and their public URLs. This list can be a simple JSON file.
    *   [ ] The script should be able to parse the `verification_data.json` for each artifact.
    *   [ ] Use libraries like `requests`, `gnupg`, and `hashlib`.
    *   [ ] Set this up as a cron job to run hourly.

### Task 3: Build the Sentinel Bot (Layer 3)

1.  **`sentinel.py`:**
    *   [ ] In the **Researcher VM**, write a Python script that implements the OSINT leakage detection process.
    *   [ ] Use libraries like `requests` and `beautifulsoup4` for web scraping.
    *   [ ] Use a library like `stem` to control Tor for dark web searches.
    *   [ ] Define a list of sensitive keywords (your name, internal codenames, etc.) for the bot to search for.
    *   [ ] Set this up as a cron job to run daily.

### Task 4: Create the Master Dashboard

1.  **`dashboard.py`:**
    *   [ ] On the host machine, write a Python script that aggregates the output from all the monitoring scripts.
    *   [ ] The script should read the log files from AIDE, nmap, the Verifier Bot, and the Sentinel Bot.
    *   [ ] It should generate a simple HTML file with a summary of the system status.

---

## 5. Incident Response

If any of these systems trigger a red alert, you must have a pre-defined incident response plan.

1.  **Halt the Pipeline:** The first step is always to immediately halt the master orchestration script to prevent any further releases.
2.  **Isolate the System:** Disconnect the host machine from the internet.
3.  **Analyze the Alert:** Carefully review the logs to understand the nature and scope of the breach.
4.  **Execute Remediation:** Depending on the alert, this could involve anything from rebuilding a compromised VM to rotating all cryptographic keys.

---

**This comprehensive monitoring system provides the necessary checks and balances for our zero-trust architecture. It ensures that we can not only trust our system to be secure but also verify that it remains so over time.**
