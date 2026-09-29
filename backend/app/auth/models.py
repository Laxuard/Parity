from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid6 import uuid7

from app.database import Base

if TYPE_CHECKING:
    from app.accounts.models import Account


class User(Base):
    __tablename__ = "users"

    # Python-side UUIDv7 generation
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))

    is_active: Mapped[bool] = mapped_column(default=True)

    # Timestamps (timezone-aware UTC), very basic auditing
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    accounts: Mapped[list[Account]] = relationship(back_populates="user")
