from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_user_menu() -> ReplyKeyboardMarkup:
    profile_button = KeyboardButton(text="👤 Профіль")
    orders_button = KeyboardButton(text="📦 Замовлення")
    refill_balance_button = KeyboardButton(text="💰 Поповнити баланс")
    settings_button = KeyboardButton(text="⚙️ Налаштування")

    return ReplyKeyboardMarkup(
        keyboard=[
            [profile_button, orders_button],
            [refill_balance_button, settings_button],
        ],
        resize_keyboard=True,
    )
