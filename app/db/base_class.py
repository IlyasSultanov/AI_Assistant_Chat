from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import ConfigDict
from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)

    __abstract__ = True

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        ),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
    )

    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={getattr(self, 'id', None)})>"

    def to_dict(self) -> dict[str, Any]:
        if hasattr(self, "__table__"):
            return {
                column.name: getattr(self, column.name)
                for column in self.__table__.columns
            }
        return self.model_dump()

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def mark_as_deleted(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)
