from pydantic import field_validator
from annotated_types import MinLen, MaxLen
from datetime import datetime
from typing import Optional, Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

Username = Annotated[str, Field(min_length=3, max_length=20)]


class UserSchema(BaseModel):
    """
    Схема пользователя для внутреннего использования в сервисах.
    Содержит все поля включая пароль для валидации.
    """
    model_config = ConfigDict(strict=True)
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    username: Annotated[str, MinLen(3), MaxLen(20)]
    password: bytes
    email: Optional[EmailStr] = None
    active: bool = True

    @field_validator("email", mode="before")
    def empty_to_none(cls, v):
        return None if v == "" else v


# --------- Схемы запросов (входные) ---------


class UserCreate(BaseModel):
    """
    Для создания пользователя. Принимаем пароль как строку (до хеширования).
    ID генерируется автоматически при создании пользователя.
    """

    model_config = ConfigDict()
    username: Username
    password: str
    email: Optional[EmailStr] = None


class UserUpdate(BaseModel):
    """
    Частичное обновление. Все поля опциональны.
    """

    model_config = ConfigDict(strict=True)

    username: Optional[Username] = None
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


# --------- Схемы ответов (выходные) ---------


class UserRead(BaseModel):
    """
    Схема для возврата данных пользователя клиенту (без пароля).
    Совместимо с ORM (SQLAlchemy) благодаря from_attributes=True.
    """

    model_config = ConfigDict(strict=True, from_attributes=True)

    id: UUID
    username: str
    email: Optional[EmailStr] = None
    is_active: bool = True

    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


# --------- Внутренняя схема (для сервисного слоя) ---------


class UserInDB(BaseModel):
    """
    Внутренняя схема, если нужно оперировать хешём пароля.
    Поле password (bytes) исключено из сериализации.
    """

    model_config = ConfigDict(strict=True, from_attributes=True)

    id: UUID
    username: str
    password: bytes = Field(exclude=True)  # bcrypt-хэш
    email: Optional[EmailStr] = None
    is_active: bool = True

    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class TokenInfo(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None


class AuthUser(BaseModel):
    """Внутренняя схема для контекста авторизации (без пароля)."""

    model_config = ConfigDict(strict=True)

    username: str
    email: Optional[EmailStr] = None
    active: bool = True
