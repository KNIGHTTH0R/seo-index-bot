from sqlalchemy import Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.models.base import Base
from infrastructure.database.models.timestampmixin import TimestampMixin


class Order(Base, TimestampMixin):
    __tablename__ = "orders"
    order_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fk_tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"))
    urls: Mapped[str] = mapped_column(Text)
    count_urls: Mapped[int]
    status: Mapped[str]
