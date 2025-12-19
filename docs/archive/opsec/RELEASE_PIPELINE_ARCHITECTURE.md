# Artifact Factory & Release Pipeline Architecture

**A detailed architectural specification for the automated, secure, and forensically sterile pipeline that transforms raw content into a publicly released artifact.**

---

## 1. Core Philosophy: The Automated, Zero-Trust Assembly Line

This pipeline is designed as a **zero-trust assembly line**. No component trusts any other component. Each stage receives a specific input, performs a specific transformation, and produces a specific output. The entire process is automated to minimize human error and to enforce the strict separation of duties defined in the Compartmentalization Framework.

---

## 2. Architectural Overview

The pipeline consists of four main stages, corresponding to the four operational compartments. The entire process is orchestrated by a master script running on the host machine.

**Diagram: The Four-Stage Release Pipeline**

```
+----------------+      +----------------+      +----------------+      +----------------+
|   Stage 1:     |      |   Stage 2:     |      |   Stage 3:     |      |   Stage 4:     |
|   RESEARCH     |----->|     WRITE      |----->|    PACKAGE     |----->|    PUBLISH     |
| (Researcher VM)|      |   (Writer VM)  |      |  (Packager VM) |      |  (Publisher VM)|
+----------------+      +----------------+      +----------------+      +----------------+
       |                     |                     |                     |
       v                     v                     v                     v
+----------------+      +----------------+      +----------------+      +----------------+
| Internet Access|      | No Internet    |      | No Internet    |      | Tor/VPN Access |
| (Read-Only)    |      | (Air-gapped)   |      | (Air-gapped)   |      | (Write-Only)   |
+----------------+      +----------------+      +----------------+      +----------------+
```

---

## 3. Stage-by-Stage Technical Specification

### Stage 1: Research

*   **Orchestration Trigger:** Manual start by the operator.
*   **Environment:** The Researcher VM.
*   **Process:**
    1.  The operator conducts research and gathers information.
    2.  All notes, links, and raw data are compiled into a single text file (e.g., `research_notes.txt`).
    3.  The operator places this file into the first dead drop directory (`/mnt/dead_drop_1`).
*   **Output:** A single, unstructured text file.

### Stage 2: Write

*   **Orchestration Trigger:** The appearance of a new file in `/mnt/dead_drop_1`.
*   **Environment:** The Writer VM.
*   **Process (Automated):**
    1.  The VM starts.
    2.  A script reads the `research_notes.txt` file.
    3.  The content is transformed into a structured artifact (e.g., a Markdown document).
    4.  The **Anonymity Engine** is applied:
        *   The writing style is randomly transformed.
        *   Any code examples are formatted with a randomized style.
    5.  The final artifact (e.g., `artifact.md`) and its release notes are written to the second dead drop directory (`/mnt/dead_drop_2`).
    6.  The VM shuts down.
*   **Output:** A stylized, structured content artifact.

### Stage 3: Package

*   **Orchestration Trigger:** The appearance of a new file in `/mnt/dead_drop_2`.
*   **Environment:** The Packager VM.
*   **Process (Automated):**
    1.  The VM starts.
    2.  The `strip_all.sh` script is executed on the artifact, removing all metadata.
    3.  The appropriate **Project Key** is loaded.
    4.  A **one-time PGP key** is generated and signed with the Project Key.
    5.  The stripped artifact is signed with the one-time key.
    6.  A final release package (e.g., a signed Git commit object or a `.tar.gz` archive) is created.
    7.  The release package is placed in the third dead drop directory (`/mnt/dead_drop_3`).
    8.  The VM shuts down.
*   **Output:** A single, signed, and forensically sterile release package.

### Stage 4: Publish

*   **Orchestration Trigger:** The appearance of a new file in `/mnt/dead_drop_3`.
*   **Environment:** An ephemeral, single-use Publisher VM.
*   **Process (Automated):**
    1.  A fresh VM is created from the Publisher template.
    2.  The VM starts and connects to the internet via a randomized VPN endpoint or Tor.
    3.  The release package is read from `/mnt/dead_drop_3`.
    4.  The package is published to the target platform (e.g., `git push`, API call to a social media platform).
    5.  The VM is **immediately and permanently destroyed**.
