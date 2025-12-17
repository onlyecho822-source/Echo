
import json
import datetime
import hashlib
import argparse

NDA_TEMPLATE_PATH = "/home/ubuntu/Echo/NDA/ECHO_UNIVERSE_NDA.md"
SIGNED_NDAS_DB = "/home/ubuntu/Echo/NDA/system/signed_ndas.json"

def get_nda_hash():
    """Calculates the SHA256 hash of the NDA template to version it."""
    with open(NDA_TEMPLATE_PATH, 'rb') as f:
        nda_bytes = f.read()
        return hashlib.sha256(nda_bytes).hexdigest()

def initialize_db():
    """Creates the JSON database file if it doesn't exist."""
    try:
        with open(SIGNED_NDAS_DB, 'x') as f:
            json.dump([], f)
    except FileExistsError:
        pass # File already exists

def sign_nda(name, email, github_username):
    """Creates a record of a signed NDA and saves it to the database."""
    initialize_db()

    timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    nda_version_hash = get_nda_hash()

    agreement = {
        "agreement_id": f"NDA-{hashlib.sha256(email.encode()).hexdigest()[:12]}",
        "name": name,
        "email": email,
        "github_username": github_username,
        "timestamp_utc": timestamp,
        "nda_version_hash": nda_version_hash,
        "status": "active"
    }

    with open(SIGNED_NDAS_DB, 'r+') as f:
        records = json.load(f)
        # Check if user has already signed
        for record in records:
            if record['email'] == email or record['github_username'] == github_username:
                print(f"User {name} ({github_username}/{email}) has already signed an NDA.")
                return
        
        records.append(agreement)
        f.seek(0)
        json.dump(records, f, indent=4)

    print(f"Successfully recorded NDA for {name} ({github_username}).")
    print(f"Agreement ID: {agreement['agreement_id']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Record a signed Non-Disclosure Agreement for the Echo Universe project.")
    parser.add_argument("--name", required=True, help="Full name of the signatory.")
    parser.add_argument("--email", required=True, help="Email address of the signatory.")
    parser.add_argument("--github", required=True, help="GitHub username of the signatory.")

    args = parser.parse_args()

    print("--- Echo Universe NDA Signing --- ")
    print(f"Recording agreement for: {args.name}")
    print(f"Email: {args.email}")
    print(f"GitHub Username: {args.github}")
    print("By running this script, you acknowledge that you have read, understood, and agree to be legally bound by the terms of the Echo Universe Unilateral NDA.")
    
    # In a real scenario, you'd add a confirmation prompt.
    sign_nda(args.name, args.email, args.github)
