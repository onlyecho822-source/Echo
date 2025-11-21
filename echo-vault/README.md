# Echo Vault

## Overview
Echo Vault is the secure identity, secrets, and state management layer for the Echo system. It provides enterprise-grade security for credentials, API keys, and sensitive data.

## Components

### 1. Authentication Manager (`auth/auth_manager.py`)
Handles user authentication and authorization:
- API key generation and validation
- JWT token creation and verification
- Session management
- Permission-based access control

### 2. Secrets Manager (`secrets/secrets_manager.py`)
Secure storage for sensitive data:
- Encrypted secrets storage using Fernet encryption
- Master key rotation
- Import/export of encrypted secrets
- Pre-configured credential stores for common services

### 3. State Manager (`state/`)
Persistent state management:
- Session state persistence
- Agent state tracking
- Configuration storage

## Features

- **Military-Grade Encryption**: AES-256 encryption for all stored secrets
- **Multiple Auth Methods**: API keys, JWT, OAuth2, Basic Auth
- **Key Rotation**: Seamless master key rotation without service interruption
- **Session Management**: Secure session handling with automatic expiry
- **Permission System**: Fine-grained RBAC (Role-Based Access Control)
- **Audit Logging**: Comprehensive audit trail for all access

## Usage Examples

### Authentication

```python
from echo_vault.auth import AuthManager

# Initialize
auth = AuthManager(secret_key="your-secret-key")

# Generate API key
api_key = auth.generate_api_key(
    user_id="user@example.com",
    permissions=["read", "write"]
)

# Verify API key
key_data = auth.verify_api_key(api_key)
if key_data:
    print(f"Valid key for user: {key_data['user_id']}")

# Create JWT token
token = auth.create_jwt_token(
    user_id="user@example.com",
    permissions=["read", "write"],
    custom_claims={"org_id": "123"}
)

# Verify JWT
payload = auth.verify_jwt_token(token)
```

### Secrets Management

```python
from echo_vault.secrets import SecretsManager, CredentialsStore

# Initialize
sm = SecretsManager()
creds = CredentialsStore(sm)

# Store API credentials
creds.store_api_credentials(
    service="stripe",
    api_key="sk_test_xxxxx",
    api_secret="secret_xxxxx"
)

# Store database credentials
creds.store_database_url(
    db_name="production",
    connection_url="postgresql://user:pass@host:5432/db"
)

# Store OAuth credentials
creds.store_oauth_credentials(
    service="google",
    client_id="xxxxx.apps.googleusercontent.com",
    client_secret="xxxxx",
    refresh_token="xxxxx"
)

# Retrieve credentials
stripe_creds = creds.get_api_credentials("stripe")
db_url = creds.get_database_url("production")

# Export encrypted backup
sm.export_secrets("backup.enc", password="strong-password")

# Import from backup
sm.import_secrets("backup.enc", password="strong-password")
```

## Security Best Practices

1. **Never commit secrets**: Use `.env` files or external secret stores
2. **Rotate keys regularly**: Implement key rotation policies
3. **Use strong master keys**: Generate with `Fernet.generate_key()`
4. **Limit permissions**: Grant minimum required permissions
5. **Monitor access**: Enable audit logging for all secret access
6. **Backup encrypted**: Always encrypt secret backups

## Integration with Business Systems

### CRM Integration
```python
# Store Salesforce credentials
creds.store_oauth_credentials(
    service="salesforce",
    client_id="your-client-id",
    client_secret="your-client-secret",
    refresh_token="your-refresh-token"
)
```

### Payment Processing
```python
# Store Stripe credentials
creds.store_api_credentials(
    service="stripe",
    api_key="sk_live_xxxxx"
)
```

### Cloud Services
```python
# Store AWS credentials
sm.store_secret("aws_access_key_id", "AKIA...")
sm.store_secret("aws_secret_access_key", "secret...")
```

## Environment Variables

```bash
# Required
ECHO_VAULT_MASTER_KEY=<base64-encoded-key>
ECHO_VAULT_SECRET_KEY=<jwt-signing-key>

# Optional
ECHO_VAULT_TOKEN_EXPIRY_HOURS=24
ECHO_VAULT_ENABLE_AUDIT=true
ECHO_VAULT_LOG_LEVEL=INFO
```

## API Endpoints

When integrated with Echo API:

- `POST /vault/auth/login` - Authenticate user
- `POST /vault/auth/api-key` - Generate API key
- `GET /vault/auth/verify` - Verify token
- `POST /vault/secrets` - Store secret
- `GET /vault/secrets/:key` - Retrieve secret
- `DELETE /vault/secrets/:key` - Delete secret
- `POST /vault/secrets/export` - Export encrypted backup

## Dependencies

```
cryptography>=41.0.0
PyJWT>=2.8.0
```

Install with:
```bash
pip install cryptography PyJWT
```
