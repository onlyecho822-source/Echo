#!/usr/bin/env python3
"""
Echo Secrets Escrow System
Multi-layer secret retrieval with fallback cascade

Priority Order:
1. AWS Secrets Manager (production)
2. Local encrypted vault (development/fallback)
3. Environment variables (development only)
4. Fail securely with alerts
"""

import os
import json
import boto3
import logging
from typing import Optional, Dict
from pathlib import Path
from cryptography.fernet import Fernet
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('echo.secrets')


class SecretNotFoundError(Exception):
    """Raised when secret cannot be found in any layer"""
    pass


@dataclass
class SecretMetadata:
    """Metadata about secret retrieval"""
    secret_name: str
    source: str  # 'aws', 'vault', 'env', or 'none'
    retrieved_at: str
    rotation_due: Optional[str] = None


class SecretsEscrow:
    """Multi-layer secrets management system"""

    def __init__(
        self,
        aws_region: str = 'us-east-1',
        vault_path: str = '/opt/echo/secrets.vault',
        environment: str = None
    ):
        self.aws_region = aws_region
        self.vault_path = Path(vault_path)
        self.environment = environment or os.getenv('ECHO_ENVIRONMENT', 'production')

        # Initialize AWS Secrets Manager client
        try:
            self.secrets_client = boto3.client(
                'secretsmanager',
                region_name=self.aws_region
            )
            self.aws_available = True
        except Exception as e:
            logger.warning(f"AWS Secrets Manager unavailable: {e}")
            self.aws_available = False

        # Load local vault encryption key
        self.vault_key = self._load_vault_key()

    def _load_vault_key(self) -> Optional[Fernet]:
        """Load encryption key for local vault"""
        key_path = Path('/opt/echo/.vault_key')

        if not key_path.exists():
            logger.warning(f"Vault key not found at {key_path}")
            return None

        try:
            with open(key_path, 'rb') as f:
                key = f.read()
            return Fernet(key)
        except Exception as e:
            logger.error(f"Failed to load vault key: {e}")
            return None

    def get_secret(self, secret_name: str) -> str:
        """
        Retrieve secret with fallback cascade

        Args:
            secret_name: Name of the secret to retrieve

        Returns:
            Secret value as string

        Raises:
            SecretNotFoundError: If secret not found in any layer
        """
        # Layer 1: AWS Secrets Manager
        if self.aws_available:
            try:
                secret = self._get_from_aws(secret_name)
                if secret:
                    logger.info(f"Retrieved {secret_name} from AWS Secrets Manager")
                    return secret
            except Exception as e:
                logger.warning(f"AWS retrieval failed for {secret_name}: {e}")
                self._alert_layer_failure('aws', secret_name, str(e))

        # Layer 2: Local encrypted vault
        if self.vault_key:
            try:
                secret = self._get_from_vault(secret_name)
                if secret:
                    logger.info(f"Retrieved {secret_name} from local vault")
                    return secret
            except Exception as e:
                logger.warning(f"Vault retrieval failed for {secret_name}: {e}")
                self._alert_layer_failure('vault', secret_name, str(e))

        # Layer 3: Environment variables (development only)
        if self.environment == 'development':
            secret = os.getenv(secret_name)
            if secret:
                logger.warning(
                    f"Retrieved {secret_name} from environment (dev only)"
                )
                return secret

        # Layer 4: Fail securely with alert
        self._alert_critical(f"Secret {secret_name} not found in any layer")
        raise SecretNotFoundError(
            f"Secret '{secret_name}' not found in any retrieval layer"
        )

    def _get_from_aws(self, secret_name: str) -> Optional[str]:
        """Retrieve secret from AWS Secrets Manager"""
        try:
            response = self.secrets_client.get_secret_value(
                SecretId=secret_name
            )

            # Handle string or binary secrets
            if 'SecretString' in response:
                return response['SecretString']
            else:
                return response['SecretBinary'].decode('utf-8')

        except self.secrets_client.exceptions.ResourceNotFoundException:
            return None
        except Exception as e:
            logger.error(f"AWS Secrets Manager error: {e}")
            raise

    def _get_from_vault(self, secret_name: str) -> Optional[str]:
        """Retrieve secret from local encrypted vault"""
        if not self.vault_path.exists():
            return None

        try:
            with open(self.vault_path, 'rb') as f:
                encrypted_data = f.read()

            decrypted_data = self.vault_key.decrypt(encrypted_data)
            vault = json.loads(decrypted_data)

            return vault.get(secret_name)

        except Exception as e:
            logger.error(f"Vault decryption error: {e}")
            raise

    def set_secret(
        self,
        secret_name: str,
        secret_value: str,
        target: str = 'aws'
    ) -> bool:
        """
        Store secret in specified layer

        Args:
            secret_name: Name of the secret
            secret_value: Value to store
            target: 'aws' or 'vault'

        Returns:
            True if successful, False otherwise
        """
        if target == 'aws' and self.aws_available:
            return self._set_in_aws(secret_name, secret_value)
        elif target == 'vault' and self.vault_key:
            return self._set_in_vault(secret_name, secret_value)
        else:
            logger.error(f"Invalid target or target unavailable: {target}")
            return False

    def _set_in_aws(self, secret_name: str, secret_value: str) -> bool:
        """Store secret in AWS Secrets Manager"""
        try:
            # Try to update existing secret
            self.secrets_client.update_secret(
                SecretId=secret_name,
                SecretString=secret_value
            )
            logger.info(f"Updated secret {secret_name} in AWS")
            return True
        except self.secrets_client.exceptions.ResourceNotFoundException:
            # Create new secret if it doesn't exist
            try:
                self.secrets_client.create_secret(
                    Name=secret_name,
                    SecretString=secret_value
                )
                logger.info(f"Created secret {secret_name} in AWS")
                return True
            except Exception as e:
                logger.error(f"Failed to create secret in AWS: {e}")
                return False
        except Exception as e:
            logger.error(f"Failed to update secret in AWS: {e}")
            return False

    def _set_in_vault(self, secret_name: str, secret_value: str) -> bool:
        """Store secret in local encrypted vault"""
        try:
            # Load existing vault or create new one
            if self.vault_path.exists():
                with open(self.vault_path, 'rb') as f:
                    encrypted_data = f.read()
                decrypted_data = self.vault_key.decrypt(encrypted_data)
                vault = json.loads(decrypted_data)
            else:
                vault = {}

            # Update secret
            vault[secret_name] = secret_value

            # Encrypt and save
            encrypted_data = self.vault_key.encrypt(
                json.dumps(vault).encode()
            )

            # Ensure directory exists
            self.vault_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.vault_path, 'wb') as f:
                f.write(encrypted_data)

            # Set restrictive permissions
            os.chmod(self.vault_path, 0o600)

            logger.info(f"Stored secret {secret_name} in vault")
            return True

        except Exception as e:
            logger.error(f"Failed to store secret in vault: {e}")
            return False

    def rotate_secret(
        self,
        secret_name: str,
        new_value: str
    ) -> bool:
        """
        Rotate a secret across all layers

        Args:
            secret_name: Name of the secret to rotate
            new_value: New secret value

        Returns:
            True if rotation successful in at least one layer
        """
        success = False

        if self.aws_available:
            if self._set_in_aws(secret_name, new_value):
                success = True
                logger.info(f"Rotated {secret_name} in AWS")

        if self.vault_key:
            if self._set_in_vault(secret_name, new_value):
                success = True
                logger.info(f"Rotated {secret_name} in vault")

        if success:
            self._alert_info(f"Successfully rotated secret {secret_name}")
        else:
            self._alert_critical(f"Failed to rotate secret {secret_name}")

        return success

    def list_secrets(self, source: str = 'aws') -> list:
        """
        List all secrets in specified source

        Args:
            source: 'aws' or 'vault'

        Returns:
            List of secret names
        """
        if source == 'aws' and self.aws_available:
            try:
                response = self.secrets_client.list_secrets()
                return [s['Name'] for s in response['SecretList']]
            except Exception as e:
                logger.error(f"Failed to list AWS secrets: {e}")
                return []

        elif source == 'vault' and self.vault_key:
            try:
                if not self.vault_path.exists():
                    return []

                with open(self.vault_path, 'rb') as f:
                    encrypted_data = f.read()
                decrypted_data = self.vault_key.decrypt(encrypted_data)
                vault = json.loads(decrypted_data)
                return list(vault.keys())
            except Exception as e:
                logger.error(f"Failed to list vault secrets: {e}")
                return []

        return []

    def _alert_layer_failure(
        self,
        layer: str,
        secret_name: str,
        error: str
    ):
        """Alert that a retrieval layer failed"""
        # In production, this would send to monitoring system
        logger.warning(f"Layer {layer} failed for {secret_name}: {error}")

    def _alert_critical(self, message: str):
        """Send critical alert"""
        # In production, this would trigger PagerDuty, Slack, SMS
        logger.critical(f"CRITICAL ALERT: {message}")

    def _alert_info(self, message: str):
        """Send informational alert"""
        logger.info(f"INFO: {message}")


