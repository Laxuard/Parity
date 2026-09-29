from datetime import datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7

from app.database import Base


class AccountType(StrEnum):
    CHECKING = "checking"
    SAVINGS = "savings"
    SYSTEM = "system"  # Platform reserves, fees, clearing, loan funds


class AccountStatus(StrEnum):
    ACTIVE = "active"
    FROZEN = "frozen"
    CLOSED = "closed"


class Account(Base):
    __tablename__ = "accounts"

    # Primary Key
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)

    # Account Routing Number
    account_number: Mapped[str] = mapped_column(String(32), unique=True, index=True)

    # User FK (Nullable for system/reserve accounts)
    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
    )

    # ISO 4217 Currency (USD, EUR, GBP)
    currency: Mapped[str] = mapped_column(String(3), default="USD")

    # Enums stored as VARCHAR with check constraints to avoid PG ENUM migration friction
    account_type: Mapped[AccountType] = mapped_column(
        SQLEnum(AccountType, native_enum=False, length=20),
        default=AccountType.CHECKING,
    )
    status: Mapped[AccountStatus] = mapped_column(
        SQLEnum(AccountStatus, native_enum=False, length=20),
        default=AccountStatus.ACTIVE,
    )

    # Audit Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Optional 2-way relationship if User defines: accounts = relationship(...)
    # user: Mapped["User | None"] = relationship(back_populates="accounts")
