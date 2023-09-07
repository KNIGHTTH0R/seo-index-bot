from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing_extensions import TYPE_CHECKING


class SendFileCB(CallbackData, prefix="send_file"):
    order_id: int
    action: str


def send_file_button(order_id):
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Відправити Excel звіт",
            callback_data=SendFileCB(order_id=order_id, action="send").pack(),
        )
    )
    return builder.as_markup()


def decline_button(order_id: int):
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Скасувати",
            callback_data=SendFileCB(order_id=order_id, action="decline").pack(),
        )
    )
    return builder.as_markup()
