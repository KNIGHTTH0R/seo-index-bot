import asyncio
import logging

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import setup_dialogs

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from bot.middlewares import RepoMiddleware
from config_reader import load_config
from handlers.admin import admin_router
from handlers.user import user_router

logger = logging.getLogger(__name__)
log_level = logging.INFO
bl.basic_colorized_config(level=log_level)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config("../.env")
    storage = MemoryStorage()

    engine = create_async_engine(config.db.construct_sqlalchemy_url(), echo=True)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    bot = Bot(token=config.tg_bot.token, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=storage)
    dp.include_routers(admin_router, user_router) # main_window - aiogram dialog
    setup_dialogs(dp)

    dp.update.middleware(RepoMiddleware(session_maker=session_maker))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, config=config)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Бот был выключен")
