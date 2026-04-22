import base64
import hashlib
import hmac
import os


PBKDF2_ITERATIONS = 600_000
PBKDF2_DIGEST = "sha256"


def _encode_bytes(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def _decode_bytes(value: str) -> bytes:
    return base64.b64decode(value.encode("ascii"))


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived_key = hashlib.pbkdf2_hmac(
        PBKDF2_DIGEST,
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return f"pbkdf2_{PBKDF2_DIGEST}${PBKDF2_ITERATIONS}${_encode_bytes(salt)}${_encode_bytes(derived_key)}"


def verify_password(password: str, password_hash_value: str) -> bool:
    algorithm, iteration_count, encoded_salt, encoded_hash = password_hash_value.split("$", maxsplit=3)
    if algorithm != f"pbkdf2_{PBKDF2_DIGEST}":
        return False

    derived_key = hashlib.pbkdf2_hmac(
        PBKDF2_DIGEST,
        password.encode("utf-8"),
        _decode_bytes(encoded_salt),
        int(iteration_count),
    )
    return hmac.compare_digest(_encode_bytes(derived_key), encoded_hash)
