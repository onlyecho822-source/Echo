# Content Timestamping & Archival System Specification

**A technical specification for the system that provides verifiable, immutable timestamps for all content and ensures the long-term, durable archival of all published artifacts.**

---

## 1. Core Philosophy: Verifiable Time and Permanent Record

The influence model of Echo Universe is built on the foundation of **20/20 hindsight**. This is only possible if we can prove, without a doubt, *when* a piece of information was published. The timestamp is not just metadata; it is a core part of the content itself. Furthermore, this content must be archived in a way that is resilient to censorship, platform decay, and data loss.

---

## 2. The Multi-Layer Timestamping Protocol

We will use a multi-layer approach to timestamping, creating redundant and cross-verifiable proofs of publication time. No single timestamp is trusted; the system's integrity comes from the consensus of multiple, independent sources.

### Layer 1: Cryptographic Timestamps (The "Internal Clock")

*   **Mechanism:** OpenTimestamps (OTS). This is a decentralized protocol that anchors timestamps to the Bitcoin blockchain, providing a high degree of security and verifiability.
*   **Process:**
    1.  In the **Packager** compartment, after an artifact is finalized but before it is signed, we will create a timestamp proof for it using the `ots` client: `ots stamp <artifact_file>`.
    2.  This generates a `.ots` file, which is a cryptographic proof that the artifact existed at that moment in time.
    3.  This `.ots` file is then included in the final release package alongside the artifact itself.
*   **Verification:** Anyone can later verify the timestamp using the `ots` client: `ots verify <artifact.ots>`. This will confirm the time at which the artifact was anchored to the Bitcoin blockchain.

### Layer 2: Public Ledger Timestamps (The "Town Crier")

*   **Mechanism:** Using public, widely-witnessed platforms as a form of social timestamping.
*   **Process:**
    1.  In the **Publisher** compartment, immediately after an artifact is published to its primary location (e.g., the project website), a hash of the artifact is published to a high-visibility public ledger.
    2.  **Primary Ledger: Twitter/X.** A tweet is sent containing the SHA-256 hash of the artifact and a link to the artifact itself. The timestamp of the tweet serves as a public, widely-witnessed proof of publication time.
    3.  **Secondary Ledger: GitHub.** The signed Git commit itself, with its own timestamp, serves as another public ledger.
*   **Verification:** A user can verify the publication time by comparing the hash in the tweet to the hash of the artifact and noting the timestamp of the tweet.

### Layer 3: Decentralized Archive Timestamps (The "Eternal Library")

*   **Mechanism:** Archiving the content on decentralized, permanent storage networks.
*   **Process:**
    1.  In the **Publisher** compartment, after the primary publication, the artifact is uploaded to one or more decentralized storage networks.
    2.  **Primary Archive: Arweave.** Arweave is a permanent storage network that is ideal for this purpose. The transaction ID and timestamp of the Arweave upload provide another strong, verifiable proof of time.
    3.  **Secondary Archive: IPFS (InterPlanetary File System).** While not permanent by default, pinning the content to multiple IPFS nodes provides redundancy.
*   **Verification:** The Arweave transaction ID can be looked up on an Arweave block explorer to verify the content and the time of its upload.

---

## 3. The Archival & Redundancy Strategy

Our goal is to make the content **un-censorable and permanent**. This requires a multi-layered archival strategy.

| Archive Layer | Technology | Purpose | Retention Policy |
| :--- | :--- | :--- | :--- |
| **Hot Storage** | Project Website (GitHub Pages) | Immediate access and discovery | Current version only |
| **Warm Storage** | GitHub Repository | Version history and source code | Full history |
| **Cold Storage** | Arweave | Permanent, immutable archival | Forever |
| **Redundant Storage** | IPFS (Pinned) | Redundancy and decentralized access | Best effort |
| **Offline Backup** | Encrypted Local Storage | Disaster recovery | Full history, updated weekly |

---

## 4. Implementation Instructions for Nathan

### Task 1: Set Up Timestamping Tools

1.  **OpenTimestamps (`ots`):**
    *   [ ] In your **Packager VM** template, install the OpenTimestamps client.
    *   [ ] Modify your `packager.sh` script to automatically generate an `.ots` proof for every artifact.

2.  **Twitter/X API Access:**
    *   [ ] Apply for a developer account on the X platform to get API keys for posting tweets.
    *   [ ] Store these API keys as encrypted secrets, accessible only by the Publisher VM.

3.  **Arweave Wallet & `arweave-deploy`:**
    *   [ ] Create an Arweave wallet and securely back up the key file.
    *   [ ] In your **Publisher VM** template, install the `arweave-deploy` command-line tool.
    *   [ ] Store the Arweave wallet key as an encrypted secret, accessible only by the Publisher VM.

### Task 2: Automate the Timestamping & Archival Workflow

1.  **Packager Script (`packager.sh`):**
    *   [ ] Add the `ots stamp` command to this script. It should run *before* the PGP signing step.

2.  **Publisher Script (`publisher.sh`):**
    *   [ ] This script will now have multiple steps:
        1.  Publish the primary artifact (e.g., `git push`).
        2.  Calculate the SHA-256 hash of the artifact.
        3.  Post a tweet containing the hash and a link to the artifact using the Twitter API.
        4.  Upload the artifact to Arweave using `arweave-deploy`.
        5.  (Optional) Pin the artifact to an IPFS node.
    *   [ ] The script should log the Tweet ID and the Arweave transaction ID for future reference.

### Task 3: Create the Public Verification Guide

1.  **`VERIFICATION.md`:**
    *   [ ] Create a new document in the root of your main repository called `VERIFICATION.md`.
    *   [ ] This document should provide clear, step-by-step instructions for a non-technical user on how to verify the integrity and timestamp of any artifact.
    *   [ ] It should explain how to:
        *   Verify the PGP signature chain.
        *   Verify the OpenTimestamps proof.
        *   Cross-reference the artifact hash with the public tweet.
        *   Find the artifact on the Arweave block explorer.

---

## 5. The Final Artifact Package

When a user downloads an artifact, they should get a complete package that includes everything needed for verification:

```
release-package.zip
├── artifact.md
├── artifact.md.sig         # PGP signature
├── artifact.md.ots         # OpenTimestamps proof
└── verification_data.json  # A JSON file containing:
    {
      "sha256_hash": "...",
      "pgp_one_time_key_id": "...",
      "twitter_proof_url": "...",
      "arweave_tx_id": "..."
    }
```

---

**This multi-layered system creates a web of trust that is extremely difficult to forge or refute. By decentralizing our proofs of time and existence, we make the integrity of our work dependent on the consensus of the entire internet, not on our own authority.**
