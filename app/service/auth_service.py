from fastapi import Depends, Form, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.jwtauth import utils as auth_utils
from app.models.user_models import User
from app.schemas.userschema import UserSchema


http_bearer = HTTPBearer()


async def _get_user_by_username(db: AsyncSession, username: str) -> User | None:
    """Возвращает пользователя по имени или None, если не найден.

    Не изменяет состояние БД. Используется для устранения дублирования кода.
    """
    result = await db.execute(select(User).where(User.username == username))
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
    unauthorized_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user: User | None = await _get_user_by_username(db, username)
    if user is None:
        raise unauthorized_exc

    if not auth_utils.validate_password(password, user.password):
        raise unauthorized_exc

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return UserSchema(
        username=user.username,
        password=user.password,
        email=user.email,
        active=user.is_active,
    )


def get_current_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> dict:
    """Достает и декодирует JWT из заголовка Authorization.

    При некорректном токене возвращает 401, не раскрывая деталей.
    """
    try:
        token = credentials.credentials
        payload = auth_utils.decode_jwt(token=token)
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return payload


async def get_current_auth_user(
    payload: dict = Depends(get_current_token_payload),
    db: AsyncSession = Depends(get_db),
) -> UserSchema:
    """Возвращает текущего пользователя, указанного в payload.sub.

    Если пользователь не найден или `sub` отсутствует — 401.
    """
    username: str | None = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user: User | None = await _get_user_by_username(db, username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return UserSchema(
        username=user.username,
        password=user.password,
        email=user.email,
        active=user.is_active,
    )


async def get_current_active_user(
    user: UserSchema = Depends(get_current_auth_user),
) -> UserSchema:
    """Гарантирует, что текущий пользователь активен.

    Иначе возвращает 403.
    """
    if user.active:
        return user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

