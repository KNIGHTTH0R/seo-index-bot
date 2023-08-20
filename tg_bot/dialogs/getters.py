from typing import TYPE_CHECKING

from aiogram_dialog import DialogManager

from infrastructure.database.models import User
from infrastructure.database.repo.base import Repo

if TYPE_CHECKING:
    from tg_bot.locales.stub import TranslatorRunner


async def profile_getter(repo: Repo, dialog_manager: DialogManager, i18n: "TranslatorRunner", **kwargs):
    balance_usd = await repo.get_balance(dialog_manager.event.from_user.id)

    username = dialog_manager.event.from_user.username
    return {
        "profile-text": i18n.profile(username=username, balance=balance_usd)
    }


async def count_getter(dialog_manager: DialogManager, **kwargs):
    return {"count": dialog_manager.dialog_data.get("count_urls")}


async def get_order_id(dialog_manager: DialogManager, **kwargs):
    return {"order_id": dialog_manager.dialog_data.get("order_id")}


async def get_order_text(
        dialog_manager: DialogManager, i18n: "TranslatorRunner", **kwargs
):
    count = dialog_manager.dialog_data.get("count_urls")
    return {"pre-confirm-text": i18n.pre_confirm_text(count=count, usdt_amount=count*0.20)}


async def get_lang_setting(dialog_manager: DialogManager, **middleware_data):
    user_info: User = middleware_data.get("user_info")

    if user_info.language:
        return {
            f"lang_{user_info.language}": True,
            **dialog_manager.dialog_data,
        }


async def get_stats(dialog_manager: DialogManager, **middleware_data):
    repo: Repo = dialog_manager.middleware_data.get("repo")
    day_stats, week_stats, two_weeks_stats, month_stats, users_count = await repo.get_stats()
    stats_dict = {
        "day_stats": day_stats,
        "week_stats": week_stats,
        "two_weeks_stats": two_weeks_stats,
        "month_stats": month_stats,
        "users_count": users_count
    }

    return stats_dict
