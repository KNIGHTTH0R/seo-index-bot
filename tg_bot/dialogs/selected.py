from io import BytesIO
from typing import TYPE_CHECKING, Any

from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from infrastructure.database.repo.base import Repo

if TYPE_CHECKING:
    from tg_bot.locales.stub import TranslatorRunner

from .states import BotMenu
from .states import Order
from ..config_reader import load_config
from ..utils.utils import button_confirm, extract_links


async def to_profile(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    await dialog_manager.switch_to(BotMenu.profile)


async def go_to_order(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    await dialog_manager.start(Order.get_url)


async def go_to_deposit_balance(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    await dialog_manager.switch_to(BotMenu.deposit_balance)


async def get_links(
    message: Message,
    MessageInput,
    dialog_manager: DialogManager,
    i18n: "TranslatorRunner",
    **kwargs,
):
    bot = dialog_manager.middleware_data["bot"]
    repo = dialog_manager.middleware_data.get("repo")
    user_text = message.text
    if message.text:
        list_urls = extract_links(user_text)
        count_extracted_url = len(list_urls)
        str_links = "\n".join(list_urls)
        if count_extracted_url >= 1:
            dialog_manager.dialog_data.update(
                count_urls=count_extracted_url, urls=str_links
            )
            await dialog_manager.switch_to(Order.confirm_url)
        else:
            await message.answer(i18n.zero_links())
    elif message.document:
        content = BytesIO()
        document = await bot.download(message.document, content)
        read_document = document.read().decode("utf-8")
        list_urls = extract_links(read_document)
        count_extracted_url = len(list_urls)
        str_links = "\n".join(list_urls)
        if count_extracted_url >= 1:
            dialog_manager.dialog_data.update(
                count_urls=count_extracted_url, urls=str_links
            )
            await dialog_manager.switch_to(Order.confirm_url)
        else:
            await message.answer(i18n.zero_links())
    else:
        await message.answer(i18n.undefined_type_document())


async def on_submit_order(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
    i18n: "TranslatorRunner",
):
    repo = dialog_manager.middleware_data.get("repo")
    bot = dialog_manager.middleware_data["bot"]
    tg_id = dialog_manager.event.from_user.id
    count_links = dialog_manager.dialog_data.get("count_urls")
    links = dialog_manager.dialog_data.get("urls")
    balance = await repo.get_balance(tg_id=tg_id)
    if balance < count_links:
        await callback.answer(i18n.not_enough_balance(), show_alert=True)
    else:
        await callback.message.answer(i18n.on_cofrim())
        order_id = await repo.add_order(
            count_urls=count_links, fk_tg_id=tg_id, urls=links, status="pending"
        )
        config = load_config(".env")
        admins = config.tg_bot.admin_ids
        for i in admins:
            await bot.send_message(
                chat_id=i,
                # TODO use i18n and .format()
                text=f"ID замовлення: {order_id}\nID користувача: {dialog_manager.event.from_user.id}\nКількість посилань: {count_links}\nПосилання:\n{links}",
                disable_web_page_preview=True,
                reply_markup=button_confirm(order_id),
            )


def set_language(switch_to: State):
    async def wrapper(c: CallbackQuery, widget: Any, manager: DialogManager):
        repo: Repo = manager.middleware_data.get("repo")
        user = manager.middleware_data.get("user")
        language = widget.widget_id.split("_")[-1]
        # TODO: add update_user method to repo
        await repo.update_user(c.from_user.id, language=language)
        await manager.switch_to(switch_to)

        t_hub = manager.middleware_data.get("th")

        i18n: "TranslatorRunner" = t_hub.get_translator_by_locale(
            language,
        )
        manager.middleware_data.update(i18n=i18n)
        await c.answer(i18n.language_changed())

    return wrapper


def open_close_menu(switch_to: State):
    async def wrapper(c: CallbackQuery, widget: Any, manager: DialogManager):
        data = manager.dialog_data
        if data.get(widget.widget_id):
            data.pop(widget.widget_id, None)
        else:
            data[widget.widget_id] = True

        await manager.switch_to(switch_to)

    return wrapper
