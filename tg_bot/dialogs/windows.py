from aiogram.types import ContentType
from aiogram_dialog import Window, DialogManager
from aiogram_dialog.widgets.kbd import Back, Button, Cancel
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import MessageInput
from .keyboards import group_main_menu, order_pend
from .states import BotMenu, Order
from .getters import profile_getter, count_getter, get_order_id
from .selected import get_links


async def main_user_menu_window():
    return [
        Window(
            Const("Головне меню"),
            await group_main_menu(),
            state=BotMenu.user_menu
        ),
        Window(
            Const("Ваш профіль:"),
            Format("Username: {username}\nБаланс: {balance}"),
            Back(Const("Назад")),
            getter=profile_getter,
            state=BotMenu.profile
        )
    ]


async def order_links():
    return [
        Window(
            Const(
                "Для того, Щоб Вам замовити індексацію, потрібно відправити URL-адреси в форматі txt файлу або повідомленням.\nПриклад: \nhttps://soundcloud.com\nhttps://www.youtube.com\n1 url = 1 монета"),
            Cancel(Const("Назад")),
            MessageInput(
                func=get_links
            ),
            disable_web_page_preview=True,
            state=Order.get_url,
        ),
        Window(
            Const("Підтвердження замовлення"),
            Format("Кількість посилань: {count}\nДо сплати: {count} монет"),
            await order_pend(),
            Back(Const("Назад")),
            getter=count_getter,
            state=Order.confirm_url
        )
    ]

async def deposit():
    return [
        Window(
            Const("Поповнення балансу")
        )
    ]