*   **Output:** The public release of the artifact.

---

## 4. The Orchestration Engine

The entire pipeline is controlled by a master orchestration script on the host machine. This script is the "brain" of the operation.

### Implementation Details

*   **Language:** A robust scripting language like Python or Bash.
*   **File System Monitoring:** The script will use a file system monitoring tool (e.g., `inotifywait` on Linux) to watch the dead drop directories and trigger the next stage of the pipeline.
*   **VM Management:** The script will use the command-line interface of your chosen virtualization software (e.g., `VBoxManage` for VirtualBox) to start, stop, and destroy the VMs.
*   **Logging:** The orchestrator must keep a detailed, encrypted log of its own operations. This log should record the start and end of each stage, the hashes of the files being processed, and any errors that occur. This log is for your internal use only and should never be made public.

### Example Orchestrator Logic (Pseudocode)

```python
def run_pipeline():
    # Stage 1 (Manual)
    print("Waiting for research notes in dead_drop_1...")
    wait_for_file("/mnt/dead_drop_1/research_notes.txt")
    log("Research complete.")

    # Stage 2
    log("Starting Writer VM...")
    start_vm("Writer-VM")
    wait_for_file("/mnt/dead_drop_2/artifact.md")
    stop_vm("Writer-VM")
    log("Writing complete.")

    # Stage 3
    log("Starting Packager VM...")
    start_vm("Packager-VM")
    wait_for_file("/mnt/dead_drop_3/release.pkg")
    stop_vm("Packager-VM")
    log("Packaging complete.")

    # Stage 4
    log("Starting Publisher VM...")
    start_vm("Publisher-VM", ephemeral=True)
    # How to detect completion? A simple sleep or a more complex callback.
    wait_for_publication_signal()
    destroy_vm("Publisher-VM")
    log("Publishing complete. VM destroyed.")
```

---

## 5. Implementation Instructions for Nathan

### Task 1: Script the Pipeline Stages

1.  **Writer Script:**
    *   [ ] Write the script that runs inside the Writer VM, transforming the raw notes into a structured artifact and applying the Anonymity Engine.

2.  **Packager Script:**
    *   [ ] Write the script that runs inside the Packager VM, executing the metadata stripping and cryptographic signing process.

3.  **Publisher Script:**
    *   [ ] Write the script that runs inside the Publisher VM, taking the final package and pushing it to the public platform.

### Task 2: Build the Master Orchestrator

1.  **`orchestrator.py`:**
    *   [ ] Write the master orchestration script in Python.
    *   [ ] Implement the file system monitoring logic using a library like `watchdog`.
    *   [ ] Implement the VM control logic using the `subprocess` module to call your virtualization software's CLI.
    *   [ ] Implement a secure, encrypted logging system.

### Task 3: Test the Full Pipeline

1.  **End-to-End Test:**
    *   [ ] Run the entire pipeline from start to finish with a sample artifact.
    *   [ ] Verify that the final, public artifact is correctly formatted, signed, and stripped of all metadata.
    *   [ ] Verify that the Publisher VM is successfully destroyed after the release.

---

## 6. Security Considerations

*   **The Orchestrator is a High-Value Target:** The master orchestration script and its logs must be heavily protected. They should be stored on an encrypted volume on the host machine.
*   **VM Escape:** While unlikely, a vulnerability in your virtualization software could allow code to "escape" from a VM and access the host machine. Keep your virtualization software and host OS fully patched.
*   **Side-Channel Attacks:** Advanced adversaries could use side-channel attacks (e.g., monitoring CPU cache or power consumption) to infer information about the operations happening inside the VMs. For your threat model, this is likely out of scope, but it is important to be aware of.

---

**This automated pipeline architecture provides a high degree of security and operational consistency. By removing the human from the loop as much as possible, we minimize the risk of error and ensure that our security protocols are followed without exception for every single release.**
