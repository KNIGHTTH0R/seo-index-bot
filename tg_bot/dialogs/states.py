from aiogram.fsm.state import StatesGroup, State


class BotMenu(StatesGroup):
    user_menu = State()
    profile = State()


class Order(StatesGroup):
    get_url = State()
    confirm_url = State()


class Payment(StatesGroup):
    available_method = State()
    suma_of_payment = State()


class WayForPay(StatesGroup):
    pass


class NowPayment(StatesGroup):
    available_methods = State()


class LanguageMenu(StatesGroup):
    menu = State()
