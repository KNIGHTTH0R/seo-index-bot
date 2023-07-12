from aiogram_dialog import DialogManager

from infrastructure.database.repo.base import Repo


async def profile_getter(repo: Repo, dialog_manager: DialogManager, **kwargs):
    return \
        {
        "balance": await repo.get_balance(dialog_manager.dialog_data.get("user_id")),
        "username": dialog_manager.dialog_data.get("username")
        }
