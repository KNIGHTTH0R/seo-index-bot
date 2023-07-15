from io import BytesIO
from typing import Any

from aiogram import Bot
from aiogram.types import CallbackQuery, Message, BufferedInputFile
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from environs import Env

from .states import BotMenu
from .states import Order
from ..config_reader import load_config
from ..utils.utils import button_confirm, extract_links
from infrastructure.database.repo.base import Repo


async def to_profile(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(BotMenu.profile)


async def go_to_order(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(Order.get_url)


async def go_to_deposit_balance(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(BotMenu.deposit_balance)


async def get_links(message: Message, MessageInput, dialog_manager: DialogManager, **kwargs):
    bot = dialog_manager.middleware_data["bot"]
    repo = dialog_manager.middleware_data.get("repo")
    user_text = message.text
    if message.text:
        list_urls = extract_links(user_text)
        count_extracted_url = len(list_urls)
        str_links = '\n'.join(list_urls)
        if count_extracted_url >= 1:
            dialog_manager.dialog_data.update(count_urls=count_extracted_url,
                                              urls=str_links
                                              )
            await dialog_manager.switch_to(Order.confirm_url)
        else:
            await message.answer("Кількість посилань не може бути меньше 1")
    elif message.document:
        content = BytesIO()
        document = await bot.download(message.document, content)
        read_document = document.read().decode("utf-8")
        list_urls = extract_links(read_document)
        count_extracted_url = len(list_urls)
        str_links = '\n'.join(list_urls)
        if count_extracted_url >= 1:
            dialog_manager.dialog_data.update(count_urls=count_extracted_url,
                                              urls=str_links
                                              )
            await dialog_manager.switch_to(Order.confirm_url)
        else:
            await message.answer("Кількість посилань не може бути меньше 1")
    else:
        await message.answer("Невідомий тип документу")


async def on_submit_order(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    repo = dialog_manager.middleware_data.get("repo")
    bot = dialog_manager.middleware_data["bot"]
    tg_id = dialog_manager.event.from_user.id
    count_links = dialog_manager.dialog_data.get("count_urls")
    links = dialog_manager.dialog_data.get("urls")
    balance = await repo.get_balance(tg_id=tg_id)
    if balance < count_links:
        await callback.answer("Недостатньо монет на рахунку. Будь ласка, поповніть баланс", show_alert=True)
    else:
        await callback.message.answer("Ваше замовлення перевіряється адміністатором, очікуйте повідомлення від бота.")
        order_id = await repo.add_order(count_urls=count_links, fk_tg_id=tg_id, urls=links,
                                        status="pending")
        config = load_config(".env")
        admins = config.tg_bot.admin_ids
        for i in admins:
            await bot.send_message(chat_id=i,
                                   text=f"ID замовлення: {order_id}\nID користувача: {dialog_manager.event.from_user.id}\nКількість посилань: {count_links}\nПосилання:\n{links}",
                                   disable_web_page_preview=True,
                                   reply_markup=button_confirm(order_id))
