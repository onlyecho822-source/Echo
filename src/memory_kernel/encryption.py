"""
Encryption Engine - AES-256-GCM encryption for Memory Kernel

Provides secure encryption for all personal data storage.
"""

import os
import base64
import hashlib
from typing import Optional
from dataclasses import dataclass


@dataclass
class EncryptedData:
    """Container for encrypted data with metadata."""
    ciphertext: bytes
    nonce: bytes
    tag: bytes
    salt: bytes


class EncryptionEngine:
    """
    AES-256-GCM encryption engine for the Memory Kernel.

    Uses PBKDF2 for key derivation and AES-GCM for authenticated encryption.
    """

    KEY_LENGTH = 32  # 256 bits
    SALT_LENGTH = 16
    NONCE_LENGTH = 12
    ITERATIONS = 100000

    def __init__(self, master_password: str):
        """
        Initialize encryption engine with master password.

        Args:
            master_password: User's master password for key derivation
        """
        self._master_password = master_password
        self._salt: Optional[bytes] = None
        self._key: Optional[bytes] = None

    def _derive_key(self, salt: bytes) -> bytes:
        """
        Derive encryption key from master password using PBKDF2.

        Args:
            salt: Random salt for key derivation

        Returns:
            Derived key bytes
        """
        return hashlib.pbkdf2_hmac(
            'sha256',
            self._master_password.encode('utf-8'),
            salt,
            self.ITERATIONS,
            dklen=self.KEY_LENGTH
        )

    def encrypt(self, plaintext: bytes) -> EncryptedData:
        """
        Encrypt data using AES-256-GCM.

        Args:
            plaintext: Data to encrypt

        Returns:
            EncryptedData containing ciphertext and metadata
        """
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        except ImportError:
            raise ImportError(
                "cryptography package required. Install with: pip install cryptography"
            )

        salt = os.urandom(self.SALT_LENGTH)
        key = self._derive_key(salt)
        nonce = os.urandom(self.NONCE_LENGTH)

        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)

        # GCM appends the tag to ciphertext, extract it
        tag = ciphertext[-16:]
        ciphertext = ciphertext[:-16]

        return EncryptedData(
            ciphertext=ciphertext,
            nonce=nonce,
            tag=tag,
            salt=salt
        )

    def decrypt(self, encrypted_data: EncryptedData) -> bytes:
        """
        Decrypt data using AES-256-GCM.

        Args:
            encrypted_data: EncryptedData object to decrypt

        Returns:
            Decrypted plaintext bytes

        Raises:
            ValueError: If decryption fails (wrong password or corrupted data)
        """
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        except ImportError:
            raise ImportError(
                "cryptography package required. Install with: pip install cryptography"
            )

        key = self._derive_key(encrypted_data.salt)
        aesgcm = AESGCM(key)

        # Reconstruct ciphertext with tag
        ciphertext_with_tag = encrypted_data.ciphertext + encrypted_data.tag

        try:
            plaintext = aesgcm.decrypt(
                encrypted_data.nonce,
                ciphertext_with_tag,
                None
            )
            return plaintext
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")

    def encrypt_string(self, plaintext: str) -> str:
        """
        Encrypt a string and return base64-encoded result.

        Args:
            plaintext: String to encrypt

        Returns:
            Base64-encoded encrypted data
        """
        encrypted = self.encrypt(plaintext.encode('utf-8'))

        # Pack all components into a single base64 string
        packed = (
            encrypted.salt +
            encrypted.nonce +
            encrypted.tag +
            encrypted.ciphertext
        )
        return base64.b64encode(packed).decode('ascii')

    def decrypt_string(self, encrypted_b64: str) -> str:
        """
        Decrypt a base64-encoded encrypted string.

        Args:
            encrypted_b64: Base64-encoded encrypted data

        Returns:
            Decrypted string
        """
        packed = base64.b64decode(encrypted_b64)

        # Unpack components
        salt = packed[:self.SALT_LENGTH]
        nonce = packed[self.SALT_LENGTH:self.SALT_LENGTH + self.NONCE_LENGTH]
        tag = packed[self.SALT_LENGTH + self.NONCE_LENGTH:
                     self.SALT_LENGTH + self.NONCE_LENGTH + 16]
        ciphertext = packed[self.SALT_LENGTH + self.NONCE_LENGTH + 16:]

        encrypted_data = EncryptedData(
            ciphertext=ciphertext,
            nonce=nonce,
            tag=tag,
            salt=salt
        )

        return self.decrypt(encrypted_data).decode('utf-8')

    def secure_wipe(self):
        """Securely wipe key material from memory."""
        if self._key:
            # Overwrite with random data before clearing
            self._key = os.urandom(len(self._key))
            self._key = None
        self._master_password = ""
