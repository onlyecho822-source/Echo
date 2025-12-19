# Echo Universe NDA System

This directory contains the tools and documentation for managing Non-Disclosure Agreements (NDAs) for the Echo Universe project.

## Components

*   `ECHO_UNIVERSE_NDA.md`: The master Unilateral Non-Disclosure Agreement template.
*   `sign_nda.py`: A Python script to record a signed NDA.
*   `check_nda.py`: A Python script to check the status of a signed NDA.
*   `pre-receive-hook.sh`: A shell script that simulates a GitHub pre-receive hook to enforce NDA signing before allowing code pushes.
*   `signed_ndas.json`: A JSON file that acts as a simple database for signed NDAs.

## How to Use

### Signing an NDA

To record a new signed NDA, run the `sign_nda.py` script with the signatory's information:

```bash
python3 sign_nda.py --name "John Doe" --email "john.doe@example.com" --github "johndoe"
```

This will create a record in the `signed_ndas.json` file.

### Checking an NDA

To check if a user has a signed NDA, run the `check_nda.py` script with their email or GitHub username:

```bash
python3 check_nda.py "johndoe"
```

### Enforcing NDAs with GitHub

The `pre-receive-hook.sh` script is a simulation of how you would enforce NDAs in a GitHub Enterprise environment. To test it, you can run it with a GitHub username:

```bash
# Simulate a user who has not signed an NDA
./pre-receive-hook.sh "jane-doe"

# Simulate a user who has signed an NDA
./pre-receive-hook.sh "johndoe"
```

In a real-world scenario, this script would be placed in the `/hooks` directory of your repository on a GitHub Enterprise server. For GitHub.com, you would need to use a different mechanism, such as a GitHub App that checks for a signed NDA before granting repository access.
