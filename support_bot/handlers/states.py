from aiogram.fsm.state import StatesGroup, State


class AdminMenu(StatesGroup):
    start = State()
    send_file = State()
    cancel_order = State()
