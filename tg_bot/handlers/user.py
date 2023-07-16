import pathlib
import typing
from typing import Any

from aiogram import F, Router, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, FSInputFile, document
from aiogram_dialog import StartMode, DialogManager, ShowMode
from aiogram import Bot
from pathlib import Path
from aiogram.types import BufferedInputFile
from infrastructure.database.repo.base import Repo
from tg_bot.dialogs.states import BotMenu
from tg_bot.middlewares.repo import CheckUser
from tg_bot.utils.utils import OrderIdFactory

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tg_bot.locales.stub import TranslatorRunner

user_router = Router()
user_router.message.middleware(CheckUser())


@user_router.message(CommandStart())
async def user_start(message: Message, i18n: "TranslatorRunner"):
    await message.answer(
        i18n.hello()
    )


@user_router.message(Command("menu"))
async def show_menu(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(BotMenu.user_menu)


@user_router.callback_query(OrderIdFactory.filter())
async def on_click_submit(callback: types.CallbackQuery, callback_data: OrderIdFactory, repo: Repo, bot: Bot,
                          dialog_manager: DialogManager, i18n: "TranslatorRunner"):
    order_id = callback_data.id_order
    response = await repo.get_user_id_order(order_id)
    await bot.send_message(chat_id=response[0],
                           text=i18n.message_when_confirm_admin())
    await repo.transaction_minus(tg_id=response[0], amount_points=-response[1])
    await repo.change_status(order_id=order_id, status="submit")
    await callback.answer()
    await callback.message.edit_reply_markup()
