from app.db.base_class import BaseModel
from sqlalchemy import String, Boolean, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column


class User(BaseModel):
    """Модель пользователя системы.

    Содержит учетные данные и профильные атрибуты. Пароль хранится в виде
    bcrypt-хэша (bytes). Поле `is_active` определяет доступ к системе.
    """
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    password: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)