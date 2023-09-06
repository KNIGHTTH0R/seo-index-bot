import datetime
import hashlib
import logging
import re
from contextlib import suppress
from io import BytesIO
from typing import TYPE_CHECKING, Any

from _decimal import Decimal
from aiogram import enums, Bot
from aiogram.fsm.state import State
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton, )
from aiogram.utils.deep_linking import create_start_link
from aiogram.utils.markdown import hbold, hcode
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.common import ManagedWidget
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.input.text import TextInput, T
from aiogram_dialog.widgets.kbd import Button, Select

from ..misc.constants import COINS_TO_USD_RATE, PACKAGES

logger = logging.getLogger(__name__)
log_level = logging.INFO

from infrastructure.database.repo.base import Repo
from infrastructure.nowpayments.api import NowPaymentsAPI
from infrastructure.wayforpay.api import WayForPayAPI
from ..keyboards.inline import main_user_menu

if TYPE_CHECKING:
    from tg_bot.locales.stub import TranslatorRunner

from .states import BotMenu, LanguageMenu, AdminMenu, TierMenu
from .states import Order, Payment
from ..config_reader import load_config, Config
from ..utils.utils import button_confirm, extract_links, create_order, get_content_from_message, handle_order, \
    send_documents_to_admin


async def to_profile(
        callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    await dialog_manager.switch_to(BotMenu.profile)


async def go_to_order(
        callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    await dialog_manager.start(Order.get_url)


async def go_to_tier(
        callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    await dialog_manager.start(TierMenu.menu)


async def go_to_deposit_balance(
        callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    await dialog_manager.start(Payment.deposit_amount)


async def get_links(
        message: Message,
        mi: MessageInput,
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
                count_urls=count_extracted_url,
                urls=str_links,
                suma_in_dollars=count_extracted_url * COINS_TO_USD_RATE
            )
            await dialog_manager.switch_to(Order.confirm_url)
        else:
            await message.answer(i18n.less_than_1_links())
    elif message.document:
        content = BytesIO()
        document = await bot.download(message.document, content)
        read_document = document.read().decode("utf-8")
        list_urls = extract_links(read_document)
        count_extracted_url = len(list_urls)
        str_links = "\n".join(list_urls)
        logger.info(f"precount {count_extracted_url}")
        print(count_extracted_url)
        if count_extracted_url >= 1:
            dialog_manager.dialog_data.update(
                count_urls=count_extracted_url, urls=str_links,
                suma_in_dollars=count_extracted_url * COINS_TO_USD_RATE,
                document_file_id=message.document.file_id
            )
            await dialog_manager.switch_to(Order.confirm_url)
        else:
            await message.answer(i18n.less_than_1_links())
    else:
        await message.answer(i18n.undefined_type_document())


async def on_submit_order(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager,
):
    i18n: "TranslatorRunner" = dialog_manager.middleware_data["i18n"]
    repo: Repo = dialog_manager.middleware_data.get("repo")
    bot = dialog_manager.middleware_data["bot"]
    tg_id = dialog_manager.event.from_user.id
    count_links = dialog_manager.dialog_data.get("count_urls")
    links = dialog_manager.dialog_data.get("urls")
    usd_amount = dialog_manager.dialog_data.get("suma_in_dollars")
    document_file_id = dialog_manager.dialog_data.get("document_file_id")
    balance = await repo.get_balance(tg_id=tg_id)
    if round(balance, 1) < round(count_links * COINS_TO_USD_RATE, 1):
        await callback.answer(i18n.not_enough_balance(), show_alert=True)
        return
    logger.info(-count_links * COINS_TO_USD_RATE)
    await callback.message.answer(i18n.on_cofrim())
    order_id = await repo.add_order(
        count_urls=count_links, fk_tg_id=tg_id, urls=links, status="pending",
    )
    await repo.transaction_minus(tg_id=tg_id, usd_amount=-count_links * COINS_TO_USD_RATE, order_id=str(order_id))
    config = load_config(".env")
    admins = config.tg_bot.admin_ids
    for i in admins:
        with suppress():
            if not document_file_id:
                await bot.send_message(
                    chat_id=i,
                    text=f"ID замовлення: {order_id}\nID користувача: {dialog_manager.event.from_user.id}\nКількість посилань: {count_links}\nПосилання:\n{links}",
                    disable_web_page_preview=True,
                    reply_markup=button_confirm(order_id),
                )
            else:
                await  bot.send_document(
                    chat_id=i,
                    document=document_file_id,
                    caption=f"ID замовлення: {order_id}\nID користувача: {dialog_manager.event.from_user.id}\nКількість посилань: {count_links}",
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

    if int(message.text) < 7:
        await message.answer(i18n.min_deposit())
        return

    dialog_manager.dialog_data.update(usd_amount=float(message.text))
    logger.info(f'Dollars: {message.text}')

    await dialog_manager.switch_to(Payment.available_method)


def create_order_information(callback, dialog_manager: DialogManager):
    total_amount_usd = dialog_manager.dialog_data.get("usd_amount")

    order_time = datetime.datetime.now().timestamp()
    order_date = int(order_time)
    order_id = (
            f"{callback.from_user.id}-{total_amount_usd}-"
            + hashlib.sha1(str(order_date).encode()).hexdigest()
    )
    logger.info(f'Total amount (USD): {total_amount_usd}')
    logger.info(f'Order ID: {order_id}')
    logger.info(f'Order date: {order_date}')

    return total_amount_usd, order_id, order_date


async def pay_wayforpay(
        callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    i18n: "TranslatorRunner" = dialog_manager.middleware_data.get("i18n")
    repo: Repo = dialog_manager.middleware_data.get("repo")

    total_amount_usd, order_id, order_date = create_order_information(
        callback, dialog_manager
    )

    wayforpay: WayForPayAPI = dialog_manager.middleware_data.get("wayforpay")
    logger.info(f'Dollars: {total_amount_usd}')
    invoice = await wayforpay.create_invoice(
        product_name=f"Поповнення балансу на суму {total_amount_usd} $",
        product_price=int(total_amount_usd),
        product_count=1,
        currency="USD",
        order_date=order_date,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
        order_reference=order_id,
    )
    logger.info(invoice)
    logger.info(f'link: {invoice.invoiceUrl}')

    await repo.create_tx(
        order_id,
        callback.from_user.id,
        amount=total_amount_usd,
        usd_amount=total_amount_usd,
        currency="USD"
    )
    await callback.message.edit_text(
        i18n.pay_message(
            usd_amount=hbold(str(total_amount_usd)),
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
    total_amount_usd, order_id, order_date = create_order_information(
        callback, dialog_manager
    )
    logger.info(f'Total amount (USD): {total_amount_usd}')
    if total_amount_usd < 7:
        await callback.message.answer(i18n.amount_less_35())
        await dialog_manager.switch_to(Payment.deposit_amount)
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
        usd_amount=total_amount_usd,
        currency=currency,
    )

    payment = await generate_crypto_payment(
        config, nowpayments, total_amount_usd, currency, order_id
    )
    await callback.message.edit_text(
        i18n.pay_message_crypto(
            crypto_amount=hcode(str(round(payment.pay_amount * 100000) / 100000)),
            address=hbold(str(payment.pay_address)),
            currency=hbold(str(payment.pay_currency).upper()),
        )
        ,
    )


async def on_error_func(
        message: Message,
        ti: TextInput,
        dialog_manager: DialogManager
):
    await message.answer("<b>Формат неправильный</b>")


async def get_id_menu(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.switch_to(AdminMenu.id)


async def to_suma_menu(
        message: Message,
        ti: TextInput,
        dialog_manager: DialogManager,
        data: str
):
    repo: Repo = dialog_manager.middleware_data.get("repo")
    id_match = r'^-?\d+$'
    username_match = r'^@\w+$'
    info = message.text

    if re.match(id_match, info):
        id_user = int(info)
        check_user = await repo.find_user_by_id(tg_id=id_user)
        if not check_user:
            await message.answer("Юзера с таким айди не существует")
            await dialog_manager.switch_to(AdminMenu.menu)
            return
    elif re.match(username_match, info):
        username = info[1:]
        id_user = await repo.find_user(username=username)

        if not id_user:
            await message.answer("Юзера с таким username не существует")
            await dialog_manager.switch_to(AdminMenu.menu)
            return
    else:
        await message.answer("Неправильный формат")
        return

    dialog_manager.dialog_data.update(user_id=id_user)
    await dialog_manager.switch_to(AdminMenu.suma)


async def get_suma(
        message: Message,
        ti: TextInput,
        dialog_manager: DialogManager,
        data: T
):
    user_input_amount = Decimal(message.text)
    bot = dialog_manager.middleware_data.get("bot")
    repo = dialog_manager.middleware_data.get("repo")
    user_id = dialog_manager.dialog_data.get("user_id")

    current_balance_in_dollars = await repo.get_balance(tg_id=user_id)
    if user_input_amount < 0 and abs(user_input_amount) > current_balance_in_dollars:
        user_input_amount = -current_balance_in_dollars
    order_id = create_order(user_id, user_input_amount)
    await repo.create_tx(order_id=order_id, tg_id=user_id, amount=user_input_amount,
                         usd_amount=user_input_amount,
                         currency="USD", status=True, comment="admin")
    await message.answer("Баланс пользователя был успешно изменен")
    await dialog_manager.switch_to(AdminMenu.menu)


async def to_back_menu_admin(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.switch_to(AdminMenu.menu)


async def to_stats(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
):
    await dialog_manager.switch_to(AdminMenu.stats)


async def to_confirm_tier(
        callback: CallbackQuery,
        managed: ManagedWidget[Select],
        dialog_manager: DialogManager,
        tariff_name: str
):
    repo: Repo = dialog_manager.middleware_data.get("repo")
    balance = await repo.get_balance(tg_id=callback.from_user.id)
    i18n: "TranslatorRunner" = dialog_manager.middleware_data["i18n"]
    tariff_price = PACKAGES.get(tariff_name)
    dialog_manager.show_mode = ShowMode.SEND
    if balance >= tariff_price:
        dialog_manager.dialog_data.update(package=tariff_name, price=tariff_price)
        await dialog_manager.switch_to(TierMenu.confirm)
    else:
        await callback.message.answer(i18n.not_enough_balance())
        await dialog_manager.done()
        await dialog_manager.start(BotMenu.user_menu)


async def decline(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager,
):
    i18n: TranslatorRunner = dialog_manager.middleware_data.get("i18n")
    await dialog_manager.done()
    await callback.message.answer(i18n.decline())
    await dialog_manager.start(BotMenu.user_menu)


async def to_get_text(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager,
):
    await dialog_manager.switch_to(TierMenu.get_links)


async def get_urls(
        message: Message,
        mi: MessageInput,
        dialog_manager: DialogManager,
        **kwargs,
):
    bot: Bot = dialog_manager.middleware_data.get("bot")
    i18n: "TranslatorRunner" = dialog_manager.middleware_data["i18n"]
    links, content = await get_content_from_message(message, bot)
    if links:
        order_id = await handle_order(message, dialog_manager, links)
        await send_documents_to_admin(dialog_manager, order_id, content)
        await dialog_manager.done()
        await dialog_manager.start(BotMenu.user_menu)
    else:
        await dialog_manager.done()
        await dialog_manager.start(BotMenu.user_menu)
        await message.answer(i18n.undefined_type_document())


async def referral_system(
        callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    i18n: "TranslatorRunner" = dialog_manager.middleware_data["i18n"]
    bot: Bot = dialog_manager.middleware_data.get("bot")
    repo: Repo = dialog_manager.middleware_data.get("repo")
    user_id = callback.from_user.id
    count_referrals = await repo.get_referrals_count(tg_id=user_id)
    count_money = await repo.get_total_referral_amount(tg_id=user_id)
    referral_link = await create_start_link(bot, payload=f"ref-{callback.from_user.id}", encode=True)
    await bot.send_message(chat_id=user_id,
                           text=i18n.ref(count_referrals=count_referrals,
                                         count_money=count_money,
                                         referral_link=referral_link))
