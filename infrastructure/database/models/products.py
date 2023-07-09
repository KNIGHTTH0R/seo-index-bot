from sqlalchemy import BigInteger, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from infrastructure.database.models.base import Base


class Products(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    category: Mapped[str] = mapped_column(String(50))  # Категория
    grade: Mapped[str] = mapped_column(String(50))  # Сорт
    genetic: Mapped[str] = mapped_column(String(50))  # Генетика
    description: Mapped[str] = mapped_column(String(100))
    price: Mapped[float]
    area: Mapped[str] = mapped_column(String(50))
    city: Mapped[str] = mapped_column(String(50))
    weight: Mapped[int]
    photo_id: Mapped[str] = mapped_column(String(100))

    def __repr__(self) -> str:
        params = ", ".join(
            (
                f"{attr}={self.__dict__[attr]}"
                for attr in self.__dict__
                if not attr.startswith("_")
            )
        )
        return f"{self.__class__.__name__}({params})"
