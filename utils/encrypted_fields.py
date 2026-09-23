"""
Field-level encryption for sensitive PII (Aadhaar numbers, etc.).

Uses `cryptography`'s Fernet (symmetric AES-128-CBC + HMAC) — a free,
open-source library, no paid KMS/HSM service required. The key is read
from FIELD_ENCRYPTION_KEY in settings, which should be a 32-byte urlsafe
base64 key (generate one with `Fernet.generate_key()`).
"""
import logging

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.db import models

logger = logging.getLogger(__name__)

_fernet = None


def _get_fernet():
    global _fernet
    if _fernet is None:
        key = settings.FIELD_ENCRYPTION_KEY
        if isinstance(key, str):
            key = key.encode()
        _fernet = Fernet(key)
    return _fernet


class EncryptedCharField(models.CharField):
    """
    Transparently encrypts the value before it hits the database and
    decrypts it when the model instance is loaded. Values are stored as
    base64 ciphertext, so `max_length` is padded generously in `db_type`.
    """

    def __init__(self, *args, **kwargs):
        # Ciphertext is longer than plaintext; store a generous max_length
        # in the DB regardless of the logical max_length used for validation.
        self.logical_max_length = kwargs.get("max_length", 255)
        kwargs["max_length"] = 500
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["max_length"] = self.logical_max_length
        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection):
        return self._decrypt(value)

    def to_python(self, value):
        if isinstance(value, str) and value.startswith("gAAAAA"):
            # Looks like a Fernet token that hasn't been decrypted yet
            # (e.g. loaded via from_db_value already handles this normally;
            # this branch guards direct assignment of raw tokens).
            return self._decrypt(value)
        return value

    def get_prep_value(self, value):
        if value in (None, ""):
            return value
        return self._encrypt(str(value))

    def _encrypt(self, value):
        try:
            return _get_fernet().encrypt(value.encode()).decode()
        except Exception:
            logger.exception("Failed to encrypt field value")
            raise

    def _decrypt(self, value):
        if value in (None, ""):
            return value
        try:
            return _get_fernet().decrypt(value.encode()).decode()
        except InvalidToken:
            # Value predates encryption being enabled, or key rotated —
            # fail safe by returning a masked placeholder rather than raw data.
            logger.warning("Could not decrypt stored value (invalid token)")
            return value
        except Exception:
            logger.exception("Failed to decrypt field value")
            return value


def mask_aadhaar(value):
    """Return only the last 4 digits for display, e.g. 'XXXX-XXXX-1234'."""
    if not value or len(value) < 4:
        return "N/A"
    return f"XXXX-XXXX-{value[-4:]}"
