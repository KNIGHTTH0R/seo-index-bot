from typing import Optional

from sqlalchemy import String, Integer, BIGINT, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.models.base import Base
from infrastructure.database.models.timestampmixin import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"
    tg_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=False)
    username: Mapped[Optional[str]] = mapped_column(String(50))
    full_name: Mapped[str] = mapped_column(String(50))
    language: Mapped[str] = mapped_column(String(5), default="ua")
    referrer_id: Mapped[Optional[int]] = mapped_column(BIGINT, ForeignKey("users.tg_id"))
