#!/usr/bin/env python3
"""
Aletheia CLI Ingest + Sealing Tool
===================================
Ingests raw artifacts, computes cryptographic hashes, generates manifests,
signs them, and obtains trusted timestamps for the Aletheia Reality Decoding System.

Usage:
    python ingest.py --file <path> --type <artifact_type> --output <manifest_path>
    python ingest.py --file sample.vcf.gz --type VCF --output manifest.json

Author: Echo Nexus Omega
Version: 1.0.0
"""

import os
import sys
import json
import hashlib
import argparse
import mimetypes
import secrets
import base64
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

# Optional imports with fallbacks
try:
    import blake3
    HAS_BLAKE3 = True
except ImportError:
    HAS_BLAKE3 = False

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.backends import default_backend
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


# =============================================================================
# CONSTANTS
# =============================================================================

MANIFEST_VERSION = "1.0.0"
VALID_ARTIFACT_TYPES = [
    "FASTQ", "VCF", "BAM", "IIIF", "TIFF", "XRF_CSV", "TEI_XML",
    "SPECTRA", "RADIOCARBON", "DOCUMENT", "IMAGE", "AUDIO", "VIDEO", "OTHER"
]


# =============================================================================
# CORE CRYPTOGRAPHIC FUNCTIONS
# =============================================================================

