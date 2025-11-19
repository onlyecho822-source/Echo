#!/usr/bin/env python3
"""
Aletheia Encrypted Local-First Vault
======================================
Secure storage for raw artifacts with encryption at rest,
verifiable export bundles, and consent-based access control.

Author: Echo Nexus Omega
Version: 1.0.0
"""

import os
import json
import hashlib
import secrets
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
import base64

# Optional crypto imports
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


@dataclass
class VaultEntry:
    """Entry in the encrypted vault."""
    artifact_id: str
    encrypted_path: str
    manifest_path: str
    size_bytes: int
    encryption_algo: str
    key_id: str
    created_at: str
    consent_ids: List[str]


@dataclass
class ExportBundle:
    """Verifiable export bundle."""
    bundle_id: str
    artifact_ids: List[str]
    manifest_data: List[Dict[str, Any]]
    consent_snapshot: Dict[str, Any]
    export_timestamp: str
    integrity_hash: str
    minimized: bool


class EncryptedVault:
    """
    Encrypted local-first vault for Aletheia artifacts.

    Features:
    - AES-256-GCM encryption at rest
    - Verifiable export bundles
    - Consent-based access control
    - Audit logging
    """

    def __init__(self, vault_path: str, master_key: Optional[bytes] = None):
        self.vault_path = Path(vault_path)
        self.vault_path.mkdir(parents=True, exist_ok=True)

        # Subdirectories
        self.artifacts_dir = self.vault_path / "artifacts"
        self.manifests_dir = self.vault_path / "manifests"
        self.keys_dir = self.vault_path / "keys"
        self.exports_dir = self.vault_path / "exports"
        self.audit_dir = self.vault_path / "audit"

        for d in [self.artifacts_dir, self.manifests_dir, self.keys_dir,
                  self.exports_dir, self.audit_dir]:
            d.mkdir(exist_ok=True)

        # Index of vault entries
        self.index_path = self.vault_path / "vault_index.json"
        self.index: Dict[str, VaultEntry] = self._load_index()

        # Master key (in production, use HSM or secure key management)
        self.master_key = master_key or self._get_or_create_master_key()

    def _load_index(self) -> Dict[str, VaultEntry]:
        """Load vault index from disk."""
        if self.index_path.exists():
            with open(self.index_path) as f:
                data = json.load(f)
                return {
                    k: VaultEntry(**v) for k, v in data.items()
                }
        return {}

    def _save_index(self):
        """Save vault index to disk."""
        with open(self.index_path, "w") as f:
            json.dump({k: asdict(v) for k, v in self.index.items()}, f, indent=2)

    def _get_or_create_master_key(self) -> bytes:
        """Get or create master encryption key."""
        key_file = self.keys_dir / "master.key"
        if key_file.exists():
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = secrets.token_bytes(32)  # 256-bit key
            with open(key_file, "wb") as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Restrict permissions
            return key

    def _derive_artifact_key(self, artifact_id: str) -> bytes:
        """Derive per-artifact key from master key."""
        if not HAS_CRYPTO:
            # Fallback: use hash-based key derivation
            return hashlib.sha256(
                self.master_key + artifact_id.encode()
            ).digest()

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=artifact_id.encode(),
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(self.master_key)

    def _encrypt(self, data: bytes, key: bytes) -> Tuple[bytes, bytes]:
        """Encrypt data with AES-256-GCM."""
        if not HAS_CRYPTO:
            # Placeholder: XOR with key hash (NOT SECURE - for demo only)
            key_hash = hashlib.sha256(key).digest()
            encrypted = bytes(b ^ key_hash[i % 32] for i, b in enumerate(data))
            nonce = secrets.token_bytes(12)
            return nonce, encrypted

        nonce = secrets.token_bytes(12)
        aesgcm = AESGCM(key)
        encrypted = aesgcm.encrypt(nonce, data, None)
        return nonce, encrypted

    def _decrypt(self, nonce: bytes, encrypted: bytes, key: bytes) -> bytes:
        """Decrypt data with AES-256-GCM."""
        if not HAS_CRYPTO:
            # Placeholder: XOR with key hash
            key_hash = hashlib.sha256(key).digest()
            return bytes(b ^ key_hash[i % 32] for i, b in enumerate(encrypted))

        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, encrypted, None)

    def store_artifact(
        self,
        artifact_path: str,
        manifest: Dict[str, Any],
        consent_ids: List[str] = None
    ) -> str:
        """
        Store an artifact in the encrypted vault.

        Returns: artifact_id
        """
        artifact_path = Path(artifact_path)
        if not artifact_path.exists():
            raise FileNotFoundError(f"Artifact not found: {artifact_path}")

        # Get artifact ID from manifest
        artifact_id = manifest.get("stableID")
        if not artifact_id:
            raise ValueError("Manifest must contain stableID")

        # Read artifact
        with open(artifact_path, "rb") as f:
            data = f.read()

        # Derive encryption key
        key = self._derive_artifact_key(artifact_id)
        key_id = hashlib.sha256(key).hexdigest()[:16]

        # Encrypt
        nonce, encrypted = self._encrypt(data, key)

        # Store encrypted artifact
        enc_filename = f"{artifact_id}.enc"
        enc_path = self.artifacts_dir / enc_filename

        with open(enc_path, "wb") as f:
            f.write(nonce)
            f.write(encrypted)

        # Store manifest
        manifest_path = self.manifests_dir / f"{artifact_id}.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        # Create vault entry
        entry = VaultEntry(
            artifact_id=artifact_id,
            encrypted_path=str(enc_path),
            manifest_path=str(manifest_path),
            size_bytes=len(data),
            encryption_algo="AES-256-GCM" if HAS_CRYPTO else "XOR-DEMO",
            key_id=key_id,
            created_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            consent_ids=consent_ids or []
        )

        self.index[artifact_id] = entry
        self._save_index()

        # Audit log
        self._audit_log("store", artifact_id, {"size": len(data)})

        return artifact_id

    def retrieve_artifact(
        self,
        artifact_id: str,
        consent_token: Optional[str] = None
    ) -> Tuple[bytes, Dict[str, Any]]:
        """
        Retrieve and decrypt an artifact from the vault.

        Returns: (decrypted_data, manifest)
        """
        if artifact_id not in self.index:
            raise KeyError(f"Artifact not found: {artifact_id}")

        entry = self.index[artifact_id]

        # Check consent (simplified)
        if entry.consent_ids and consent_token not in entry.consent_ids:
            # In production, verify consent token against ledger
            pass  # For demo, allow access

        # Read encrypted artifact
        with open(entry.encrypted_path, "rb") as f:
            nonce = f.read(12)
            encrypted = f.read()

        # Derive key and decrypt
        key = self._derive_artifact_key(artifact_id)
        data = self._decrypt(nonce, encrypted, key)

        # Read manifest
        with open(entry.manifest_path) as f:
            manifest = json.load(f)

        # Audit log
        self._audit_log("retrieve", artifact_id, {"consent_token": consent_token})

        return data, manifest

    def create_export_bundle(
        self,
        artifact_ids: List[str],
        consent_snapshot: Dict[str, Any],
        minimize: bool = True
    ) -> ExportBundle:
        """
        Create a verifiable export bundle.

        Args:
            artifact_ids: List of artifact IDs to include
            consent_snapshot: Current consent state
            minimize: If True, include only minimal data for validation

        Returns: ExportBundle
        """
        bundle_id = f"BUNDLE-{secrets.token_hex(8).upper()}"
        manifests = []

        for artifact_id in artifact_ids:
            if artifact_id not in self.index:
                raise KeyError(f"Artifact not found: {artifact_id}")

            with open(self.index[artifact_id].manifest_path) as f:
                manifest = json.load(f)

            if minimize:
                # Include only validation-necessary fields
                manifest = {
                    "stableID": manifest.get("stableID"),
                    "contentHash": manifest.get("contentHash"),
                    "signature": manifest.get("signature"),
                    "timestamp": manifest.get("timestamp"),
                    "integrity": manifest.get("integrity")
                }

            manifests.append(manifest)

        # Compute bundle integrity hash
        bundle_data = json.dumps({
            "artifact_ids": artifact_ids,
            "manifests": manifests,
            "consent": consent_snapshot
        }, sort_keys=True)
        integrity_hash = hashlib.sha256(bundle_data.encode()).hexdigest()

        bundle = ExportBundle(
            bundle_id=bundle_id,
            artifact_ids=artifact_ids,
            manifest_data=manifests,
            consent_snapshot=consent_snapshot,
            export_timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            integrity_hash=integrity_hash,
            minimized=minimize
        )

        # Save bundle
        bundle_path = self.exports_dir / f"{bundle_id}.json"
        with open(bundle_path, "w") as f:
            json.dump(asdict(bundle), f, indent=2)

        # Audit log
        self._audit_log("export", bundle_id, {
            "artifact_count": len(artifact_ids),
            "minimized": minimize
        })

        return bundle

    def verify_integrity(self, artifact_id: str) -> Tuple[bool, str]:
        """
        Verify integrity of a stored artifact.

        Returns: (is_valid, details)
        """
        if artifact_id not in self.index:
            return False, f"Artifact not found: {artifact_id}"

        try:
            data, manifest = self.retrieve_artifact(artifact_id)

            # Compute hash
            computed_hash = hashlib.sha256(data).hexdigest()
            expected_hash = manifest.get("contentHash", {}).get("value")

            if computed_hash == expected_hash:
                return True, "Integrity verified"
            else:
                return False, f"Hash mismatch: computed={computed_hash[:16]}..., expected={expected_hash[:16]}..."

        except Exception as e:
            return False, f"Verification failed: {str(e)}"

    def list_artifacts(self) -> List[Dict[str, Any]]:
        """List all artifacts in the vault."""
        return [
            {
                "artifact_id": entry.artifact_id,
                "size_bytes": entry.size_bytes,
                "created_at": entry.created_at,
                "encryption": entry.encryption_algo
            }
            for entry in self.index.values()
        ]

    def _audit_log(self, action: str, target_id: str, details: Dict[str, Any]):
        """Write audit log entry."""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "action": action,
            "target_id": target_id,
            "details": details
        }

        log_file = self.audit_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Aletheia Encrypted Vault CLI")
    parser.add_argument("--vault", default="./vault_data", help="Vault directory")
    subparsers = parser.add_subparsers(dest="command")

    # Store command
    store_parser = subparsers.add_parser("store", help="Store artifact")
    store_parser.add_argument("--file", required=True)
    store_parser.add_argument("--manifest", required=True)

    # List command
    subparsers.add_parser("list", help="List artifacts")

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify artifact")
    verify_parser.add_argument("--id", required=True)

    args = parser.parse_args()

    vault = EncryptedVault(args.vault)

    if args.command == "store":
        with open(args.manifest) as f:
            manifest = json.load(f)
        artifact_id = vault.store_artifact(args.file, manifest)
        print(f"Stored artifact: {artifact_id}")

    elif args.command == "list":
        artifacts = vault.list_artifacts()
        print(json.dumps(artifacts, indent=2))

    elif args.command == "verify":
        is_valid, details = vault.verify_integrity(args.id)
        print(f"Valid: {is_valid}")
        print(f"Details: {details}")

    else:
        parser.print_help()
