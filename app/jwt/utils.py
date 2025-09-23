"""
JWT utilities for encoding and decoding JWT tokens.

This module provides functions to encode and decode JWT tokens.
"""

import jwt
from app.core.config import settings


def encode_jwt(
    payload: dict,  # type: ignore
    private_key: str = settings.auth_jwt.private_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
):
    encoded = jwt.encode(
        payload,  # type: ignore
        private_key,
        algorithm=algorithm,
    )
    return encoded


def decoded_jwt(
    token: str | bytes,
    public_key: str = settings.auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
):
    decoded = jwt.decode(token, public_key, algorithm=[algorithm])
    return decoded