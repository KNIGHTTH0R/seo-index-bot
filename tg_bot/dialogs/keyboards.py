from aiogram_dialog.widgets.kbd import Group, Button
from aiogram_dialog.widgets.text import Const
from .selected import to_profile, go_to_order, on_submit_order, on_click_back_delete


async def group_main_menu():
    return Group(
        Button(Const("Мій профіль"), id="profile", on_click=to_profile),
        Button(Const("Замовлення"), id="order", on_click=go_to_order),
        Button(Const("Поповнення балансу"), id="deposit"),
        Button(Const("Налаштування"), id="settings"),
    )


async def order_pend():
    return Button(
        Const("Оформити замовлення"),
        id="pending",
        on_click=on_submit_order
    )


async def back_delete_order():
    return Button(
        Const("Назад"),
        id="delete",
        on_click=on_click_back_delete
    )
