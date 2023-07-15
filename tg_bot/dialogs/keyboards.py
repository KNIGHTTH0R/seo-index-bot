from aiogram_dialog.widgets.kbd import Group, Button
from aiogram_dialog.widgets.text import Const
from .selected import to_profile, go_to_order, on_submit_order, go_to_deposit_balance


async def group_main_menu():
    return Group(
        Button(Const("Мій профіль"), id="profile", on_click=to_profile),
        Button(Const("Замовлення"), id="order", on_click=go_to_order),
        Button(Const("Поповнення балансу"), id="deposit", on_click=go_to_deposit_balance),
        Button(Const("Налаштування"), id="settings"),
    )


async def order_pend():
    return Button(
        Const("Оформити замовлення"),
        id="pending",
        on_click=on_submit_order
    )


async def choose_type_payment():
    return Group(
        Button(Const("Гривні"), id="wayforpay"),
        Button(Const("Криптовалюта"), id="nowpayments")
    )

