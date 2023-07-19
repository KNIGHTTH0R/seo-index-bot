from typing import Optional

from sqlalchemy import select, func, update, Row
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.order import Order
from infrastructure.database.models.transactions import Transaction
from infrastructure.database.models.users import User


class Repo:
    def __init__(self, session):
        self.session: AsyncSession = session

    async def check_user(
        self, tg_id: int, username: Optional[str], full_name: str
    ) -> User:
        statement = (
            insert(User)
            .values(tg_id=tg_id, username=username, full_name=full_name)
            .returning(User)
            .on_conflict_do_update(
                index_elements=[User.tg_id],
                set_=dict(username=username, full_name=full_name),
            )
        )

        result = await self.session.scalars(statement)
        await self.session.commit()
        return result.first()

    async def get_balance(self, tg_id: int) -> int:
        statement = select(func.sum(Transaction.amount_points)).where(
            Transaction.fk_tg_id == tg_id
        )
        result = await self.session.execute(statement)
        return result.scalar()

    async def add_order(self, fk_tg_id: int, urls, count_urls, status) -> int:
        statement = (
            insert(Order)
            .values(fk_tg_id=fk_tg_id, urls=urls, count_urls=count_urls, status=status)
            .returning(Order.order_id)
        )
        result = await self.session.scalar(statement)
        await self.session.commit()
        return result

    async def get_order_info(self, order_id: int) -> Row[tuple[int, str, int]]:
        statement = select(Order.fk_tg_id, Order.urls, Order.count_urls).where(
            Order.order_id == order_id
        )
        result = await self.session.execute(statement)
        return result.fetchone()

    async def get_user_id_order(self, order_id: int) -> Row[tuple[int, int]]:
        statement = select(Order.fk_tg_id, Order.count_urls).where(
            Order.order_id == order_id
        )
        result = await self.session.execute(statement)
        return result.fetchone()

    # async def transaction_minus(self, tg_id: int, amount_points: int) -> None:
    #     statement = insert(Transaction).values(
    #         fk_tg_id=tg_id, amount_points=amount_points
    #     )
    #     await self.session.scalars(statement)
    async def create_tx(
        self,
        order_id: str,
        tg_id: int,
        amount_points: int,
        amount: int = None,
        currency: str = None,
    ) -> None:
        statement = insert(Transaction).values(
            order_id=order_id,
            fk_tg_id=tg_id,
            amount_points=amount_points,
            amount=amount,
            currency=currency,
        )
        await self.session.execute(statement)
        await self.session.commit()

    async def change_language(self, tg_id: int, language: str) -> None:
        statement = update(User).values(language=language).where(User.tg_id == tg_id)
        await self.session.execute(statement)
        await self.session.commit()

    async def change_status(self, status: str, order_id: int) -> None:
        statement = (
            update(Order).values(status=status).where(Order.order_id == order_id)
        )
        await self.session.execute(statement)
        await self.session.commit()
