import asyncio
import logging

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram_dialog import setup_dialogs
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from infrastructure.nowpayments.api import NowPaymentsAPI
from infrastructure.wayforpay.api import WayForPayAPI
from tg_bot.config_reader import load_config
from tg_bot.dialogs.dialog import bot_menu_dialogs
from tg_bot.handlers.user import user_router
from tg_bot.middlewares.repo import RepoMiddleware, CheckUser
from tg_bot.middlewares.translator import TranslationMiddleware

logger = logging.getLogger(__name__)
log_level = logging.INFO
bl.basic_colorized_config(level=log_level)


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

    bot = Bot(token=config.tg_bot.token, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=storage)
    wayforpay = WayForPayAPI(
        config.wayforpay.merchant_account,
        config.wayforpay.merchant_secret_key,
        config.wayforpay.merchant_domain,
        config.wayforpay.webhook_url,
    )
    nowpayments = NowPaymentsAPI(config.nowpayments.api_key)

    for global_middleware in (
        RepoMiddleware(session_maker=session_maker),
        CheckUser(),
        TranslationMiddleware(),
    ):
        dp.message.outer_middleware(global_middleware)
        dp.callback_query.outer_middleware(global_middleware)

    dp.workflow_data.update(
        wayforpay=wayforpay,
        nowpayments=nowpayments,
    )

    dp.include_routers(user_router, *bot_menu_dialogs())  # main_window - aiogram dialog
    setup_dialogs(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(
        bot, allowed_updates=dp.resolve_used_update_types(), config=config
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Бот був вимкнений!")
