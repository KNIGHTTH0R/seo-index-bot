import logging
import os
from io import BytesIO

from aiogram import Router, types, Bot, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BufferedInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from infrastructure.database.repo.base import Repo
from support_bot.handlers.states import AdminMenu
from support_bot.keyboards.inline import send_file_button, decline_button, SendFileCB
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
    bot: Bot,
):
    chat_id = c.from_user.id
    order_id = callback_data.id_order
    await c.answer()
    await c.message.edit_caption(
        caption=c.message.caption
        + """
Ви прийняли це замовлення!

Вам необхідно відправити звіт протягом 12 днів!

Натисніть кнопку, коли будете готові прислати Excel файл
""",
        reply_markup=send_file_button(order_id),
    )
    response = await repo.get_user_id_order(order_id)
    user_id, count_urls = response
    language = await repo.get_user_language(tg_id=user_id)
    logging.info(f"language {language}")
    if language == "ua":
        text = f"""
            <b>
Ваше замовлення #{order_id} було прийнято в роботу!
Очікуйте, виконання замовлення може зайняти до 12 днів
</b>"""
    else:
        text = f"""
            <b>
Ваш заказ #{order_id} был принят в работу!
Ожидайте, выполнение заказа может занять до 12 дней
</b>
                """

    await main_bot.send_message(
        chat_id=user_id,
        text=text,
    )
    await repo.change_status(order_id=order_id, status="wait_tier")
    await repo.session.commit()
    scheduler.add_job(
        report_status_and_send,
        "interval",
        args=[order_id, bot, chat_id, repo],
        seconds=1036800,
    )


@user_router.callback_query(
    SendFileCB.filter(F.action == "send"), ~StateFilter(AdminMenu.send_file)
)
async def get_file(
    call: types.CallbackQuery, state: FSMContext, callback_data: SendFileCB
):
    await call.answer()
    await state.update_data(
        order_id=callback_data.order_id,
    )
    text = call.message.caption.splitlines()[:-1] + ["Надішліть Excel звіт"]
    text = "\n".join(text)
    await call.message.edit_caption(
        caption=text, reply_markup=decline_button(order_id=callback_data.order_id)
    )
    await state.set_state(AdminMenu.send_file)


@user_router.callback_query(
    SendFileCB.filter(F.action == "send"), StateFilter(AdminMenu.send_file)
)
async def get_file_another_order_error(call: types.CallbackQuery, state: FSMContext):
    await call.answer("Потрібно завершити інший заказ")


@user_router.callback_query(
    StateFilter(AdminMenu.send_file), SendFileCB.filter(F.action == "decline")
)
async def decline(
    call: types.CallbackQuery, state: FSMContext, callback_data: SendFileCB
):
    logging.info("decline handler called")
    text = call.message.caption.splitlines()[:-1] + ["Звіт не був відправлений"]
    text = "\n".join(text)
    await call.message.edit_caption(
        caption=text, reply_markup=send_file_button(order_id=callback_data.order_id)
    )
    await state.clear()


async def report_not_sent(bot: Bot, chat_id: int):
    await bot.send_message(chat_id, "Звіт не був відправлений.")


@user_router.message(StateFilter(AdminMenu.send_file), F.document)
async def submitted_order(
    message: Message, state: FSMContext, repo: Repo, bot: Bot, main_bot: Bot
):
    content = BytesIO()
    await bot.download(message.document, content)
    file_info = await bot.get_file(message.document.file_id)
    file_extension = os.path.splitext(file_info.file_path)[1]
    content.seek(0)
    document_content = content.getvalue()

    await message.answer(
        """
Чудово!

Це замовлення було виконано"""
    )

    data = await state.get_data()
    order_id = data["order_id"]
    user_id, count_urls = await repo.get_user_id_order(order_id)
    language = await repo.get_user_language(tg_id=user_id)
    logging.info(f"language: {language}")
    if language == "ua":
        caption = "<b>Ваше замовлення було виконано!\nЗвіт в цьому файлі</b>"
    else:
        caption = "<b>Ваш заказ был выполнен!\nОтчет в этом файле</b>"
    await main_bot.send_document(
        user_id,
        caption=caption,
        document=BufferedInputFile(
            file=document_content, filename=f"stats {order_id}{file_extension}"
        ),
    )
    await repo.change_status(status="already_done", order_id=int(order_id))
    await state.clear()


async def report_status_and_send(order_id: int, bot: Bot, chat_id: int, repo: Repo):
    if await repo.check_order_status(order_id):
        await report_not_sent(bot, chat_id)
