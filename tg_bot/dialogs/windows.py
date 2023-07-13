from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Back, Button, Cancel
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import MessageInput
from .keyboards import group_main_menu
from .states import BotMenu, Order
from .getters import profile_getter, photo_getter
from .selected import close_dialog, get_links


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
            Back(),
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
            Const("Вікно"),
            Format("{count}"),
            StaticMedia(

            )
            getter=photo_getter,
            state=Order.confirm_url
        )
    ]
