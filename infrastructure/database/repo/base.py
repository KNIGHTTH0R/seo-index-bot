import asyncio

from sqlalchemy import select, distinct, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.sql.elements import and_

from tg_bot.config_reader import load_config
from infrastructure.database.models.products import Products


class Repo:
    def __init__(self, session):
        self.session: AsyncSession = session

    def __repr__(self) -> str:
        params = ", ".join(
            (
                f"{attr}={self.__dict__[attr]}"
                for attr in self.__dict__
                if not attr.startswith("_")
            )
        )
        return f"{self.__class__.__name__}({params})"


async def async_main():
    config = load_config(".env")
    engine = create_async_engine(config.db.construct_sqlalchemy_url(), echo=True)
    async_session = async_sessionmaker(engine)

    async with async_session() as session:
        repo = Repo(session)


asyncio.run(async_main())
