from aiogram import Dispatcher
from sqlalchemy.ext.asyncio import async_sessionmaker

from .repo import RepoMiddleware


def setup_middlewares(dp: Dispatcher, session_maker: async_sessionmaker):
    dp.update.middleware(RepoMiddleware(session_maker))