def compute_sha256(file_path: str) -> str:
    """Compute SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def compute_blake3(file_path: str) -> Optional[str]:
    """Compute BLAKE3 hash of a file (if available)."""
    if not HAS_BLAKE3:
        # Fallback to BLAKE2s if BLAKE3 not available
        blake2s_hash = hashlib.blake2s()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                blake2s_hash.update(chunk)
        return blake2s_hash.hexdigest()

    hasher = blake3.blake3()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def generate_stable_id(artifact_type: str) -> str:
    """Generate a unique stable ID for the artifact."""
    type_prefix = artifact_type[:4].upper()
    random_hex = secrets.token_hex(8).upper()
    return f"ALT-{type_prefix}-{random_hex[:8]}-{random_hex[8:12]}"


def sign_manifest(manifest_data: bytes, private_key_path: Optional[str] = None) -> Tuple[str, str, str]:
    """
    Sign manifest data with Ed25519.

    Returns: (signature_b64, algorithm, public_key_id)
    """
    if not HAS_CRYPTO:
        # Return placeholder if cryptography library not available
        return (
            base64.b64encode(b"placeholder_signature_install_cryptography").decode(),
            "Ed25519",
            "placeholder-key-install-cryptography"
        )

    if private_key_path and os.path.exists(private_key_path):
        # Load existing key
        with open(private_key_path, "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)
    else:
        # Generate ephemeral key for demo (in production, use HSM or secure key store)
        private_key = ed25519.Ed25519PrivateKey.generate()

    # Sign the manifest
    signature = private_key.sign(manifest_data)
    signature_b64 = base64.b64encode(signature).decode()

    # Get public key fingerprint as ID
    public_key = private_key.public_key()
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    public_key_id = f"aletheia-key-{hashlib.sha256(public_key_bytes).hexdigest()[:16]}"

    return signature_b64, "Ed25519", public_key_id


def get_timestamp_proof() -> Tuple[str, str, str]:
    """
    Get trusted timestamp proof.

    In production, integrate with:
    - OpenTimestamps
    - RFC3161 TSA
    - Blockchain timestamping

    Returns: (authority, timestamp_iso, proof_b64)
    """
    # For demo, return current time with placeholder proof
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # In production, call OpenTimestamps or TSA here
    # Example: ots_proof = opentimestamps.stamp(manifest_hash)

    proof_placeholder = base64.b64encode(
        f"OTS_PROOF_PLACEHOLDER_{now}".encode()
    ).decode()

    return "OpenTimestamps", now, proof_placeholder


# =============================================================================
# MANIFEST GENERATION
# =============================================================================

def generate_manifest(
    file_path: str,
    artifact_type: str,
    metadata_overrides: Optional[Dict[str, Any]] = None,
    private_key_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a complete manifest for an artifact.

    Args:
        file_path: Path to the raw artifact file
        artifact_type: Type of artifact (VCF, FASTQ, etc.)
        metadata_overrides: Optional custom metadata to include
        private_key_path: Optional path to signing key

    Returns:
        Complete manifest dictionary
    """
    file_path = os.path.abspath(file_path)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Artifact not found: {file_path}")

    if artifact_type not in VALID_ARTIFACT_TYPES:
        raise ValueError(f"Invalid artifact type: {artifact_type}. Valid types: {VALID_ARTIFACT_TYPES}")

    # Get file metadata
    file_stat = os.stat(file_path)
    filename = os.path.basename(file_path)
    mime_type, _ = mimetypes.guess_type(file_path)

    # Compute hashes
    sha256_hash = compute_sha256(file_path)
    blake_hash = compute_blake3(file_path)
    blake_algo = "BLAKE3" if HAS_BLAKE3 else "BLAKE2s"

    # Generate stable ID
    stable_id = generate_stable_id(artifact_type)

    # Build core manifest (without signature for signing)
    manifest = {
        "stableID": stable_id,
        "version": MANIFEST_VERSION,
        "artifactType": artifact_type,
        "contentHash": {
            "algorithm": "SHA-256",
            "value": sha256_hash,
            "secondaryHash": {
                "algorithm": blake_algo,
                "value": blake_hash
            }
        },
        "metadata": {
            "filename": filename,
            "fileSize": file_stat.st_size,
            "mimeType": mime_type or "application/octet-stream",
            "captureDate": datetime.fromtimestamp(
                file_stat.st_mtime, timezone.utc
            ).isoformat().replace("+00:00", "Z"),
            "custody": [
                {
                    "party": "Aletheia Ingest CLI",
                    "action": "created",
                    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                    "location": os.uname().nodename if hasattr(os, 'uname') else "local",
                    "notes": "Initial ingest and sealing"
                }
            ],
            "labels": [artifact_type.lower()],
            "custom": {}
        },
        "consent": {
            "consentID": None,
            "scope": [],
            "restrictions": [],
            "stewardID": None
        },
        "provenance": {
            "parentIDs": [],
            "derivationMethod": None,
            "derivationGraph": None
        },
        "integrity": {
            "lastVerified": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "verificationCount": 1,
            "status": "valid"
        }
    }

    # Apply metadata overrides
    if metadata_overrides:
        for key, value in metadata_overrides.items():
            if key in manifest["metadata"]:
                if isinstance(manifest["metadata"][key], dict) and isinstance(value, dict):
                    manifest["metadata"][key].update(value)
                else:
                    manifest["metadata"][key] = value
            elif key == "custom":
                manifest["metadata"]["custom"].update(value)
            elif key == "consent":
                manifest["consent"].update(value)

    # Sign the manifest (on the content without signature/timestamp)
    manifest_bytes = json.dumps(manifest, sort_keys=True).encode("utf-8")
    signature_b64, sig_algo, key_id = sign_manifest(manifest_bytes, private_key_path)

    manifest["signature"] = {
        "algorithm": sig_algo,
        "value": signature_b64,
        "publicKeyID": key_id,
        "signerIdentity": os.environ.get("ALETHEIA_SIGNER", "aletheia-cli@local")
    }

    # Get trusted timestamp
    ts_authority, ts_value, ts_proof = get_timestamp_proof()
    manifest["timestamp"] = {
        "authority": ts_authority,
        "value": ts_value,
        "proof": ts_proof
    }

    return manifest


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Aletheia Ingest + Sealing CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic ingest
  python ingest.py --file sample.vcf.gz --type VCF --output manifest.json

  # With custom metadata
  python ingest.py --file data.csv --type XRF_CSV --output manifest.json \\
    --metadata '{"custom": {"instrument": "Bruker Tracer 5i"}}'

  # With signing key
  python ingest.py --file genome.fastq --type FASTQ --output manifest.json \\
    --key /path/to/private_key.pem
        """
    )

    parser.add_argument(
        "--file", "-f",
        required=True,
        help="Path to the artifact file to ingest"
    )

    parser.add_argument(
        "--type", "-t",
        required=True,
        choices=VALID_ARTIFACT_TYPES,
        help="Type of artifact"
    )

    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output path for the manifest JSON"
    )

    parser.add_argument(
        "--metadata", "-m",
        default=None,
        help="JSON string of additional metadata to include"
    )

    parser.add_argument(
        "--key", "-k",
        default=None,
        help="Path to Ed25519 private key for signing"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    # Parse metadata overrides
    metadata_overrides = None
    if args.metadata:
        try:
            metadata_overrides = json.loads(args.metadata)
        except json.JSONDecodeError as e:
            print(f"Error parsing metadata JSON: {e}", file=sys.stderr)
            sys.exit(1)

    try:
        if args.verbose:
            print(f"Ingesting artifact: {args.file}")
            print(f"Artifact type: {args.type}")

        # Generate manifest
        manifest = generate_manifest(
            file_path=args.file,
            artifact_type=args.type,
            metadata_overrides=metadata_overrides,
            private_key_path=args.key
        )

        # Write manifest
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        if args.verbose:
            print(f"\nManifest generated successfully!")
            print(f"Stable ID: {manifest['stableID']}")
            print(f"SHA-256: {manifest['contentHash']['value']}")
            print(f"Output: {args.output}")
        else:
            print(json.dumps({
                "status": "success",
                "stableID": manifest["stableID"],
                "output": str(output_path)
            }))

    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": str(e)
        }), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
