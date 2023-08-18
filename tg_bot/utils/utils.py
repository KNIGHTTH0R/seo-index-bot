import datetime
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
    builder.add(
        types.InlineKeyboardButton(
            text="В процесі", callback_data=OrderIdFactory(id_order=id_order).pack()
        )
    )
    return builder.as_markup()


def generate_signature(merchant_key, data_str):
    return hmac.new(merchant_key.encode(), data_str.encode(), hashlib.md5).hexdigest()


def create_order(id_user, balance):
    coins_per_dollar = 5
    total_coins = balance * coins_per_dollar
    order_time = datetime.datetime.now().timestamp()
    order_date = int(order_time)
    order_id = (
            f"{id_user}-{total_coins}-"
            + hashlib.sha1(str(order_date).encode()).hexdigest()
    )
    return order_id, total_coins


def type_factory_advanced(text: str):
    id_pattern = r'^-?\d+$'
    username_pattern = r'^@\w+$'
    if re.fullmatch(id_pattern, text) or re.fullmatch(username_pattern, text):
        return text
    else:
        raise ValueError('Input does not match any of the expected patterns.')