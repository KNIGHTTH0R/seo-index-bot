from aiogram import Router, F, flags
from aiogram.filters import StateFilter
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommandScopeChat, CallbackQuery
from aiogram_dialog import DialogManager

from infrastructure.database.repo.base import Repo
from tg_bot.dialogs.states import AdminMenu
from tg_bot.filters.admin import IsAdminFilter
from tg_bot.keyboards.inline import confirm_keyboard
from tg_bot.utils.broadcaster import broadcast

admin_router = Router()
admin_router.message.filter(IsAdminFilter())


@admin_router.message(Command("admin"))
@flags.command_description(
    scopes=[BotCommandScopeChat(chat_id=chat_id) for chat_id in [362089194, 292235412]],
    en="Admin menu",
    uk="Меню адміністратора",
    ru="Меню администратора",
)
async def admin_start(message: Message, dialog_manager: DialogManager):
    await message.reply("Приветствую, администратор")
    await dialog_manager.start(AdminMenu.menu)


@admin_router.message(Command("mailing"))
async def cmd_mailing(message: Message, state: FSMContext):
    text = "Введите текст рассылки"
    await message.answer(text)
    await state.set_state("mailing")


@admin_router.message(StateFilter("mailing"))
async def text_mailing(message: Message, state: FSMContext, repo: Repo):
    msg = await message.answer(message.html_text)
    await msg.reply(
        "Вы действительно хотите отправить это сообщение?",
        reply_markup=confirm_keyboard(),
    )
    await state.set_state("confirm_mailing")
    await state.update_data(text=message.html_text)


@admin_router.callback_query(F.data == "confirm", StateFilter("confirm_mailing"))
async def confirm_mailing(cq: CallbackQuery, state: FSMContext, repo: Repo, bot):
    data = await state.get_data()
    text = data["text"]
    users = await repo.get_all_users()
    await broadcast(bot, users, text)
    await cq.message.edit_text("Рассылка успешно отправлена")
    await state.clear()


@admin_router.callback_query(F.data == "cancel", StateFilter("confirm_mailing"))
async def cancel_mailing(cq: CallbackQuery, state: FSMContext):
    await cq.message.edit_text("Рассылка отменена")
    await state.clear()
