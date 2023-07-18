from typing import TYPE_CHECKING

from aiogram_dialog.widgets.kbd import Group, Button
from aiogram_dialog.widgets.text import Const

from .selected import to_profile, go_to_order, on_submit_order, go_to_deposit_balance
from ..utils.widgets import TranslatableFormat

if TYPE_CHECKING:
    from ..locales.stub import TranslatorRunner


def group_main_menu(i18n: "TranslatorRunner"):
    return Group(
        Button(TranslatableFormat(i18n.button_profile()), id="profile", on_click=to_profile),
        Button(TranslatableFormat(i18n.button_order()), id="order", on_click=go_to_order),
        Button(
            TranslatableFormat(i18n.button_deposit()), id="deposit", on_click=go_to_deposit_balance
        ),
        Button(TranslatableFormat(i18n.button_settings()), id="settings"),
    )


def order_pend(i18n: "TranslatorRunner"):
    # TODO add translation and use i18n
    return Button(Const("Оформити замовлення"), id="pending", on_click=on_submit_order)


def choose_type_payment(i18n: "TranslatorRunner"):
    # TODO add translation and use i18n
    return Group(
        Button(Const("Гривні"), id="wayforpay"),
        Button(Const("Криптовалюта"), id="nowpayments"),
    )
