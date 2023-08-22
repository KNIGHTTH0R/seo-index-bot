from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing_extensions import TYPE_CHECKING



if TYPE_CHECKING:
    from tg_bot.locales.stub import TranslatorRunner


def send_file_button(id_order):
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Відправити Excel звіт", callback_data="send file"
        )
    )
    return builder.as_markup()


def decline_button():
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Скасувати", callback_data="decline"
        )
    )
    return builder.as_markup()
