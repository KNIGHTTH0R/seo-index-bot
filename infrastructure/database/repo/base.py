import asyncio
import datetime
from typing import Optional

from sqlalchemy import select, func, update, Row, and_, case, exists
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.sql.functions import coalesce

from infrastructure.database.models.order import Order
from infrastructure.database.models.transactions import Transaction
from infrastructure.database.models.users import User
from tg_bot.config_reader import load_config


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
        statement = select(func.coalesce(func.sum(Transaction.amount_points), 0)).where(
            Transaction.fk_tg_id == tg_id, Transaction.status == True
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

    async def transaction_minus(self, tg_id: int, amount_points: int) -> None:
        statement = insert(Transaction).values(
            fk_tg_id=tg_id, amount_points=amount_points, status=True, comment='expense'
        )
        await self.session.scalars(statement)
        await self.session.commit()

    async def create_tx(
            self,
            order_id: str,
            tg_id: int,
            amount_points: int,
            amount: int = None,
            currency: str = None,
            status: bool = False,
            comment: str = 'topup',
    ) -> None:
        statement = insert(Transaction).values(
            order_id=order_id,
            fk_tg_id=tg_id,
            amount_points=amount_points,
            amount=amount,
            currency=currency,
            status=status,
            comment=comment,
        )
        await self.session.execute(statement)
        await self.session.commit()

    async def get_tx(self, order_id: str) -> Transaction:
        statement = select(Transaction).where(Transaction.order_id == order_id)
        result = await self.session.scalars(statement)
        return result.first()

    async def update_tx_paid(self, order_id: str) -> None:
        statement = (
            update(Transaction)
            .values(status=True)
            .where(Transaction.order_id == order_id)
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

    async def get_stats(self):
        now = datetime.datetime.now()
        one_day_ago = now - datetime.timedelta(days=1)
        one_week_ago = now - datetime.timedelta(weeks=1)
        two_weeks_ago = now - datetime.timedelta(weeks=2)
        one_month_ago = now - datetime.timedelta(weeks=4)

        transaction_statement = select(
            coalesce(func.sum(case((Transaction.created_at > one_day_ago, Transaction.amount), else_=0)), 0).label(
                'day'),
            coalesce(func.sum(case((Transaction.created_at > one_week_ago, Transaction.amount), else_=0)), 0).label(
                'week'),
            coalesce(func.sum(case((Transaction.created_at > two_weeks_ago, Transaction.amount), else_=0)), 0).label(
                'two_weeks'),
            coalesce(func.sum(case((Transaction.created_at > one_month_ago, Transaction.amount), else_=0)), 0).label(
                'month')
        ).where(Transaction.comment == "topup")

        user_count_statement = select(coalesce(func.count(User.tg_id), 0))

        transaction_result = await self.session.execute(transaction_statement)
        users_count_result = await self.session.execute(user_count_statement)

        day_stats, week_stats, two_weeks_stats, month_stats = transaction_result.fetchone()
        users_count = users_count_result.scalar_one()
        return day_stats, week_stats, two_weeks_stats, month_stats, users_count

    async def find_user(self, username: str) -> Optional[int]:
        statement = select(User.tg_id).where(User.username == username)
        result = await self.session.execute(statement)
        return result.scalar()

    async def find_user_by_id(self, tg_id: int) -> bool:
        statement = select(exists().where(User.tg_id == tg_id))
        result = await self.session.execute(statement)
        return result.scalar()
