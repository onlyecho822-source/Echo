'''
import json
import argparse

def check_nda(identifier):
    """Checks if a user has a valid, signed NDA on record."""
    try:
        with open("signed_ndas.json", 'r') as f:
            records = json.load(f)
    except FileNotFoundError:
        print("NDA database not found. No NDAs have been signed.")
        return

    found_record = None
    for record in records:
        if record["email"] == identifier or record["github_username"] == identifier:
            found_record = record
            break

    if found_record:
        print("--- NDA Status Found ---")
        print(f"Name: {found_record['name']}")
        print(f"Email: {found_record['email']}")
        print(f"GitHub Username: {found_record['github_username']}")
        print(f"Agreement ID: {found_record['agreement_id']}")
        print(f"Signed On (UTC): {found_record['timestamp_utc']}")
        print(f"NDA Version Hash: {found_record['nda_version_hash']}")
        print(f"Status: {found_record['status']}")
        print("------------------------")
    else:
        print(f"No NDA found for identifier: {identifier}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check the status of a signed Non-Disclosure Agreement.")
    parser.add_argument("identifier", help="The email address or GitHub username to check.")

    args = parser.parse_args()
    check_nda(args.identifier)
'''
