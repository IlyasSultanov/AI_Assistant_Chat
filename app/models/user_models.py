from typing import Optional
from uuid import UUID, uuid4

from app.db.base_class import BaseModel
from sqlalchemy import String, Boolean, Column, LargeBinary
from sqlmodel import Field



class Users(BaseModel, table=True):
    """Модель пользователя системы.

    Содержит учетные данные и профильные атрибуты. Пароль хранится в виде
    bcrypt-хэша (bytes). Поле `is_active` определяет доступ к системе.
    """

    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
    )
    username: str = Field(
        sa_column=Column(String(50), unique=True, index=True, nullable=False)
    )
    email: str = Field(
        sa_column=Column(String(255), unique=True, index=True, nullable=False)
    )
    password: bytes = Field(sa_column=Column(LargeBinary, nullable=False))
    is_active: bool = Field(default=True, sa_column=Column(Boolean, nullable=False))
