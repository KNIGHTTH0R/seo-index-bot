from _decimal import Decimal
from aiogram import Router, F, flags
from aiogram.filters.command import Command
from aiogram.types import Message, BotCommandScopeChat
from aiogram_dialog import DialogManager

from infrastructure.database.repo.base import Repo
from tg_bot.dialogs.states import AdminMenu
from tg_bot.filters.admin import IsAdminFilter
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
    (
        day_stats,
        week_stats,
        two_weeks_stats,
        month_stats,
        users_count,
    ) = await repo.get_stats()
    text = f"""<b>
Статистика пополнений:
- 1 день: {day_stats} $
- 1 неделя: {week_stats} $
- 2 недели: {two_weeks_stats} $
- 1 месяц: {month_stats} $
- Всего пользователей: {users_count}
</b>
    """
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
