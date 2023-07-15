from aiogram.fsm.state import StatesGroup, State


class BotMenu(StatesGroup):
    user_menu = State()
    profile = State()
    deposit_balance = State()


class Order(StatesGroup):
    get_url = State()
    confirm_url = State()


class WayForPay(StatesGroup):
    pass


class NowPayment(StatesGroup):
    available_methods = State()