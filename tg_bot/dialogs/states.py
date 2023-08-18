from aiogram.fsm.state import StatesGroup, State


class BotMenu(StatesGroup):
    user_menu = State()
    profile = State()


class Order(StatesGroup):
    get_url = State()
    confirm_url = State()


class Payment(StatesGroup):
    deposit_amount = State()
    available_method = State()
    choose_crypto_currency = State()


class LanguageMenu(StatesGroup):
    menu = State()


class AdminMenu(StatesGroup):
    menu = State()
    id = State()
    suma = State()
    stats = State()