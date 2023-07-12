from aiogram.fsm.state import StatesGroup, State


class BotMenu(StatesGroup):
    user_menu = State()
    profile = State()
