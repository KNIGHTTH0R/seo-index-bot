import logging
from typing import TYPE_CHECKING

from aiogram_dialog import DialogManager

from infrastructure.database.models import User
from infrastructure.database.repo.base import Repo
from tg_bot.misc.constants import COINS_TO_USD_RATE, PACKAGES

if TYPE_CHECKING:
    from tg_bot.locales.stub import TranslatorRunner


async def profile_getter(
    repo: Repo, dialog_manager: DialogManager, i18n: "TranslatorRunner", **kwargs
):
    balance_usd = await repo.get_balance(dialog_manager.event.from_user.id)

    username = dialog_manager.event.from_user.username
    return {"profile-text": i18n.profile(username=username, balance=balance_usd)}


async def count_getter(dialog_manager: DialogManager, **kwargs):
    return {"count": dialog_manager.dialog_data.get("count_urls")}


async def get_order_id(dialog_manager: DialogManager, **kwargs):
    return {"order_id": dialog_manager.dialog_data.get("order_id")}


async def get_order_text(
    dialog_manager: DialogManager, i18n: "TranslatorRunner", **kwargs
):
    count = dialog_manager.dialog_data.get("count_urls")
    return {
        "pre-confirm-text": i18n.pre_confirm_text(
            count=count, usdt_amount=count * COINS_TO_USD_RATE
        )
    }


async def get_lang_setting(dialog_manager: DialogManager, **middleware_data):
    user_info: User = middleware_data.get("user_info")

    if user_info.language:
        return {
            f"lang_{user_info.language}": True,
            **dialog_manager.dialog_data,
        }


async def get_stats(dialog_manager: DialogManager, **middleware_data):
    repo: Repo = dialog_manager.middleware_data.get("repo")
    (
        day_stats,
        week_stats,
        two_weeks_stats,
        month_stats,
        users_count,
    ) = await repo.get_stats()

    top_referrers = await repo.get_top_referrers()
    top_earnings = await repo.get_top_referrers_earnings()

    top_referrers_text = "\n".join(
        f'{rank} | <a href="tg://user?id={tg_id}">{fullname}</a> | {referrals}' for rank, tg_id, fullname, referrals in
        top_referrers
    )

    top_earnings_text = "\n".join(
        f'{rank} | <a href="tg://user?id={tg_id}">{fullname}</a> | {earnings}' for rank, tg_id, fullname, earnings in
        top_earnings
    )

    stats_dict = {
        "day_stats": day_stats,
        "week_stats": week_stats,
        "two_weeks_stats": two_weeks_stats,
        "month_stats": month_stats,
        "users_count": users_count,
        "top_referrers": top_referrers_text,
        "top_earnings": top_earnings_text,
    }

    return stats_dict


async def get_user_balance(dialog_manager: DialogManager, **kwargs):
    repo: Repo = dialog_manager.middleware_data.get("repo")
    tg_id = dialog_manager.event.from_user.id
    balance = float(await repo.get_balance(tg_id=tg_id))
    count_urls = balance / COINS_TO_USD_RATE
    return {"balance": balance, "count_urls": count_urls, "price": COINS_TO_USD_RATE}


async def get_packages(**kwargs):
    return {
        "packages": [
            (f"{name} - {int(price)}$", name) for name, price in PACKAGES.items()
        ]
    }


async def tier_info(dialog_manager: DialogManager, **kwargs):
    repo: Repo = dialog_manager.middleware_data.get("repo")
    tg_id = dialog_manager.event.from_user.id
    balance = float(await repo.get_balance(tg_id=tg_id))
    price = dialog_manager.dialog_data.get("price")
    package = dialog_manager.dialog_data.get("package")
    return {"balance": balance, "price": price, "package": package}


async def package_info(dialog_manager: DialogManager, **kwargs):
    package = dialog_manager.dialog_data.get("package")
    logging.info(f"package {package}")
    return {"package": package}
