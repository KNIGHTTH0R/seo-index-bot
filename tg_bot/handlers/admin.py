import html
import re

from aiogram import Router
from aiogram.filters.command import CommandStart, Command
from aiogram.types import Message
from aiogram_dialog import DialogManager

from infrastructure.database.repo.base import Repo
from tg_bot.dialogs.states import AdminMenu
from tg_bot.filters.admin import IsAdminFilter
from tg_bot.utils.utils import create_order

admin_router = Router()
admin_router.message.filter(IsAdminFilter())


@admin_router.message(Command("admin"))
async def admin_start(message: Message, dialog_manager: DialogManager):
    await message.reply("Приветствую, администратор")
    await dialog_manager.start(AdminMenu.menu)


@admin_router.message(Command("stats"))
async def stats(message: Message, repo: Repo):
    day_stats, week_stats, two_weeks_stats, month_stats, users_count = await repo.get_stats()
    text = f"""<b>
Статистика:
- 1 день: {day_stats} $
- 1 неделя: {week_stats} $
- 2 недели: {two_weeks_stats} $
- 1 месяц: {month_stats} $
- Всего пользователей: {users_count}
</b>
    """
    await message.answer(text)


@admin_router.message(Command("set_balance"))
async def set_balance(message: Message, repo: Repo):
    id_match = re.fullmatch(r'/set_balance (\d+) ([+-]?\d+)', message.text)
    username_match = re.fullmatch(r'/set_balance (\w+) ([+-]?\d+)', message.text)
    if id_match:
        id_user, balance = map(int, id_match.groups())
        check_user = await repo.find_user_by_id(tg_id=id_user)
        if check_user:
            balance = balance
            current_balance_in_coins = await repo.get_balance(tg_id=id_user)
            current_balance_in_dollars = current_balance_in_coins * 0.2  # conversion
            if balance < 0 and current_balance_in_dollars + balance < 0:
                balance = -current_balance_in_dollars
            order_id, total_coins = create_order(id_user, balance)
            await repo.create_tx(order_id=order_id, tg_id=id_user, amount_points=total_coins, amount=balance,
                                 currency="USD", status=True, comment="admin")
            await message.answer("Баланс пользователя был успешно изменен")
        else:
            await message.answer("Юзера с таким айди не существует")
    elif username_match:
        username, balance = username_match.groups()
        balance = float(balance)  # Преобразование balance в число
        id_user = await repo.find_user(username=username)
        if id_user is not None:
            current_balance_in_coins = await repo.get_balance(tg_id=id_user)
            current_balance_in_dollars = current_balance_in_coins * 0.2  # conversion
            if balance < 0 and current_balance_in_dollars + balance < 0:
                balance = -current_balance_in_dollars
            order_id, total_coins = create_order(id_user, balance)
            await repo.create_tx(order_id=order_id, tg_id=id_user, amount_points=total_coins, amount=balance,
                                 currency="USD", status=True, comment="admin")
            await message.answer("Баланс пользователя был успешно изменен")
        else:
            await message.answer("Юзера с таким username не существует")
    else:
        await message.answer(
            "Неправильная команда, используй: `/set_balance " + html.escape("<ID>") + " " + html.escape(
                "<balance>") + "` или `/set_balance " + html.escape("<username>") + " " + html.escape(
                "<balance>") + "`")
