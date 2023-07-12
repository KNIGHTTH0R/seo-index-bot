from typing import Optional

from sqlalchemy.types import DECIMAL
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.models import User
from infrastructure.database.models.base import Base
from infrastructure.database.models.timestampmixin import TimestampMixin


class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"
    transaction_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fk_tg_id: Mapped[int] = mapped_column(ForeignKey(User.tg_id))
    amount: Mapped[Optional[float]] = mapped_column(DECIMAL(16, 4), nullable=True)
    amount_points: Mapped[int]
    currency: Mapped[str] = mapped_column(String(50))

