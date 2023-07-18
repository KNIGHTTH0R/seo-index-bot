from typing import TYPE_CHECKING, Union

from aiogram.utils import i18n
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Cancel
from aiogram_dialog.widgets.text import Format

from . import selected
from .getters import profile_getter, get_order_text, get_lang_setting
from .keyboards import group_main_menu, order_pend, choose_type_payment
from .selected import get_links, get_suma_to_deposit
from .states import BotMenu, Order, LanguageMenu, Payment
from ..utils.widgets import (
    Translation,
    TranslatableFormat,
    dropdown_on_off_menu,
    Option,
)

if TYPE_CHECKING:
    from tg_bot.locales.stub import TranslatorRunner

i18n: Union["TranslatorRunner", Translation] = Translation()


def main_user_menu_window():
    return [
        Window(
            TranslatableFormat(i18n.main_menu_name()),
            group_main_menu(i18n),
            state=BotMenu.user_menu,
        ),
        Window(
            Format("{profile-text}"),
            Back(TranslatableFormat(i18n.back_button())),
            getter=profile_getter,
            state=BotMenu.profile,
        ),
        Window(
            TranslatableFormat(i18n.button_deposit()),
            choose_type_payment(i18n),
            Back(TranslatableFormat(i18n.back_button())),
            state=BotMenu.deposit_balance,
        )
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
            order_pend(i18n),
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
                    id="set_lang_en",
                    text=i18n.dialogs.buttons.english(),
                    when_key="lang_en",
                ),
                Option(
                    id="set_lang_uk",
                    text=i18n.dialogs.buttons.ukrainian(),
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
        ),
        # TODO Make this work in the correct dialog
        # Start(
        #     TranslatableFormat(i18n.dialogs.buttons.back_to_main_menu()),
        #     id="back_to_main_menu",
        #     state=MainMenu.menu,
        #     mode=StartMode.RESET_STACK,
        # ),
        Cancel(TranslatableFormat(i18n.back_button())),
        state=LanguageMenu.menu,
        getter=get_lang_setting,
    )


def deposit():
    return Window(
        TranslatableFormat(i18n.suma_to_deposit()),
        Cancel(TranslatableFormat(i18n.back_button())),
        MessageInput(func=get_suma_to_deposit),
        state=Payment.suma_of_payment
    )
