from aiogram_dialog import Dialog

from .windows import main_user_menu_window, order_links, language_menu_window, deposit, \
    admin_menu, tier_menu


def bot_menu_dialogs():
    return [
        Dialog(*main_user_menu_window()),
        Dialog(*order_links()),
        Dialog(language_menu_window()),
        Dialog(*deposit()),
        Dialog(*admin_menu()),
        Dialog(*tier_menu())
    ]
