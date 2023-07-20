from typing import Literal

    
class TranslatorRunner:
    def get(self, path: str, **kwargs) -> str: ...
    
    dialogs: Dialogs

    @staticmethod
    def hello() -> Literal["""Вас вітає телеграм бот, який допоможе  з індексацією URL-адрес в Google.
Головне меню за командою: /menu"""]: ...

    @staticmethod
    def main_menu_name() -> Literal["""Головне меню"""]: ...

    @staticmethod
    def profile(*, username, balance) -> Literal["""Ваш профіль:
Ім&#39;я: { $username }
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
    def confirm_button() -> Literal["""Підтвердити"""]: ...

    @staticmethod
    def money_hrn() -> Literal["""Гривні"""]: ...

    @staticmethod
    def money_crypto() -> Literal["""Кріптовалюта"""]: ...

    @staticmethod
    def on_cofrim() -> Literal["""Ваше замовлення перевіряється адміністратором, очікуйте повідомлення від бота."""]: ...

    @staticmethod
    def confrirm_by_user(*, order_id, id, count_links) -> Literal["""ID замовлення: { $order_id }
ID користувача: { $id }
Кількість посилань: { $count_links }
Посилання:
https://soundcloud.com
https://www.youtube.com"""]: ...

    @staticmethod
    def message_when_confirm_admin() -> Literal["""Посилання індексуються, очікуйте завершення індексації від кількох годин до кількох днів"""]: ...

    @staticmethod
    def not_enough_balance() -> Literal["""Недостатньо монет на рахунку. Будь ласка, поповніть баланс"""]: ...

    @staticmethod
    def on_confirm_sum(*, suma, link) -> Literal["""Сума до сплати: { $suma }
Посилання на оплату: { $link }"""]: ...

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
    def suma_to_deposit() -> Literal["""Введіть скільки монет ви хочете поповнити. 1 монета = $0.05"""]: ...

    @staticmethod
    def pre_confirm_text(*, count, count) -> Literal["""Кількість посилань: { $count }
До сплати: { $count } монет"""]: ...

    @staticmethod
    def language_changed() -> Literal["""Мова змінена на українську"""]: ...

    @staticmethod
    def pay_message(*, usd_amount, coins, link) -> Literal["""Сума до сплати: ${ $usd_amount }
Кількість отриманих монет: 1 монета = $0.05
Всього монет до зачислення: { $coins }
Посилання на оплату: { $link }"""]: ...

    @staticmethod
    def pay_button() -> Literal["""Оплатити"""]: ...

    @staticmethod
    def not_digit() -> Literal["""Ви ввели не число! Спробуйте ще раз"""]: ...

    @staticmethod
    def enter_deposit_amount() -> Literal["""Введіть суму монет для поповнення"""]: ...

    @staticmethod
    def choose_payment_method() -> Literal["""Оберіть спосіб оплати"""]: ...

    @staticmethod
    def wayforpay() -> Literal["""WayForPay"""]: ...

    @staticmethod
    def nowpayments() -> Literal["""NowPayments"""]: ...

    @staticmethod
    def choose_crypto_currency() -> Literal["""Оберіть криптовалюту"""]: ...

    @staticmethod
    def pay_message_crypto(*, usd_amount, currency, address, crypto_amount) -> Literal["""Будь ласка, відправте не менше &lt;b&gt;{ $usd_amount } { $currency }&lt;/b&gt; на адресу нижче.
Ви будете повідомлені, коли платіж буде отриманий.

🔎 Адреса: &lt;code&gt;{ $address }&lt;/code&gt;\n
💰 Сума: &lt;code&gt;{ $crypto_amount }&lt;/code&gt;\n\n"""]: ...


class Dialogs:
    buttons: DialogsButtons


class DialogsButtons:
    @staticmethod
    def ukranian() -> Literal["""Українська"""]: ...

    @staticmethod
    def russian() -> Literal["""Русский"""]: ...

    @staticmethod
    def change_language() -> Literal["""Змінити мову"""]: ...

