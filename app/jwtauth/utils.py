"""
Утилиты для работы с JWT (кодирование/декодирование, пароли).

Добавляет `iss`, `aud`, `iat`, `exp` в токены. Проверяет `iss` и `aud` при
декодировании. Хэширование паролей — через bcrypt.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import bcrypt
import jwt as pyjwt
from app.core.config import settings


def encode_jwt(
    payload: Dict[str, Any],
    private_key: str = settings.auth_settings.private_key.read_text(),
    algorithm: str = settings.auth_settings.algorithm,
    expires_in: int = settings.auth_settings.access_token_expires_minutes,
    expires_timedelta: Optional[timedelta] = None,
    issuer: str = settings.auth_settings.issuer,
    audience: str = settings.auth_settings.audience,
) -> str:
    now = datetime.utcnow()
    exp = now + (expires_timedelta or timedelta(minutes=expires_in))
    to_encode = {**payload, "iss": issuer, "aud": audience, "exp": exp, "iat": now}

    token = pyjwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm,
    )
    return token


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.auth_settings.public_key.read_text(),
    algorithm: str = settings.auth_settings.algorithm,
    issuer: str = settings.auth_settings.issuer,
    audience: str = settings.auth_settings.audience,
) -> Dict[str, Any]:
    decoded = pyjwt.decode(
        token,
        public_key,
        algorithms=[algorithm],
        audience=audience,
        issuer=issuer,
    )
    return decoded


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)


def validate_password(password: str, hash_pass: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hash_pass)
