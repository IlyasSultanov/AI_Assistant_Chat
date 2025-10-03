from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from app.db.database import get_db
from app.jwtauth import utils as auth_utils
from app.schemas.userschema import UserSchema, TokenInfo, UserCreate, UserRead
from app.service.auth_service import (
    validate_auth_user,
    get_current_active_user,
    create_user,
)
from app.core.config import settings
from app.exceptions.base_ex import BadRequestException

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Регистрация нового пользователя.
    
    Args:
        user: Данные для создания пользователя (username, password, email).
              ID генерируется автоматически.
        db: Сессия базы данных
        
    Returns:
        UserRead: Данные созданного пользователя (без пароля)
        
    Raises:
        BadRequestException: Если пользователь с таким username или email уже существует
    """
    res = await create_user(db, user)
    if res.get("status") == "error":
        raise BadRequestException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=res.get("detail", "User creation failed"),
        )
    return res["user"]


@router.post("/login", response_model=TokenInfo)
async def login(user: "UserSchema" = Depends(validate_auth_user)):
    """
    Аутентификация пользователя и получение JWT токенов.
    
    Args:
        user: Валидированный пользователь (через validate_auth_user)
        
    Returns:
        TokenInfo: Access и refresh токены для авторизации
        
    Raises:
        HTTPException: При неверных учетных данных или неактивном пользователе
    """
    jwt_payload = {
        "sub": str(user.id),
        "name": user.username,
        "email": user.email,
    }

    access_token = auth_utils.encode_jwt(
        jwt_payload, expires_in=settings.auth_settings.access_token_expires_minutes
    )
    refresh_token = auth_utils.encode_jwt(
        {"sub": str(user.id)},
        expires_in=settings.auth_settings.refresh_token_expires_minutes,
    )

    return TokenInfo(
        access_token=access_token, token_type="bearer", refresh_token=refresh_token
    )


@router.post("/refresh", response_model=TokenInfo)
async def refresh_token(payload: dict = Depends(lambda: {}), token: str | None = None):
    """
    Обновление access токена с помощью refresh токена.
    
    Args:
        payload: Данные из тела запроса (не используется)
        token: Refresh токен для обновления access токена
        
    Returns:
        TokenInfo: Новый access токен
        
    Note:
        В текущей реализации refresh токены не проверяются на валидность.
        В продакшене следует добавить проверку в черном списке.
    """
    if token is None:
        return TokenInfo(access_token="", token_type="bearer")

    data = auth_utils.decode_jwt(token)
    new_access = auth_utils.encode_jwt(
        {
            "sub": data.get("sub"),
            "name": data.get("name"),
            "email": data.get("email"),
        }
    )
    return TokenInfo(access_token=new_access, token_type="bearer")


@router.get("/logout/me")
async def logout_me(user: UserSchema = Depends(get_current_active_user)):
    """
    Получение информации о текущем пользователе.
    
    Args:
        user: Текущий авторизованный пользователь
        
    Returns:
        dict: Информация о пользователе (username и email)
    """
    return {"sub": user.username, "email": user.email}
