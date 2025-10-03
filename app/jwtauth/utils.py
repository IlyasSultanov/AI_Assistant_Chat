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
    """
    Кодирует JWT токен с указанными параметрами.
    
    Args:
        payload: Данные для включения в токен
        private_key: Приватный ключ для подписи
        algorithm: Алгоритм подписи (по умолчанию RS256)
        expires_in: Время жизни токена в минутах
        expires_timedelta: Альтернативный способ указания времени жизни
        issuer: Издатель токена
        audience: Аудитория токена
        
    Returns:
        str: Закодированный JWT токен
    """
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
    """
    Декодирует и проверяет JWT токен.
    
    Args:
        token: JWT токен для декодирования
        public_key: Публичный ключ для проверки подписи
        algorithm: Алгоритм подписи
        issuer: Ожидаемый издатель токена
        audience: Ожидаемая аудитория токена
        
    Returns:
        Dict[str, Any]: Декодированный payload токена
        
    Raises:
        InvalidTokenError: При некорректном токене или неверной подписи
    """
    decoded = pyjwt.decode(
        token,
        public_key,
        algorithms=[algorithm],
        audience=audience,
        issuer=issuer,
    )
    return decoded


def hash_password(password: str) -> bytes:
    """
    Хэширует пароль с использованием bcrypt.
    
    Args:
        password: Пароль в открытом виде
        
    Returns:
        bytes: Хэшированный пароль для хранения в БД
    """
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password.encode(), salt)
    return hashed_bytes


def validate_password(password: str, hash_pass: bytes) -> bool:
    """
    Проверяет пароль против хэша.
    
    Args:
        password: Пароль в открытом виде
        hash_pass: Хэшированный пароль из БД (bytes)
        
    Returns:
        bool: True если пароль совпадает, False иначе
    """
    return bcrypt.checkpw(password.encode(), hash_pass)
