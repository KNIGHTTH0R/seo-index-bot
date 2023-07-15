from aiogram_dialog import Dialog
from .windows import main_user_menu_window, order_links


def bot_menu_dialogs():
    return [
        Dialog(
            *main_user_menu_window()
        ),
        Dialog(
            *order_links()
        )
    ]