def initialize_vault(vault_path: str = '/opt/echo/secrets.vault'):
    """
    Initialize a new encrypted vault

    This generates a new encryption key and creates an empty vault.
    The key is stored separately and must be secured.
    """
    key_path = Path('/opt/echo/.vault_key')

    # Generate encryption key
    key = Fernet.generate_key()

    # Save key with restrictive permissions
    key_path.parent.mkdir(parents=True, exist_ok=True)
    with open(key_path, 'wb') as f:
        f.write(key)
    os.chmod(key_path, 0o600)

    # Create empty vault
    fernet = Fernet(key)
    empty_vault = json.dumps({}).encode()
    encrypted = fernet.encrypt(empty_vault)

    vault_path = Path(vault_path)
    vault_path.parent.mkdir(parents=True, exist_ok=True)
    with open(vault_path, 'wb') as f:
        f.write(encrypted)
    os.chmod(vault_path, 0o600)

    print(f"✅ Vault initialized at {vault_path}")
    print(f"🔑 Key stored at {key_path}")
    print("⚠️  SECURE THE KEY FILE - NEVER COMMIT TO GIT")


# Example usage
if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'init':
        initialize_vault()
    else:
        # Example: Retrieve secrets
        escrow = SecretsEscrow()

        try:
            # Try to get a secret
            stripe_key = escrow.get_secret('STRIPE_SECRET_KEY')
            print(f"✅ Retrieved Stripe key: {stripe_key[:10]}...")
        except SecretNotFoundError as e:
            print(f"❌ {e}")

        # List secrets
        print("\n📋 AWS Secrets:")
        for secret in escrow.list_secrets('aws'):
            print(f"  - {secret}")

        print("\n📋 Vault Secrets:")
        for secret in escrow.list_secrets('vault'):
            print(f"  - {secret}")
