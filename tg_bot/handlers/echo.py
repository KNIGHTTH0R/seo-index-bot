from typing import TYPE_CHECKING

from aiogram import Router
from aiogram.types import Message

from tg_bot.keyboards.inline import main_user_menu

if TYPE_CHECKING:
    from tg_bot.locales.stub import TranslatorRunner

echo_router = Router()


@echo_router.message()
async def unknown_message(message: Message, i18n: "TranslatorRunner"):
    await message.answer("Unknown message", reply_markup=main_user_menu(i18n))
