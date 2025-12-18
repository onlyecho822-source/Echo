# Forensic Trace Minimization & Metadata Stripping Protocol

**A comprehensive technical protocol for identifying, neutralizing, and stripping all forms of metadata and forensic traces from artifacts before public release. This is a critical component of maintaining long-term operational security.**

---

## 1. Core Philosophy: Leave No Trace

Every digital artifact, from a simple text file to a compiled binary, contains a hidden layer of metadata. This metadata, when aggregated over time, creates a detailed forensic fingerprint that can be used to identify the author, their tools, their location, and their habits. Our goal is to **aggressively and systematically** remove all such traces, ensuring that the only information released is the information we intend to release.

---

## 2. The Three Categories of Traces

We will classify all potential traces into three categories, each with its own set of mitigation strategies.

### Category 1: File System Metadata

This is the most basic layer of metadata, attached to files by the operating system.

*   **Traces:**
    *   File creation, modification, and access timestamps.
    *   User and group ownership information.
    *   File permissions.
*   **Mitigation:**
    *   **Timestamp Standardization:** Before release, all file timestamps must be set to a standard, constant value (e.g., the Unix epoch, `1970-01-01 00:00:00 UTC`). This can be done with the `touch` command: `touch -d "1970-01-01" <file>`.
    *   **Ownership Neutralization:** The user and group ownership of all files must be set to a neutral, standard value (e.g., `root:root`). This can be done with the `chown` command: `chown root:root <file>`.
    *   **Permission Standardization:** File permissions should be set to a standard, non-identifiable value (e.g., `644` for files, `755` for directories).

### Category 2: Embedded Application Metadata

This is metadata embedded within the file itself by the application that created it.

*   **Traces:**
    *   **Documents (PDF, DOCX):** Author name, company, creation date, software version.
    *   **Images (JPEG, PNG):** Camera model, GPS coordinates, creation date, software version.
    *   **Audio/Video (MP3, MP4):** Artist, album, genre, encoding software.
    *   **Compressed Archives (ZIP, TAR):** File timestamps, user/group info from the source system.
*   **Mitigation:**
    *   **The `mat2` Tool:** We will use the **Metadata Anonymisation Toolkit v2 (`mat2`)** as our primary weapon for stripping embedded metadata. This tool is designed for this exact purpose and supports a wide range of file formats.
    *   **The Stripping Process:** All artifacts, without exception, must be processed by `mat2` in the **Packager** compartment before being signed and released. The command is simple: `mat2 <file>`.

### Category 3: Behavioral & Environmental Traces

This is the most subtle and dangerous category of traces, left by the unique habits and environment of the creator.

*   **Traces:**
    *   **Git Commits:** Author name, email, and timestamp. The commit message style itself can also be a fingerprint.
    *   **Code Style:** Consistent use of certain variable names, commenting styles, or architectural patterns.
    *   **Toolchain Artifacts:** Specific versions of compilers, libraries, and operating systems can be fingerprinted.
    *   **Network Patterns:** Consistent use of certain IP addresses, VPN providers, or browser user agents.
*   **Mitigation:**
    *   **Git Commit Anonymization:**
        *   All commits must be authored by a generic, non-attributable name and email (e.g., `"Aria" <aria@echouniverse.dev>`).
        *   Commit timestamps must be standardized. This can be done by setting the `GIT_AUTHOR_DATE` and `GIT_COMMITTER_DATE` environment variables before committing.
        *   We will use `git-filter-repo` to perform a final, destructive scrub of all historical metadata before any public release.
    *   **Behavioral Obfuscation:** This is the purpose of the **Anonymity Engine** described in the Cryptographic Identity Protocol. The systematic rotation of writing styles, code styles, and temporal patterns is our primary defense against behavioral analysis.
    - **Environmental Standardization:** All development and packaging must be done within the standardized, minimal VMs defined in the Compartmentalization Framework. This ensures that the toolchain and environment are consistent and non-attributable.

---

## 3. The Metadata Stripping Workflow

This workflow must be executed within the **Packager** compartment for every single release.

1.  **Receive Artifact:** The final content artifact arrives from the Writer compartment.
2.  **Strip Embedded Metadata:**
    *   Run the artifact through `mat2`: `mat2 <artifact_file>`.
    *   Verify that `mat2` reports all metadata has been successfully removed.
3.  **Standardize File System Metadata:**
    *   Set the timestamp to the Unix epoch: `touch -d "1970-01-01" <artifact_file>`.
    *   Set the ownership to root: `chown root:root <artifact_file>`.
4.  **Prepare Git Commit (if applicable):**
    *   Set the author and committer information:
        ```bash
        export GIT_AUTHOR_NAME="Aria"
        export GIT_AUTHOR_EMAIL="aria@echouniverse.dev"
        export GIT_COMMITTER_NAME="Aria"
        export GIT_COMMITTER_EMAIL="aria@echouniverse.dev"
        ```
    *   Set a standardized timestamp:
        ```bash
        export GIT_AUTHOR_DATE="1970-01-01T00:00:00Z"
        export GIT_COMMITTER_DATE="1970-01-01T00:00:00Z"
        ```
    *   Create the commit.
5.  **Sign the Artifact:**
    *   Use the appropriate one-time PGP key to sign the final, stripped artifact.
6.  **Package for Release:**
    *   Create the final release package (e.g., a `.tar.gz` archive) containing the stripped artifact and its signature.
    *   Run the final archive itself through the metadata stripping process one last time to remove any traces left by the archiving tool.

---

## 4. Implementation Instructions for Nathan

### Task 1: Install and Configure Tooling

1.  **`mat2`:**
    *   [ ] In your **Packager VM** template, install `mat2` from your distribution's package manager (e.g., `sudo apt-get install mat2`).

2.  **`git-filter-repo`:**
    *   [ ] In your **Packager VM** template, install `git-filter-repo`.

### Task 2: Create the Master Stripping Script

1.  **`strip_all.sh`:**
    *   [ ] Write a single shell script named `strip_all.sh` that automates the entire metadata stripping workflow described in Section 3.
    *   [ ] This script should take a single file or directory as input and perform all the necessary steps in the correct order.
    *   [ ] The script should be heavily commented to explain each step and its purpose.
    *   [ ] It should include robust error checking. If any step fails, the script should exit immediately and clean up any temporary files.

### Task 3: Integrate into the Workflow

1.  **Orchestration:**
    *   [ ] Modify your master orchestration script to call `strip_all.sh` as the first step within the **Packager** compartment.
    *   [ ] Ensure that the signing process only happens *after* the stripping process is complete.

---

## 5. Verification

Before any public release, you must verify that the stripping process was successful. This involves using forensic tools to inspect the final artifact for any remaining metadata.

*   **Tools:** Use tools like `exiftool`, `binwalk`, and `strings` to inspect the final, packaged artifact.
*   **Checklist:**
    *   [ ] Are all timestamps set to the standard value?
    *   [ ] Is the author/creator information removed?
    *   [ ] Are there any embedded GPS coordinates or device information?
    *   [ ] Does the Git log show the correct, anonymized author and timestamp?

---

**This protocol, when implemented correctly and followed with discipline, will ensure that your public artifacts are forensically sterile. It is a critical defense against the long-term, cumulative risk of metadata analysis.**
