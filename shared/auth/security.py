from __future__ import annotations

import hashlib
import hmac
import secrets


def hash_password(password: str, *, salt: str | None = None, iterations: int = 200_000) -> str:
    salt_value = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt_value.encode("utf-8"),
        iterations,
    )
    return f"pbkdf2_sha256${iterations}${salt_value}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt, hash_hex = encoded.split("$", 3)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    expected = hash_password(password, salt=salt, iterations=int(iterations))
    return hmac.compare_digest(expected, encoded)


def generate_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def normalize_password_hash(password: str, salt: str | None = None) -> str:
    return hash_password(password, salt=salt)
