import datetime
from typing import Optional, Any, Sequence

from pydantic.types import Decimal
from sqlalchemy import select, func, update, Row, case, exists, and_, over, alias
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import coalesce

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

    async def get_balance(self, tg_id: int) -> int | Row[Any]:
        statement = select(func.coalesce(func.sum(Transaction.usd_amount), 0)).where(
            Transaction.fk_tg_id == tg_id, Transaction.status == True
        )
        result = (await self.session.execute(statement)).scalar()
        return result or 0

    async def get_user_language(self, tg_id: int) -> str:
        statement = select(User.language).where(User.tg_id == tg_id)
        result = await self.session.execute(statement)
        return result.scalar()

    async def add_order(
        self, fk_tg_id: int, urls: str, count_urls: Optional[int], status: str
    ) -> int:
        statement = (
            insert(Order)
            .values(fk_tg_id=fk_tg_id, urls=urls, count_urls=count_urls, status=status)
            .returning(Order.order_id)
        )
        result = await self.session.scalar(statement)
        await self.session.commit()
        return result

    async def get_user_id_order(self, order_id: int) -> Row[tuple[int, int]]:
        statement = select(Order.fk_tg_id, Order.count_urls).where(
            Order.order_id == order_id
        )
        result = await self.session.execute(statement)
        return result.fetchone()

    async def transaction_minus(
        self, tg_id: int, usd_amount: float, order_id: str = None
    ) -> None:
        statement = insert(Transaction).values(
            fk_tg_id=tg_id, usd_amount=usd_amount, status=True, comment="expense"
        )
        if order_id:
            statement = statement.values(order_id=order_id)
        await self.session.scalars(statement)
        await self.session.commit()

    async def create_tx(
        self,
        order_id: str,
        tg_id: int,
        usd_amount: Decimal,
        amount: Decimal = None,
        currency: str = None,
        status: bool = False,
        comment: str = "topup",
    ) -> None:
        statement = insert(Transaction).values(
            order_id=order_id,
            fk_tg_id=tg_id,
            usd_amount=usd_amount,
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

    async def check_order_status(self, order_id: int) -> bool:
        statement = select(Order.status).where(Order.order_id == order_id)
        result = await self.session.execute(statement)
        order_status = result.scalar_one()
        return order_status

    async def get_stats(self):
        now = datetime.datetime.now()
        one_day_ago = now - datetime.timedelta(days=1)
        one_week_ago = now - datetime.timedelta(weeks=1)
        two_weeks_ago = now - datetime.timedelta(weeks=2)
        one_month_ago = now - datetime.timedelta(weeks=4)

        transaction_statement = select(
            coalesce(
                func.sum(
                    case(
                        (Transaction.created_at > one_day_ago, Transaction.usd_amount),
                        else_=0,
                    )
                ),
                0,
            ).label("day"),
            coalesce(
                func.sum(
                    case(
                        (Transaction.created_at > one_week_ago, Transaction.usd_amount),
                        else_=0,
                    )
                ),
                0,
            ).label("week"),
            coalesce(
                func.sum(
                    case(
                        (
                            Transaction.created_at > two_weeks_ago,
                            Transaction.usd_amount,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label("two_weeks"),
            coalesce(
                func.sum(
                    case(
                        (
                            Transaction.created_at > one_month_ago,
                            Transaction.usd_amount,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label("month"),
        ).where(Transaction.comment == "topup", Transaction.status == True)

        user_count_statement = select(coalesce(func.count(User.tg_id), 0))

        transaction_result = await self.session.execute(transaction_statement)
        users_count_result = await self.session.execute(user_count_statement)

        (
            day_stats,
            week_stats,
            two_weeks_stats,
            month_stats,
        ) = transaction_result.fetchone()
        users_count = users_count_result.scalar_one()
        return day_stats, week_stats, two_weeks_stats, month_stats, users_count

    async def find_user(self, username: str) -> Optional[int]:
        statement = select(User.tg_id).where(User.username.ilike(username))
        result = await self.session.execute(statement)
        return result.scalar()

    async def get_user(self, tg_id: int) -> Optional[Row[Any]]:
        statement = select(User).where(User.tg_id == tg_id)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def find_user_by_id(self, tg_id: int) -> bool:
        statement = select(exists().where(User.tg_id == tg_id))
        result = await self.session.execute(statement)
        return result.scalar()

    async def get_referrals_count(self, tg_id: int) -> int:
        statement = select(func.count(User.tg_id)).where(User.referrer_id == tg_id)
        result = await self.session.execute(statement)
        return result.scalar() or 0

    async def get_referral(self, tg_id: int):
        statement = select(User.referrer_id).where(User.tg_id == tg_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_all_users(self):
        statement = select(User.tg_id)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_total_referral_amount(self, tg_id: int) -> int | Row[Any]:
        statement = select(func.coalesce(func.sum(Transaction.usd_amount), 0)).where(
            and_(Transaction.fk_tg_id == tg_id, Transaction.order_id == "referral")
        )
        result = await self.session.execute(statement)
        return result.scalar() or 0

    async def set_referrer_id(self, tg_id: int, referrer_id: int) -> None:
        statement = (
            update(User).values(referrer_id=referrer_id).where(User.tg_id == tg_id)
        )
        await self.session.execute(statement)
        await self.session.commit()
        return

    async def get_top_referrers(self) -> Sequence[Row[tuple[Any, Any, Any, Any]]]:
        user_alias = alias(User)
        statement = (
            select(
                User.tg_id, User.full_name, func.count(User.tg_id).label("referrals")
            )
            .select_from(User)
            .join(user_alias, User.tg_id == user_alias.c.referrer_id, isouter=True)
            .group_by(User.tg_id, User.full_name)
            .order_by(func.count(User.tg_id).desc())
            .limit(10)
        )
        result = await self.session.execute(statement)
        return result.all()

    async def get_top_referrers_earnings(self):
        statement = (
            select(
                over(
                    func.row_number(), order_by=func.sum(Transaction.usd_amount).desc()
                ).label("rank"),
                User.tg_id,
                User.full_name,
                func.sum(Transaction.usd_amount).label("earnings"),
            )
            .select_from(User)
            .join(Transaction, User.tg_id == Transaction.fk_tg_id)
            .filter(Transaction.comment == "referral")
            .group_by(User.tg_id)
            .order_by(func.sum(Transaction.usd_amount).desc())
            .limit(10)
        )

        result = await self.session.execute(statement)
        return result.all()
