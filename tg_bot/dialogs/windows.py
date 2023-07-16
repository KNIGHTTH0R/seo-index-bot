from aiogram.types import ContentType
from aiogram.utils import i18n
from aiogram_dialog import Window, DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Back, Button, Cancel, Start
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import MessageInput

from . import selected
from .keyboards import group_main_menu, order_pend, choose_type_payment
from .states import BotMenu, Order
from .getters import profile_getter, count_getter, get_order_id
from .selected import get_links
from ..utils.translation_utils import dropdown_on_off_menu, Option, TranslatableFormat


def main_user_menu_window():
    return [
        Window(
            Const("Головне меню"),
            group_main_menu(),
            state=BotMenu.user_menu
        ),
        Window(
            Const("Ваш профіль:"),
            Format("Username: {username}\nБаланс: {balance}"),
            Back(Const("Назад")),
            getter=profile_getter,
            state=BotMenu.profile
        ),
        Window(
            Const("Поповнення балансу"),
            choose_type_payment(),
            Back(Const("Назад")),
            state=BotMenu.deposit_balance
        )
    ]


def order_links():
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
            order_pend(),
            Back(Const("Назад")),
            getter=count_getter,
            state=Order.confirm_url
        )
    ]


def language_menu_window():
    return Window(
        *dropdown_on_off_menu(
            dropdown_title=i18n.dialogs.buttons.change_language(),
            selection_key="change_language",
            options=[
                Option(
                    id="set_lang_en",
                    text=i18n.dialogs.buttons.english(),
                    when_key="lang_en",
                ),
                Option(
                    id="set_lang_uk",
                    text=i18n.dialogs.buttons.ukrainian(),
                    when_key="lang_uk",
                ),
                Option(
                    id="set_lang_ru",
                    text=i18n.dialogs.buttons.russian(),
                    when_key="lang_ru",
                ),
            ],
            on_click=selected.set_language(switch_to=LanguageMenu.menu),
            on_open_close=selected.open_close_menu(switch_to=LanguageMenu.menu),
        ),
        Start(
            TranslatableFormat(i18n.dialogs.buttons.back()),
            id="back_to_main_menu",
            state=MainMenu.menu,
            mode=StartMode.RESET_STACK,
        ),
        Cancel(TranslatableFormat(i18n.dialogs.buttons.exit()), result={"exit": True}),
        state=LanguageMenu.menu,
        getter=(getters.get_settings, getters.get_lang_setting),
        parse_mode=ParseMode.HTML,
    )
