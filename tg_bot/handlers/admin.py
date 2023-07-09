from aiogram import Bot, F, Router
from aiogram.filters.command import Command, CommandStart
from aiogram.types import Message

from tg_bot.filters.admin import IsAdminFilter

admin_router = Router()
admin_router.message.filter(IsAdminFilter())


@admin_router.message(CommandStart())
async def admin_start(message: Message):
    await message.reply("Вітаю, адміне!")


