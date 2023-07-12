from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Back
from aiogram_dialog.widgets.text import Const, Format
from .keyboards import group_main_menu
from .states import BotMenu
from .getters import profile_getter


async def main_user_menu_window():
    return Window(
        Const("Головне меню"),
        await group_main_menu(),
        state=BotMenu.user_menu
    )


async def profile_menu():
    return Window(
        Const("Ваш профіль:"),
        Format("Username: {username}\nБаланс: {balance}"),
        Back(),
        getter=profile_getter,
        state=BotMenu.profile
    )
