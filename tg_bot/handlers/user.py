import pathlib
import typing
from typing import Any

from aiogram import F, Router, types
from aiogram.filters import CommandStart, Command, callback_data
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, FSInputFile, document
from aiogram_dialog import StartMode, DialogManager
from aiogram import Bot
from pathlib import Path
from aiogram.types import BufferedInputFile
from infrastructure.database.repo.base import Repo
from tg_bot.dialogs.states import BotMenu
from tg_bot.middlewares.repo import CheckUser
from tg_bot.utils.txtwork import prepare_document

user_router = Router()
user_router.message.middleware(CheckUser())


@user_router.message(CommandStart())
async def user_start(message: Message, dialog_manager: DialogManager, repo: Repo, bot: Bot):
    await message.answer(
        "Вас вітає телеграм бот, який допоможе  з індексацією URL-адрес в Google.\nГоловне меню за командою: /menu")


@user_router.message(Command("menu"))
async def show_menu(message: Message, dialog_manager: DialogManager):
    username = message.from_user.username
    full_name = message.from_user.full_name
    user_id = message.from_user.id
    await dialog_manager.start(BotMenu.user_menu)
    dialog_manager.dialog_data.update(username=username, full_name=full_name, user_id=user_id)
