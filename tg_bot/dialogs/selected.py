from typing import Any

from aiogram.types import CallbackQuery, Message, BufferedInputFile
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from .states import BotMenu
from .states import Order
from ..utils.txtwork import prepare_document


async def to_profile(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(BotMenu.profile)


async def go_to_order(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(Order.get_url)


async def close_dialog(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.done()


async def get_links(message: Message, MessageInput, dialog_manager: DialogManager):
    user_text = message.text
    count_links, encode_links = prepare_document(user_text)
    photo = BufferedInputFile(encode_links, filename="file.txt")
    dialog_manager.dialog_data.update(count=count_links)
    await dialog_manager.switch_to(Order.confirm_url)


