import datetime
import hashlib
import math
from io import BytesIO
from typing import TYPE_CHECKING, Any

from aiogram import enums
from aiogram.fsm.state import State
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.markdown import hbold, hcode
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button

from infrastructure.database.repo.base import Repo
from infrastructure.nowpayments.api import NowPaymentsAPI
from infrastructure.wayforpay.api import WayForPayAPI
from ..keyboards.inline import main_user_menu

if TYPE_CHECKING:
    from tg_bot.locales.stub import TranslatorRunner

from .states import BotMenu, LanguageMenu
from .states import Order, Payment
from ..config_reader import load_config, Config
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
    await dialog_manager.start(Payment.deposit_amount)


async def get_links(
    message: Message,
    MessageInput,
    dialog_manager: DialogManager,
    **kwargs,
):
    bot = dialog_manager.middleware_data["bot"]
    i18n: "TranslatorRunner" = dialog_manager.middleware_data["i18n"]
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
):
    i18n: "TranslatorRunner" = dialog_manager.middleware_data["i18n"]
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
                text=f"ID замовлення: {order_id}\nID користувача: {dialog_manager.event.from_user.id}\nКількість посилань: {count_links}\nПосилання:\n{links}",
                disable_web_page_preview=True,
                reply_markup=button_confirm(order_id),
            )


def set_language(switch_to: State):
    async def wrapper(c: CallbackQuery, widget: Any, manager: DialogManager):
        repo: Repo = manager.middleware_data.get("repo")
        user = manager.middleware_data.get("user")
        language = widget.widget_id.split("_")[-1]
        await repo.change_language(c.from_user.id, language=language)
        await manager.switch_to(switch_to)

        t_hub = manager.middleware_data.get("th")

        i18n: "TranslatorRunner" = t_hub.get_translator_by_locale(
            language,
        )
        manager.middleware_data.update(i18n=i18n)
        await c.message.answer(text=i18n.language_changed(),
                               reply_markup=main_user_menu(i18n))

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


async def go_to_settings(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    await dialog_manager.start(LanguageMenu.menu)


async def get_deposit_amount(
    message: Message,
    widget: MessageInput,
    dialog_manager: DialogManager,
):
    i18n: "TranslatorRunner" = dialog_manager.middleware_data["i18n"]
    if not message.text.isdigit():
        await message.answer(i18n.not_digit())
        return

    dialog_manager.dialog_data.update(total_coins=message.text)
    await dialog_manager.switch_to(Payment.available_method)


def create_order_information(callback, dialog_manager: DialogManager):
    total_coins = int(dialog_manager.dialog_data.get("total_coins"))
    total_amount_usd = math.ceil(total_coins * 0.2)
    order_time = datetime.datetime.now().timestamp()
    order_date = int(order_time)
    order_id = (
        f"{callback.from_user.id}-{total_coins}-"
        + hashlib.sha1(str(order_date).encode()).hexdigest()
    )

    return total_coins, total_amount_usd, order_id, order_date

async def pay_wayforpay(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    i18n: "TranslatorRunner" = dialog_manager.middleware_data.get("i18n")
    repo: Repo = dialog_manager.middleware_data.get("repo")

    total_coins, total_amount_usd, order_id, order_date = create_order_information(
        callback, dialog_manager
    )
    wayforpay: WayForPayAPI = dialog_manager.middleware_data.get("wayforpay")

    invoice = await wayforpay.create_invoice(
        product_name=f"Поповнення балансу на суму {total_coins} монет.",
        product_price=total_amount_usd,
        product_count=1,
        currency="USD",
        order_date=order_date,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
        order_reference=order_id,
    )

    await repo.create_tx(
        order_id,
        callback.from_user.id,
        amount=total_amount_usd,
        currency="USD",
        amount_points=total_coins,
    )
    await callback.message.edit_text(
        i18n.pay_message(
            usd_amount=hbold(str(total_amount_usd)),
            coins=hbold(str(total_coins)),
            link=invoice.invoiceUrl,
        ),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=i18n.pay_button(), url=invoice.invoiceUrl)],
            ]
        ),
        parse_mode=enums.ParseMode.HTML,
    )


async def generate_crypto_payment(
    config: Config,
    nowpayments: NowPaymentsAPI,
    total_amount_usd: int,
    currency: str,
    order_id: str,
):
    estimated = await nowpayments.get_estimated_price(
        currency, amount=total_amount_usd
    )  # replace with your currency

    payment = await nowpayments.create_payment(
        price_amount=total_amount_usd,
        pay_amount=estimated.estimated_amount,
        price_currency="usd",
        pay_currency=currency,
        order_id=order_id,
        ipn_callback_url=f"{config.nowpayments.callback_url}",
    )
    return payment


async def pay_nowpayments(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    i18n: "TranslatorRunner" = dialog_manager.middleware_data.get("i18n")
    await callback.answer()
    total_coins, total_amount_usd, order_id, order_date = create_order_information(
        callback, dialog_manager
    )
    if total_coins < 100:
        await callback.message.edit_text(i18n.amount_less_100())
        return
    # answer with loading emoji
    await callback.message.edit_text("⏳")
    currency = button.widget_id.split("_")[-1]
    repo: Repo = dialog_manager.middleware_data.get("repo")
    nowpayments: NowPaymentsAPI = dialog_manager.middleware_data.get("nowpayments")
    config: Config = dialog_manager.middleware_data.get("config")

    crypto_amount = await nowpayments.get_estimated_price(
        currency, amount=total_amount_usd
    )
    tx_id = await repo.create_tx(
        order_id,
        callback.from_user.id,
        amount=crypto_amount.estimated_amount,
        currency=currency,
        amount_points=total_coins,
    )

    payment = await generate_crypto_payment(
        config, nowpayments, total_amount_usd, currency, order_id
    )
    await callback.message.edit_text(
        i18n.pay_message_crypto(
            crypto_amount=hcode(str(round(payment.pay_amount * 100000) / 100000)),
            address=hbold(str(payment.pay_address)),
            currency=hbold(str(payment.pay_currency).upper()),
        ),
    )
