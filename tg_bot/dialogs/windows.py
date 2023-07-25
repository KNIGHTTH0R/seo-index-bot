from typing import TYPE_CHECKING

from aiogram.utils import i18n
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Cancel, Group, Button, SwitchTo
from aiogram_dialog.widgets.text import Format, Const

from . import selected
from .getters import profile_getter, get_order_text, get_lang_setting
from .selected import (
    get_links,
    pay_wayforpay,
    to_profile,
    go_to_order,
    go_to_deposit_balance,
    go_to_settings,
    on_submit_order,
    get_deposit_amount,
)
from .states import BotMenu, Order, LanguageMenu, Payment
from ..utils.widgets import (
    Translation,
    TranslatableFormat,
    dropdown_on_off_menu,
    Option,
)

if TYPE_CHECKING:
    from tg_bot.locales.stub import TranslatorRunner

i18n: "TranslatorRunner" = Translation()


def main_user_menu_window():
    return [
        Window(
            TranslatableFormat(i18n.main_menu_name()),
            Group(
                Button(
                    TranslatableFormat(i18n.button_profile()),
                    id="profile",
                    on_click=to_profile,
                ),
                Button(
                    TranslatableFormat(i18n.button_order()),
                    id="order",
                    on_click=go_to_order,
                ),
                Button(
                    TranslatableFormat(i18n.button_deposit()),
                    id="deposit",
                    on_click=go_to_deposit_balance,
                ),
                Button(
                    TranslatableFormat(i18n.button_settings()),
                    id="settings",
                    on_click=go_to_settings,
                ),
            ),
            state=BotMenu.user_menu,
        ),
        Window(
            Format("{profile-text}"),
            Back(TranslatableFormat(i18n.back_button())),
            getter=profile_getter,
            state=BotMenu.profile,
        ),
    ]


def order_links():
    return [
        Window(
            TranslatableFormat(i18n.order()),
            Cancel(TranslatableFormat(i18n.back_button())),
            MessageInput(func=get_links),
            disable_web_page_preview=True,
            state=Order.get_url,
        ),
        Window(
            TranslatableFormat(i18n.confirm_order()),
            Format("{pre-confirm-text}"),
            Button(
                TranslatableFormat(i18n.confirm_button()),
                id="pending",
                on_click=on_submit_order,
            ),
            Back(TranslatableFormat(i18n.back_button())),
            getter=get_order_text,
            state=Order.confirm_url,
        ),
    ]


def language_menu_window():
    return Window(
        *dropdown_on_off_menu(
            dropdown_title=i18n.dialogs.buttons.change_language(),
            selection_key="change_language",
            options=[
                Option(
                    id="set_lang_uk",
                    text=i18n.dialogs.buttons.ukranian(),
                    when_key="lang_uk",
                ),
                Option(
                    id="set_lang_ru",
                    text=i18n.dialogs.buttons.russian(),
                    when_key="lang_ru",
                ),
            ],
            on_click=selected.set_language(switch_to=LanguageMenu.menu),
            on_open_close=selected.open_close_menu(switch_to=LanguageMenu.menu),
            always_open=True
        ),
        Cancel(TranslatableFormat(i18n.back_button())),
        state=LanguageMenu.menu,
        getter=get_lang_setting,
    )


def deposit():
    return [
        Window(
            TranslatableFormat(i18n.enter_deposit_amount()),
            Cancel(TranslatableFormat(i18n.back_button())),
            MessageInput(func=get_deposit_amount),
            state=Payment.deposit_amount,
        ),
        Window(
            TranslatableFormat(i18n.choose_payment_method()),
            Group(
                Button(
                    TranslatableFormat(i18n.wayforpay()),
                    id="wayforpay",
                    on_click=pay_wayforpay,
                ),
                SwitchTo(
                    TranslatableFormat(i18n.nowpayments()),
                    id="nowpayments",
                    state=Payment.choose_crypto_currency,
                ),
            ),
            Back(TranslatableFormat(i18n.back_button())),
            state=Payment.available_method,
        ),
        Window(
            TranslatableFormat(i18n.choose_crypto_currency()),
            # Make choose currency
            Group(
                *[
                    Button(
                        Const(currency.upper()),
                        id=f"pay_{currency}",
                        on_click=selected.pay_nowpayments,
                    )
                    for currency in ["btc", "eth", "ltc", "usdttrc20"]
                ]
            ),
            Back(TranslatableFormat(i18n.back_button())),
            state=Payment.choose_crypto_currency,
        ),
    ]
