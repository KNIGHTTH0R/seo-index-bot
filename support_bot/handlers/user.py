import logging
import os
import re
from io import BytesIO

from aiogram import Router, types, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BufferedInputFile, ReplyKeyboardRemove, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import KeyboardBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from infrastructure.database.repo.base import Repo
from support_bot.keyboards.inline import send_file_button, decline_button
from support_bot.handlers.states import AdminMenu
from tg_bot.utils.utils import OrderIdFactory

user_router = Router()


@user_router.callback_query(OrderIdFactory.filter())
async def submit_admin(
        c: types.CallbackQuery,
        callback_data: OrderIdFactory,
        repo: Repo,
        state: FSMContext,
        main_bot: Bot,
        scheduler: AsyncIOScheduler,
        bot: Bot
):
    current_state = await state.get_state()
    if current_state is None:
        await process_order(c, callback_data, repo, bot, state, main_bot, scheduler)
    else:
        await c.answer("Потрібно завершити інший заказ")

@user_router.callback_query(AdminMenu.start, F.data == "send file")
async def get_file(
        call: types.CallbackQuery,
        state: FSMContext
):
    await call.message.edit_reply_markup()
    await call.answer()
    await call.message.answer("Надішліть Excel звіт", reply_markup=decline_button())
    await state.set_state(AdminMenu.send_file)


@user_router.callback_query(AdminMenu.send_file, F.data == "decline")
async def decline(
        call: types.CallbackQuery,
        state: FSMContext
):
    logging.info("decline handler called")
    data = await state.get_data()
    order_id = data.get("order_id")
    document_id = data.get("document_id")
    package_info = data.get("package")
    await call.answer()
    await call.message.answer_document(document=document_id, caption=f"""
Ви прийняли це замовлення №{order_id}
Пакет: {package_info}

Посилання в файлі.

Вам необхідно відправити звіт протягом 12 днів!

Натисніть кнопку, коли будете готові прислати Excel файл
            """, reply_markup=send_file_button(order_id))
    await state.set_state(AdminMenu.start)


async def report_not_sent(bot: Bot, chat_id: int):
    await bot.send_message(chat_id, "Звіт не був відправлений.")
    return


@user_router.message(AdminMenu.send_file, F.document)
async def submitted_order(
        message: Message,
        state: FSMContext,
        repo: Repo,
        bot: Bot,
        main_bot: Bot
):
    content = BytesIO()
    await bot.download(message.document, content)
    file_info = await bot.get_file(message.document.file_id)
    file_extension = os.path.splitext(file_info.file_path)[1]
    content.seek(0)
    document_content = content.getvalue()

    await message.answer("""
Чудово!

Це замовлення було виконано""")

    data = await state.get_data()
    user_id = data["user_id"]
    order_id = data["order_id"]
    language = await repo.get_user_language(tg_id=user_id)
    logging.info(f"language: {language}")
    if language == "ua":
        await main_bot.send_document(user_id, document=BufferedInputFile(file=document_content,
                                                                         filename=f"stats {order_id}{file_extension}"),
                                     caption="<b>Ваше замовлення було виконано!\nЗвіт в цьому файлі</b>")
    else:
        await main_bot.send_document(user_id, document=BufferedInputFile(file=document_content,
                                                                         filename=f"stats {order_id}{file_extension}"),
                                     caption="<b>Ваш заказ был выполнен!\nОтчет в этом файле</b>")
    await repo.change_status(status="already_done", order_id=int(order_id))
    await state.clear()
    return


async def   process_order(
        c: CallbackQuery, callback_data, repo, bot: Bot, state: FSMContext, main_bot: Bot, scheduler: AsyncIOScheduler
):
    chat_id = c.from_user.id
    await state.set_state(AdminMenu.start)
    match = re.search('Пакет: (\S+)', c.message.caption)
    if match:
        package_info = match.group(1)
        order_id = callback_data.id_order
        await c.answer()
        await c.message.answer_document(document=c.message.document.file_id, caption=f"""
Ви прийняли це замовлення №{order_id}
Пакет: {package_info}

Посилання в файлі.

Вам необхідно відправити звіт протягом 12 днів!

Натисніть кнопку, коли будете готові прислати Excel файл
            """, reply_markup=send_file_button(order_id))
        await c.message.delete_reply_markup()
        response = await repo.get_user_id_order(order_id)
        user_id, count_urls = response
        language = await repo.get_user_language(tg_id=user_id)
        logging.info(f"language {language}")
        await state.update_data(document_id=c.message.document.file_id, order_id=order_id, package=package_info,
                                user_id=user_id)
        if language == "ua":
            await main_bot.send_message(chat_id=user_id, text="""
            <b>
Ваше замовлення було прийнято в роботу!
Очікуйте, виконання замовлення може зайняти до 12 днів
</b>""")
        else:
            await main_bot.send_message(chat_id=user_id, text="""
            <b>
Ваш заказ был принят в работу!
Ожидайте, выполнение заказа может занять до 12 дней
</b>
                """)
        await repo.change_status(order_id=order_id, status="wait_tier")
        await repo.session.commit()
        scheduler.add_job(report_status_and_send, 'interval', args=[order_id, bot, chat_id, repo], seconds=1036800)


async def report_status_and_send(order_id: int, bot: Bot, chat_id: int, repo: Repo):
    if await repo.check_order_status(order_id):
        await report_not_sent(bot, chat_id)
