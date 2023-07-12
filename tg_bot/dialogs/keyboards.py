from aiogram_dialog.widgets.kbd import Group, Button
from aiogram_dialog.widgets.text import Const
from .selected import to_profile


async def group_main_menu():
    return Group(
        Button(Const("Мій профіль"), id="profile", on_click=to_profile),
        Button(Const("Замовлення"), id="order"),
        Button(Const("Поповнення балансу"), id="deposit"),
        Button(Const("Налаштування"), id="settings"),
    )
