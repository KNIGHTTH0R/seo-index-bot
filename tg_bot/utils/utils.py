import hashlib
import hmac
import re

from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


def extract_links(links):  # func to check valid urls
    url_pattern = re.compile(
        r"\b(?:http:\/\/|https:\/\/)?[\w-]+(?:\.[\w-]+)+(?:[\w.,@?^=%&amp;:\/~+#-]*[\w@?^=%&amp;\/~+#-])?\b"
    )
    urls = re.findall(url_pattern, links)
    return urls


class OrderIdFactory(CallbackData, prefix="order_id"):
    id_order: int


def button_confirm(id_order):
    builder = InlineKeyboardBuilder()
    # TODO add i18n translation
    builder.add(
        types.InlineKeyboardButton(
            text="В процесі", callback_data=OrderIdFactory(id_order=id_order).pack()
        )
    )
    return builder.as_markup()


def generate_signature(merchant_key, data_str):
    return hmac.new(merchant_key.encode(), data_str.encode(), hashlib.md5).hexdigest()
