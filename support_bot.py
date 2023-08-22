import asyncio
import logging

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram_dialog import setup_dialogs
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tg_bot.config_reader import load_config, Config
from support_bot.handlers.user import user_router
from tg_bot.middlewares.repo import RepoMiddleware
from tg_bot.utils.broadcaster import broadcast
from tg_bot.utils.default_commands import collect_and_assign_commands

logger = logging.getLogger(__name__)
log_level = logging.INFO
bl.basic_colorized_config(level=log_level)


async def on_startup(dispatcher, bot: Bot, config: Config):
    await collect_and_assign_commands(dispatcher.sub_routers, bot, sort=False)
    await broadcast(bot, config.tg_bot.admin_ids, "Бот запущен!")


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger.info("Starting tg_bot")
    config = load_config(".env")
    storage = RedisStorage.from_url(
        config.redis.dsn(),
        key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
    )

    engine = create_async_engine(config.db.construct_sqlalchemy_url(), echo=True)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    main_bot = Bot(token=config.tg_bot.token, parse_mode=ParseMode.HTML)
    bot_support = Bot(token=config.support_bot.token)
    dp = Dispatcher(storage=storage)
    scheduler = AsyncIOScheduler()

    for global_middleware in (
            RepoMiddleware(session_maker=session_maker),
    ):
        dp.message.outer_middleware(global_middleware)
        dp.callback_query.outer_middleware(global_middleware)

    dp.include_routers(user_router)
    setup_dialogs(dp)
    await bot_support.delete_webhook(drop_pending_updates=True)
    dp.startup.register(on_startup)
    dp.workflow_data.update(
        main_bot=main_bot,
        scheduler=scheduler
    )
    scheduler.start()
    await dp.start_polling(
        bot_support, allowed_updates=dp.resolve_used_update_types(), config=config
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Бот був вимкнений!")
