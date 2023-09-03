import datetime
import hashlib
import hmac
import logging
import re
from contextlib import suppress
from io import BytesIO

from aiogram import types, Bot
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import DialogManager


from tg_bot.config_reader import load_config


def extract_links(links):  # func to check valid urls
    url_pattern = re.compile(
        r"\b(?:http:\/\/|https:\/\/)?[\w-]+(?:\.[\w-]+)+(?:[\w.,@?^=%&amp;:\/~+#-]*[\w@?^=%&amp;\/~+#-])?\b"
    )
    urls = re.findall(url_pattern, links)
    return urls


class OrderIdFactory(CallbackData, prefix="order_id"):
    id_order: int


def button_confirm(id_order, text: str = "В процесі"):
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text=text, callback_data=OrderIdFactory(id_order=id_order).pack()
        )
    )
    return builder.as_markup()


def generate_signature(merchant_key, data_str):
    return hmac.new(merchant_key.encode(), data_str.encode(), hashlib.md5).hexdigest()


def create_order(id_user, amount):
    order_time = datetime.datetime.now().timestamp()
    order_date = int(order_time)
    order_id = (
            f"{id_user}-{amount}-"
            + hashlib.sha1(str(order_date).encode()).hexdigest()
    )
    return order_id


def type_factory_advanced(text: str):
    id_pattern = r'^-?\d+$'
    username_pattern = r'^@\w+$'
    if re.fullmatch(id_pattern, text) or re.fullmatch(username_pattern, text):
        return text
    else:
        raise ValueError('Input does not match any of the expected patterns.')


async def get_content_from_message(message: Message, bot: Bot):
    links = content = None
    if message.text:
        content = BytesIO()
        links = message.text
        content.write(message.text.encode("utf-8"))
    elif message.document:
        content = BytesIO()
        await bot.download(message.document, content)
        content.seek(0)
        links = content.read().decode("utf-8")
    return links, content


async def handle_order(message: Message, dialog_manager: DialogManager, links):
    tg_id = message.from_user.id
    usd_amount = dialog_manager.dialog_data.get("price")
    repo = dialog_manager.middleware_data.get("repo")
    i18n: "TranslatorRunner" = dialog_manager.middleware_data["i18n"]

    order_id = await repo.add_order(
        count_urls=None, fk_tg_id=tg_id, urls=links, status="pending_tier"
    )
    await repo.transaction_minus(tg_id=tg_id, usd_amount=-usd_amount, order_id=str(order_id))
    await message.answer(i18n.when_send())
    return order_id


async def send_documents_to_admin(dialog_manager: DialogManager, order_id, content):
    config = load_config(".env")
    bot_support = dialog_manager.middleware_data.get("bot_support")
    admins = config.tg_bot.admin_ids
    package = dialog_manager.dialog_data.get("package")
    file_data = content.getvalue()
    for i in admins:
        with suppress():
            await bot_support.send_document(
                chat_id=i,
                document=BufferedInputFile(file=file_data, filename=f"{package}" + f"{ order_id}.txt"),
                caption=f"""
Поступило замовлення №{order_id}
Пакет: {package}
Посилання в файлі.""",
                reply_markup=button_confirm(order_id, text="Прийняти в роботу"),
            )


