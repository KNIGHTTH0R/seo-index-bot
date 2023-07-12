from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.models.base import Base
from infrastructure.database.models.timestampmixin import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"
    tg_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String(50))
    full_name: Mapped[str] = mapped_column(String(50))
    language: Mapped[str] = mapped_column(String(5), default="ua")
