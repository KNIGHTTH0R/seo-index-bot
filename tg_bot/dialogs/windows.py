import operator
from typing import TYPE_CHECKING

from aiogram.enums import ContentType
from aiogram.utils import i18n
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput, TextInput
from aiogram_dialog.widgets.kbd import Back, Cancel, Group, Button, SwitchTo, Select
from aiogram_dialog.widgets.text import Format, Const

from . import selected
from .getters import (
    profile_getter,
    get_order_text,
    get_lang_setting,
    get_stats,
    get_user_balance,
    get_packages,
    tier_info,
    package_info,
)
from .selected import (
    get_links,
    pay_wayforpay,
    to_profile,
    go_to_order,
    go_to_deposit_balance,
    go_to_settings,
    on_submit_order,
    get_deposit_amount,
    on_error_func,
    get_id_menu,
    to_suma_menu,
    get_suma,
    to_back_menu_admin,
    to_stats,
    to_confirm_tier,
    decline,
    to_get_text,
    get_urls,
    go_to_tier,
)
from .states import BotMenu, Order, LanguageMenu, Payment, AdminMenu, TierMenu
from ..utils.utils import type_factory_advanced
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
                    TranslatableFormat(i18n.button_tier()),
                    id="tier",
                    on_click=go_to_tier,
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
            getter=get_user_balance,
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
                    text=Const("Українська"),
                    when_key="lang_uk",
                ),
                Option(
                    id="set_lang_ru",
                    text=Const("Русский"),
                    when_key="lang_ru",
                ),
            ],
            on_click=selected.set_language(switch_to=LanguageMenu.menu),
            on_open_close=selected.open_close_menu(switch_to=LanguageMenu.menu),
            always_open=True,
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


def admin_menu():
    return [
        Window(
            Const("Меню администратора"),
            Button(
                Const("Изменить баланс пользователю"),
                on_click=get_id_menu,
                id="change_balance",
            ),
            Button(Const("Статистика"), on_click=to_stats, id="stats_menu"),
            state=AdminMenu.menu,
        ),
        Window(
            Const("Введите id или username пользователя. Пример @sad"),
            TextInput(
                id="id_user",
                on_success=to_suma_menu,
                type_factory=type_factory_advanced,
                on_error=on_error_func,
            ),
            Back(Const("Назад")),
            state=AdminMenu.id,
        ),
        Window(
            Const("<b>Введите сумму в $: \nПример: 100 | -200 </b>"),
            TextInput(
                id="suma", on_success=get_suma, type_factory=int, on_error=on_error_func
            ),
            Back(Const("Назад")),
            state=AdminMenu.suma,
        ),
        Window(
            Format(
                "<b>Статистика:\nЗа 1 день: {day_stats}$\nЗа неделю: {week_stats}$\nЗа две недели: {two_weeks_stats}$\nЗа месяц: {month_stats}$\nВсего пользователей: {users_count}</b>"
            ),
            Button(Const("Назад"), id="back_menu", on_click=to_back_menu_admin),
            getter=get_stats,
            state=AdminMenu.stats,
        ),
    ]


def tier_menu():
    return [
        Window(
            TranslatableFormat(i18n.select_package()),
            Group(
                Select(
                    Format("{item[0]}"),
                    id="s_packages",
                    item_id_getter=operator.itemgetter(1),
                    items="packages",
                    on_click=to_confirm_tier,
                ),
                width=3,
            ),
            getter=get_packages,
            state=TierMenu.menu,
        ),
        Window(
            TranslatableFormat(i18n.buyed_packeg()),
            Button(TranslatableFormat(i18n.yes()), id="yes", on_click=to_get_text),
            Button(TranslatableFormat(i18n.no()), id="no", on_click=decline),
            state=TierMenu.confirm,
            getter=tier_info,
        ),
        Window(
            TranslatableFormat(i18n.send_info_tier()),
            MessageInput(
                func=get_urls, content_types=[ContentType.TEXT, ContentType.DOCUMENT]
            ),
            state=TierMenu.get_links,
            getter=package_info,
        ),
    ]
