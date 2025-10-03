from fastapi import Depends, Form, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Dict, Any

from app.db.database import get_db
from app.jwtauth import utils as auth_utils
from app.models.user_models import Users
from app.schemas.userschema import UserSchema, UserCreate, UserRead
from app.exceptions import (
    AuthException,
    ForbiddenException,
)
from app.jwtauth.utils import hash_password


http_bearer = HTTPBearer()
# async def authenticate(
#     credentials: HTTPBearer,
# ):


async def create_user(db: AsyncSession, user: UserCreate) -> Dict[str, Any]:
    """
    Создает нового пользователя в базе данных.
    
    Args:
        db: Сессия базы данных
        user: Данные для создания пользователя
        
    Returns:
        Dict[str, Any]: Результат операции с данными пользователя или ошибкой
        
    Raises:
        IntegrityError: При попытке создать пользователя с существующим username/email
    """
    hashed_password = hash_password(user.password)
    user_obj = Users(
        username=user.username,
        email=user.email,
        password=hashed_password,
    )

    db.add(user_obj)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        return {
            "status": "error",
            "detail": "User with this username or email already exists",
        }
    await db.refresh(user_obj)
    # Не включаем hashed_password в ответ
    return {
        "status": "ok",
        "user": UserRead(
            id=user_obj.id,
            username=user_obj.username,
            email=user_obj.email,
            is_active=user_obj.is_active,
            created_at=user_obj.created_at,
            updated_at=user_obj.updated_at,
            deleted_at=user_obj.deleted_at,
        ),
    }


async def _get_user_by_username(db: AsyncSession, username: str) -> Users | None:
    """Возвращает пользователя по имени или None, если не найден.

    Не изменяет состояние БД. Используется для устранения дублирования кода.
    """
    result = await db.execute(select(Users).where(Users.username == username))
    return result.scalars().first()


async def validate_auth_user(
    username: str = Form(),
    password: str = Form(),
    db: AsyncSession = Depends(get_db),
) -> UserSchema:
    """Валидирует учетные данные пользователя.

    - Ищет пользователя по имени в БД
    - Сравнивает пароль с bcrypt-хэшем
    - Проверяет, что пользователь активен

    Возвращает `UserSchema` без изменения внешнего поведения эндпоинтов.
    """
    unauthorized_exc = AuthException(
        status_code=status.HTTP_401_UNAUTHORIZED, message="Unauthorized"
    )

    user: Users | None = await _get_user_by_username(db, username)
    if user is None:
        raise unauthorized_exc

    if not auth_utils.validate_password(password, user.password):
        raise unauthorized_exc

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return UserSchema(
        id=user.id,
        username=user.username,
        password=user.password,
        email=user.email,
        active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
        deleted_at=user.deleted_at,
    )


def get_current_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> dict:
    """
    Извлекает и декодирует JWT токен из заголовка Authorization.
    
    Args:
        credentials: Bearer токен из заголовка Authorization
        
    Returns:
        dict: Декодированный payload JWT токена
        
    Raises:
        AuthException: При некорректном или недействительном токене
    """
    try:
        token = credentials.credentials
        payload = auth_utils.decode_jwt(token=token)
    except InvalidTokenError:
        raise AuthException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid token",
        )
    return payload


async def get_current_auth_user(
    payload: dict = Depends(get_current_token_payload),
    db: AsyncSession = Depends(get_db),
) -> UserSchema:
    """Возвращает текущего пользователя, указанного в payload.sub.

    Если пользователь не найден или `sub` отсутствует — 401.
    """
    user_id: str | None = payload.get("sub")
    if not user_id:
        raise AuthException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Unauthorized",
        )

    # Ищем пользователя по ID
    result = await db.execute(select(Users).where(Users.id == user_id))
    user: Users | None = result.scalars().first()
    if user is None:
        raise AuthException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="User not found",
        )

    return UserSchema(
        id=user.id,
        username=user.username,
        password=user.password,
        email=user.email,
        active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
        deleted_at=user.deleted_at,
    )


async def get_current_active_user(
    user: UserSchema = Depends(get_current_auth_user),
) -> UserSchema:
    """Гарантирует, что текущий пользователь активен.

    Иначе возвращает 403.
    """
    if user.active:
        return user
    raise ForbiddenException(
        status_code=status.HTTP_403_FORBIDDEN,
        message="You are not authorized to view this resource",
    )
