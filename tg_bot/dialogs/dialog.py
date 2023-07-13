from aiogram_dialog import Dialog
from .windows import main_user_menu_window, order_links


async def bot_menu_dialogs():
    return [
        Dialog(
            *await main_user_menu_window()
        ),
        Dialog(
            *await order_links()
        )
    ]



