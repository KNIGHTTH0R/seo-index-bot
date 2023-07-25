from typing import Optional

from sqlalchemy import String, Integer, ForeignKey, BIGINT, Boolean, false
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DECIMAL

from infrastructure.database.models.base import Base
from infrastructure.database.models.timestampmixin import TimestampMixin


class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"
    transaction_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fk_tg_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.tg_id"))
    order_id: Mapped[Optional[str]] = mapped_column(String(128))
    amount: Mapped[Optional[float]] = mapped_column(DECIMAL(16, 4), nullable=True)
    amount_points: Mapped[int]
    currency: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    status: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=false())
