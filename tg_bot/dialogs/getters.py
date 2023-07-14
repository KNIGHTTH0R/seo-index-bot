from aiogram_dialog import DialogManager

from infrastructure.database.repo.base import Repo


async def profile_getter(repo: Repo, dialog_manager: DialogManager, **kwargs):
    return \
        {
            "balance": await repo.get_balance(dialog_manager.dialog_data.get("user_id")),
            "username": dialog_manager.dialog_data.get("username")
        }


async def count_getter(dialog_manager: DialogManager, **kwargs):
    return \
        {
            "count": dialog_manager.dialog_data.get("count")
        }


async def get_order_id(dialog_manager: DialogManager, **kwargs):
    return {"order_id": dialog_manager.dialog_data.get("order_id")}
