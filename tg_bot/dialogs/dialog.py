from aiogram_dialog import Dialog
from .windows import main_user_menu_window, profile_menu


async def bot_menu_dialogs():
    return Dialog(
        await main_user_menu_window(),
        await profile_menu()
    )
