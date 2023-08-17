from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from typing_extensions import TYPE_CHECKING

if TYPE_CHECKING:
    from tg_bot.locales.stub import TranslatorRunner


def main_user_menu(i18n: "TranslatorRunner") -> ReplyKeyboardMarkup:
    profile_button = KeyboardButton(text=i18n.button_profile())
    orders_button = KeyboardButton(text=i18n.button_order())
    refill_balance_button = KeyboardButton(text=i18n.button_deposit())
    settings_button = KeyboardButton(text=i18n.button_settings())

    return ReplyKeyboardMarkup(
        keyboard=[
            [profile_button, orders_button],
            [refill_balance_button, settings_button],
        ],
        resize_keyboard=True,
    )
