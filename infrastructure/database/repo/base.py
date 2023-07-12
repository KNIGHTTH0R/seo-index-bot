import asyncio
from typing import Optional

from sqlalchemy import select, distinct, create_engine, exists, Select, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.sql.elements import and_

from infrastructure.database.models.transactions import Transaction
from infrastructure.database.models.users import User
from tg_bot.config_reader import load_config


class Repo:
    def __init__(self, session):
        self.session: AsyncSession = session

    async def check_user(self, tg_id: int, username: Optional[str], full_name: str):
        statement = insert(User).values(
            tg_id=tg_id, username=username, full_name=full_name
        ).returning(
            User
        ).on_conflict_do_update(
            index_elements=[User.tg_id],
            set_=dict(
                username=username,
                full_name=full_name
            )
        )

        result = await self.session.scalars(statement)
        await self.session.commit()
        return result.first()

    async def get_balance(self, tg_id):
        statement = select(func.sum(Transaction.amount_points))
        result = await self.session.execute(statement)
        return result.scalar()


async def async_main():
    config = load_config(".env")
    engine = create_async_engine(config.db.construct_sqlalchemy_url(), echo=True)
    async_session = async_sessionmaker(engine)

    async with async_session() as session:
        repo = Repo(session)




asyncio.run(async_main())
