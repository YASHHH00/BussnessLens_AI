"""
BusinessLens AI — Security: JWT, Password Hashing, Fernet Encryption

Responsibilities:
- JWT access/refresh token creation and decoding
- bcrypt password hashing and verification
- Fernet symmetric encryption for credentials stored at rest
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from cryptography.fernet import Fernet, InvalidToken
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# ------------------------------------------------------------------ #
# Password hashing (bcrypt)
# ------------------------------------------------------------------ #

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if the plaintext matches the bcrypt hash."""
    return _pwd_context.verify(plain, hashed)


# ------------------------------------------------------------------ #
# JWT
# ------------------------------------------------------------------ #

def _build_token(
    subject: str,
    token_type: str,
    expires_delta: timedelta,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Internal helper — build a signed JWT with standard + custom claims."""
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(
    user_id: UUID,
    organization_id: UUID,
    role: str,
) -> str:
    """
    Create a short-lived access token.
    Embeds user_id, organization_id, and role as claims for RBAC checks.
    """
    return _build_token(
        subject=str(user_id),
        token_type="access",
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        extra_claims={
            "org": str(organization_id),
            "role": role,
        },
    )


def create_refresh_token(user_id: UUID) -> str:
    """
    Create a long-lived refresh token.
    Contains only the subject — no role/org (must be re-looked-up on refresh).
    """
    return _build_token(
        subject=str(user_id),
        token_type="refresh",
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT.

    Returns the payload dict on success.
    Raises JWTError on invalid/expired tokens — callers should catch this.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


# ------------------------------------------------------------------ #
# Fernet — Symmetric Encryption (credentials at rest)
# ------------------------------------------------------------------ #

class FernetEncryptor:
    """
    Wraps Fernet symmetric encryption for storing sensitive credentials
    (database passwords) in encrypted form at rest.

    The key is loaded from FERNET_KEY env var once at startup.
    """

    def __init__(self, key: str) -> None:
        try:
            self._fernet = Fernet(key.encode() if isinstance(key, str) else key)
        except Exception as exc:
            raise ValueError(
                "Invalid FERNET_KEY. Generate a valid key with: "
                "python -c \"from cryptography.fernet import Fernet; "
                "print(Fernet.generate_key().decode())\""
            ) from exc

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a plaintext string, returning a base64-encoded ciphertext string."""
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt a ciphertext string back to plaintext.
        Raises ValueError if the token is invalid or corrupted.
        """
        try:
            return self._fernet.decrypt(ciphertext.encode()).decode()
        except InvalidToken as exc:
            raise ValueError(
                "Decryption failed — ciphertext is invalid or key mismatch."
            ) from exc


# Module-level singleton — initialized once from config
_encryptor: FernetEncryptor | None = None


def get_encryptor() -> FernetEncryptor:
    """Return the singleton Fernet encryptor, creating it on first call."""
    global _encryptor
    if _encryptor is None:
        _encryptor = FernetEncryptor(settings.FERNET_KEY)
    return _encryptor


def encrypt_credential(plaintext: str) -> str:
    """Convenience function — encrypt a credential string."""
    return get_encryptor().encrypt(plaintext)


def decrypt_credential(ciphertext: str) -> str:
    """Convenience function — decrypt a credential string."""
    return get_encryptor().decrypt(ciphertext)
