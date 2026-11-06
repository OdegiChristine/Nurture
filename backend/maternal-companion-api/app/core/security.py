"""Passwords, JWTs, and protection of phone numbers (the most sensitive identifier we hold)."""

import hashlib
import hmac
from datetime import timedelta
from functools import lru_cache
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from cryptography.fernet import Fernet

from app.core.config import get_settings
from app.core.time import utcnow

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, InvalidHashError):
        return False


# --- Phone numbers -----------------------------------------------------------------------------


def normalize_msisdn(raw: str) -> str:
    """Return a Kenyan number as +2547XXXXXXXX / +2541XXXXXXXX. Raises ValueError otherwise."""
    digits = "".join(ch for ch in raw if ch.isdigit())
    if digits.startswith("254") and len(digits) == 12:
        pass
    elif digits.startswith("0") and len(digits) == 10:
        digits = "254" + digits[1:]
    elif len(digits) == 9 and digits[0] in "71":
        digits = "254" + digits
    else:
        raise ValueError("Unrecognised Kenyan phone number")
    return "+" + digits


def phone_hash(msisdn: str) -> str:
    """Keyed hash used for lookups, so the plaintext number is never a query key."""
    pepper = get_settings().phone_hash_pepper.get_secret_value().encode()
    return hmac.new(pepper, msisdn.encode(), hashlib.sha256).hexdigest()


@lru_cache
def _fernet() -> Fernet:
    return Fernet(get_settings().field_encryption_key.get_secret_value().encode())


def encrypt_field(plaintext: str) -> bytes:
    return _fernet().encrypt(plaintext.encode())


def decrypt_field(ciphertext: bytes) -> str:
    return _fernet().decrypt(ciphertext).decode()


# --- Tokens ------------------------------------------------------------------------------------


def create_access_token(subject: str, role: str) -> str:
    settings = get_settings()
    now = utcnow()
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_minutes),
    }
    return jwt.encode(
        payload, settings.jwt_secret.get_secret_value(), algorithm=settings.jwt_algorithm
    )


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    return jwt.decode(
        token,
        settings.jwt_secret.get_secret_value(),
        algorithms=[settings.jwt_algorithm],
        options={"require": ["exp", "sub", "role"]},
    )
