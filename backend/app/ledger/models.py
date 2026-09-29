from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid6 import uuid7

from app.database import Base

if TYPE_CHECKING:
    from app.accounts.models import Account


class TransactionStatus(StrEnum):
    PENDING = "pending"
    POSTED = "posted"
    FAILED = "failed"


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)

    # Idempotency / external tracking reference
    reference_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(255))

    status: Mapped[TransactionStatus] = mapped_column(
        SQLEnum(TransactionStatus, native_enum=False, length=20),
        default=TransactionStatus.POSTED,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    entries: Mapped[list[LedgerEntry]] = relationship(
        back_populates="transaction", cascade="all, delete-orphan"
    )


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)

    # Financial records should never be deleted via CASCADE:
    transaction_id: Mapped[UUID] = mapped_column(
        ForeignKey("transactions.id", ondelete="RESTRICT"),
        index=True,
    )
    account_id: Mapped[UUID] = mapped_column(
        ForeignKey("accounts.id", ondelete="RESTRICT"),
        index=True,
    )

    # Stored in minor units (e.g., cents: $10.00 = 1000)
    # Debits are negative, Credits are positive
    amount: Mapped[int] = mapped_column(BigInteger)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    transaction: Mapped[Transaction] = relationship(back_populates="entries")
    account: Mapped[Account] = relationship(back_populates="ledger_entries")
