from typing import Literal

    
class TranslatorRunner:
    def get(self, path: str, **kwargs) -> str: ...
    
    @staticmethod
    def hello() -> Literal["""Вас вітає телеграм бот, який допоможе  з індексацією URL-адрес в Google.
Головне меню за командою: /menu"""]: ...

    @staticmethod
    def main_menu_name() -> Literal["""Головне меню"""]: ...

    @staticmethod
    def profile(*, username, balance) -> Literal["""Ваш профіль:
Username: { $username }
Баланс: { $balance } монет"""]: ...

    @staticmethod
    def back_button() -> Literal["""Назад"""]: ...

    @staticmethod
    def order() -> Literal["""Для того, Щоб Вам замовити індексацію, потрібно відправити URL-адреси в форматі txt файлу або повідомленням.
Приклад:
https://soundcloud.com
https://www.youtube.com
1 url = 1 монета"""]: ...

    @staticmethod
    def confirm_order() -> Literal["""Підтвердження замовлення"""]: ...

    @staticmethod
    def on_cofrim() -> Literal["""Ваше замовлення перевіряється адміністратором, очікуйте повідомлення від бота."""]: ...

    @staticmethod
    def confrirm_by_user() -> Literal["""ID замовлення: $order_id
ID користувача: $id
Кількість посилань: $count_links
Посилання:
https://soundcloud.com
https://www.youtube.com"""]: ...

    @staticmethod
    def message_when_confirm_admin() -> Literal["""Посилання індексуються, очікуйте завершення індексації від кількох годин до кількох днів"""]: ...

    @staticmethod
    def not_enough_balance() -> Literal["""Недостатньо монет на рахунку. Будь ласка, поповніть баланс"""]: ...

    @staticmethod
    def zero_links() -> Literal["""Кількість посилань не може бути меньше 1"""]: ...

    @staticmethod
    def undefined_type_document() -> Literal["""Невідомий тип документу"""]: ...

    @staticmethod
    def button_order() -> Literal["""Замовлення"""]: ...

    @staticmethod
    def button_profile() -> Literal["""Мій профіль"""]: ...

    @staticmethod
    def button_deposit() -> Literal["""Поповнення балансу"""]: ...

    @staticmethod
    def button_settings() -> Literal["""Налаштування"""]: ...

    @staticmethod
    def message_order_not_found() -> Literal["""Замовлення не знайдено"""]: ...

    @staticmethod
    def pre_confirm_text(*, count, count) -> Literal["""Кількість посилань: { $count }\nДо сплати: { $count } монет"""]: ...

    @staticmethod
    def language_changed() -> Literal["""Мова змінена на українську"""]: ...

