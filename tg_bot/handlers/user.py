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

user_router = Router()
user_router.message.middleware(CheckUser())


@user_router.message(CommandStart())
async def user_start(message: Message):
    await message.answer(
        "Вас вітає телеграм бот, який допоможе  з індексацією URL-адрес в Google.\nГоловне меню за командою: /menu"
    )


@user_router.message(Command("menu"))
async def show_menu(message: Message, dialog_manager: DialogManager):
    username = message.from_user.username
    full_name = message.from_user.full_name
    user_id = message.from_user.id
    await dialog_manager.start(BotMenu.user_menu)
    dialog_manager.dialog_data.update(username=username, full_name=full_name, user_id=user_id)


@user_router.callback_query(OrderIdFactory.filter())
async def on_click_submit(callback: types.CallbackQuery, callback_data: OrderIdFactory, repo: Repo, bot: Bot, dialog_manager: DialogManager):
    order_id = str(callback_data).split("=")[1]
    response = await repo.get_user_id_order(int(order_id))
    await bot.send_message(chat_id=response[0], text="Посилання індексуються, очікуйте завершення індексації від кількох годин до кількох днів")
    await repo.transaction_minus(tg_id=response[0], amount_points=-response[1])
    await repo.change_status(order_id=int(order_id), status="submit")
    await callback.answer()
    await callback.message.edit_reply_markup()


