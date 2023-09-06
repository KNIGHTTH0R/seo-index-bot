import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from aiogram import Bot, flags
from aiogram import Router, types
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, BotCommandScopeAllPrivateChats, BotCommandScopeChat
from aiogram_dialog import DialogManager, StartMode

from infrastructure.database.repo.base import Repo
from tg_bot.dialogs.states import BotMenu, Order, Payment, LanguageMenu, TierMenu
from tg_bot.filters.translation import TranslationFilter
from tg_bot.keyboards.inline import main_user_menu
from tg_bot.middlewares.repo import CheckUser
from tg_bot.utils.utils import OrderIdFactory
if TYPE_CHECKING:
    from tg_bot.locales.stub import TranslatorRunner

user_router = Router()


@user_router.message(CommandStart(deep_link_encoded=True, deep_link=True))
@flags.command_description(
    scopes=[
        BotCommandScopeAllPrivateChats(),
        *[
            BotCommandScopeChat(chat_id=chat_id)
            for chat_id in [362089194, 292235412]
        ]
    ],
    en="Start menu (text)",
    uk="Стартове меню (текст)",
    ru="Стартовое меню (текст)",)
async def cmd_start(message: Message, user_info, command: CommandObject, repo: Repo, i18n: "TranslatorRunner"):
    deep_link_args = command.args
    parent_id = int(deep_link_args.split("-")[-1])
    created_at = user_info.created_at
    user_id = message.from_user.id
    current_time = datetime.now() - created_at
    logging.info(f"parent id {parent_id} user_id {user_id}")
    if parent_id != user_id:
        if current_time <= timedelta(minutes=1):
            await repo.set_referrer_id(tg_id=user_id, referrer_id=parent_id)
    await message.answer(i18n.hello(),
                         reply_markup=main_user_menu(i18n))
    return


@user_router.message(CommandStart())
@flags.command_description(
    scopes=[
        BotCommandScopeAllPrivateChats(),
        *[
            BotCommandScopeChat(chat_id=chat_id)
            for chat_id in [362089194, 292235412]
        ]
    ],
    en="Start menu (text)",
    uk="Стартове меню (текст)",
    ru="Стартовое меню (текст)",
)
async def user_start(message: Message, i18n: "TranslatorRunner"):
    await message.answer(i18n.hello(),
                         reply_markup=main_user_menu(i18n))


@user_router.message(Command("menu"))
@flags.command_description(
    scopes=[
        BotCommandScopeAllPrivateChats(),
        *[
            BotCommandScopeChat(chat_id=chat_id)
            for chat_id in [362089194, 292235412]
        ]
    ],
    en="Start menu (inline)",
    uk="Стартове меню (інлайн)",
    ru="Стартовое меню (инлайн)",
)
async def show_menu(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(BotMenu.user_menu)


@user_router.callback_query(OrderIdFactory.filter())
async def on_click_submit(
        callback: types.CallbackQuery,
        callback_data: OrderIdFactory,
        repo: Repo,
        bot: Bot,
        dialog_manager: DialogManager,
        i18n: "TranslatorRunner",
):
    await callback.answer()

    order_id = callback_data.id_order
    response = await repo.get_user_id_order(order_id)
    if not response:
        await callback.answer(i18n.message_order_not_found())
        return
    user_id, count_urls = response

    await repo.change_status(order_id=order_id, status="submit")
    await repo.session.commit()

    await bot.send_message(chat_id=user_id, text=i18n.message_confirm())
    await callback.message.delete_reply_markup()


@user_router.message(TranslationFilter('button_order'))
async def go_to_order(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(Order.get_url, mode=StartMode.RESET_STACK)


@user_router.message(TranslationFilter('button_profile'))
async def go_to_profile(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(BotMenu.profile, mode=StartMode.RESET_STACK)


@user_router.message(TranslationFilter('button_deposit'))
async def go_to_deposit_balance(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(Payment.deposit_amount, mode=StartMode.RESET_STACK)


@user_router.message(TranslationFilter('button_settings'))
async def go_to_settings(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(LanguageMenu.menu, mode=StartMode.RESET_STACK)


@user_router.message(TranslationFilter('button_tier'))
async def go_to_settings(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(TierMenu.menu, mode=StartMode.RESET_STACK)
