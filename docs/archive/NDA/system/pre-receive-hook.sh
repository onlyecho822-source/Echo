#!/bin/bash
#
# GitHub Pre-Receive Hook: NDA Enforcement
#
# This script simulates a pre-receive hook to enforce that users have a signed
# NDA before they can push code to a private repository.
#
# In a real GitHub Enterprise environment, this script would be placed in the
# /hooks directory of the repository on the server.

# --- Configuration ---
NDA_CHECK_SCRIPT="/home/ubuntu/Echo/NDA/system/check_nda.py"

# --- GitHub Environment Variables (Simulated) ---
# In a real hook, these are provided by GitHub.
GITHUB_USER_LOGIN="$1" # The GitHub username of the person pushing

# --- Main Logic ---
echo "---[ NDA Enforcement Hook ]---"

if [ -z "$GITHUB_USER_LOGIN" ]; then
    echo "ERROR: GitHub username not provided. Usage: ./pre-receive-hook.sh <github_username>"
    exit 1
fi

echo "Checking NDA status for user: $GITHUB_USER_LOGIN"

# Run the check script and capture the output
NDA_STATUS=$(python3 "$NDA_CHECK_SCRIPT" "$GITHUB_USER_LOGIN")

# Check if the output contains "No NDA found"
if echo "$NDA_STATUS" | grep -q "No NDA found"; then
    echo "-----------------------------------------------------------------"
    echo "ACCESS DENIED: No signed NDA found for user [1;31m$GITHUB_USER_LOGIN[0m."
    echo ""
    echo "To gain access, you must sign the Echo Universe Unilateral NDA."
    echo "Please contact the repository owner for instructions."
    echo "-----------------------------------------------------------------"
    exit 1
else
    echo "[1;32mACCESS GRANTED: Valid NDA found for user $GITHUB_USER_LOGIN.[0m"
    echo "-----------------------------------------------------------------"
    # In a real hook, the script would exit 0 to allow the push.
    echo "$NDA_STATUS"
    exit 0
fi
