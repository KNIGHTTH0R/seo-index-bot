import pathlib
import typing
from typing import Any

from aiogram import F, Router, types
from aiogram.filters import CommandStart, Command, callback_data
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram_dialog import StartMode, DialogManager
from aiogram import Bot
from pathlib import Path

user_router = Router()


@user_router.message(CommandStart())
async def get_photo_id(message: Message):
    await message.answer("Вітаю")


