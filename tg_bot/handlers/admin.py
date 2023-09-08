from _decimal import Decimal
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
from tg_bot.utils.utils import create_order

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


@admin_router.message(Command("stats"))
async def stats(message: Message, repo: Repo):
    day_stats, week_stats, two_weeks_stats, month_stats, users_count = await repo.get_stats()
    top_referrers = await repo.get_top_referrers()
    top_earnings = await repo.get_top_referrers_earnings()

    main_text = f"""Статистика пополнений:
1 день:    {day_stats} $
1 неделя:  {week_stats} $
2 недели:  {two_weeks_stats} $
1 месяц:   {month_stats} $
Всего пользователей: {users_count}
"""

    top_referrers_text = "Топ 10 рефералов:\nРанг | ID | Рефералов\n"
    for rank, tg_id, fullname, referrals in top_referrers:
        user_link = f'<a href="tg://user?id={tg_id}">{fullname}</a>'
        top_referrers_text += f"{rank} | {user_link} | {referrals}\n"

    top_earnings_text = "Топ 10 доходов:\nРанг | ID | Доход $\n"
    for rank, tg_id, fullname, earnings in top_earnings:
        user_link = f'<a href="tg://user?id={tg_id}">{fullname}</a>'
        top_earnings_text += f"{rank} | {user_link} | {earnings}\n"

    text = f"<b>{main_text}\n\n{top_referrers_text}\n\n{top_earnings_text}</b>"

    await message.answer(text)





@admin_router.message(
    F.text.regex(r"/set_balance (\d+) ([+-]?\d+)")
    .group(1)
    .cast(int)
    .rename("user_input_amount"),
    F.text.regex(r"/set_balance (\d+) ([+-]?\d+)").group(2).cast(int).rename("balance"),
)
@admin_router.message(
    F.text.regex(r"/set_balance (\d+) ([+-]?\d+)")
    .group(2)
    .cast(int)
    .rename("user_input_amount"),
    F.text.regex(r"/set_balance @(\w+) ([+-]?\d+)")
    .group(1)
    .cast(str)
    .rename("username"),
)
async def set_balance(
        message: Message,
        repo: Repo,
        id_user: int = None,
        user_input_amount: int = None,
        username: str = None,
):
    user_input_amount = Decimal(user_input_amount)

    if id_user:
        if not await repo.find_user_by_id(tg_id=id_user):
            id_user = None
    elif username:
        id_user = await repo.find_user(username=username)
    else:
        await message.answer(
            f"Неправильная команда, используй: `/set_balance <ID> <balance>` "
            f"или `/set_balance <username> <balance>`"
        )

    if not id_user:
        await message.answer(f"Пользователь не найден")
        return

    current_balance_in_dollars = await repo.get_balance(tg_id=id_user)
    if user_input_amount < 0 and abs(user_input_amount) > current_balance_in_dollars:
        user_input_amount = -current_balance_in_dollars
    order_id = create_order(id_user, user_input_amount)
    await repo.create_tx(
        order_id=order_id,
        tg_id=id_user,
        amount=user_input_amount,
        usd_amount=user_input_amount,
        currency="USD",
        status=True,
        comment="admin",
    )


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
