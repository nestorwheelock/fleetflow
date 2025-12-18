import base64
import hashlib

from cryptography.fernet import Fernet
from django.conf import settings

_cached_key = None


def get_encryption_key():
    """Get or generate the encryption key for API key storage.

    The key is derived from FIELD_ENCRYPTION_KEY setting using SHA-256,
    then base64 encoded to create a valid Fernet key.
    """
    global _cached_key
    if _cached_key is not None:
        return _cached_key

    key = getattr(settings, 'FIELD_ENCRYPTION_KEY', '')
    if not key:
        _cached_key = Fernet.generate_key()
        return _cached_key

    if isinstance(key, str):
        key = key.encode()

    derived_key = hashlib.sha256(key).digest()
    _cached_key = base64.urlsafe_b64encode(derived_key)
    return _cached_key


def reset_encryption_key_cache():
    """Reset the cached encryption key (useful for testing)."""
    global _cached_key
    _cached_key = None


def encrypt_api_key(api_key):
    """Encrypt an API key for secure storage.

    Args:
        api_key: The plaintext API key string

    Returns:
        bytes: The encrypted API key
    """
    if not api_key:
        return None
    key = get_encryption_key()
    f = Fernet(key)
    return f.encrypt(api_key.encode())


def decrypt_api_key(encrypted_key):
    """Decrypt an encrypted API key.

    Args:
        encrypted_key: The encrypted API key bytes

    Returns:
        str: The decrypted API key, or None if decryption fails
    """
    if not encrypted_key:
        return None
    try:
        key = get_encryption_key()
        f = Fernet(key)
        return f.decrypt(bytes(encrypted_key)).decode()
    except Exception:
        return None
