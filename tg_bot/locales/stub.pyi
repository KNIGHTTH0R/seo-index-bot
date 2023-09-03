from typing import Literal

    
class TranslatorRunner:
    def get(self, path: str, **kwargs) -> str: ...
    
    dialogs: Dialogs

    @staticmethod
    def hello() -> Literal["""Вас приветствует телеграмм бот, который поможет с индексацией URL-адресов в Google."""]: ...

    @staticmethod
    def main_menu_name() -> Literal["""Главное меню"""]: ...

    @staticmethod
    def profile(*, username, balance) -> Literal["""Ваш профиль:
Имя: { $username }
Баланс: { $balance }$"""]: ...

    @staticmethod
    def on_confirm_sum(*, suma, link) -> Literal["""Сума к оплате: { $suma }
Ссылка на оплату: { $link }"""]: ...

    @staticmethod
    def back_button() -> Literal["""Назад"""]: ...

    @staticmethod
    def order(*, balance, count_urls) -> Literal["""Для того чтобы заказать индексацию, нужно отправить URL-адреса в формате txt файла или сообщением.
Пример:
https://soundcloud.com
https://www.youtube.com
1 url = 20 центов

Ваш текущий баланс: { $balance }$
Количество ссылок, которые доступны для вашего баланса: { $count_urls }"""]: ...

    @staticmethod
    def confirm_order() -> Literal["""Подтверждение заказа"""]: ...

    @staticmethod
    def confirm_button() -> Literal["""Подтвердить"""]: ...

    @staticmethod
    def money_hrn() -> Literal["""Гривны"""]: ...

    @staticmethod
    def money_crypto() -> Literal["""Криптовалюта"""]: ...

    @staticmethod
    def on_cofrim() -> Literal["""Ваш заказ проверяется администратором, ждите уведомления от бота."""]: ...

    @staticmethod
    def confrirm_by_user(*, order_id, id, count_links) -> Literal["""ID заказа: { $order_id }
ID пользователя: { $id }
Количество ссылок: { $count_links }
Ссылки:
https://soundcloud.com
https://www.youtube.com"""]: ...

    @staticmethod
    def message_confirm() -> Literal["""Ссылки индексируются, ожидайте завершения индексации от нескольких часов до нескольких дней"""]: ...

    @staticmethod
    def not_enough_balance() -> Literal["""Недостаточно денег на счету. Пожалуйста, пополните баланс"""]: ...

    @staticmethod
    def less_than_10_links() -> Literal["""Количество ссылок не может быть меньше 10"""]: ...

    @staticmethod
    def undefined_type_document() -> Literal["""Неизвестный тип документа"""]: ...

    @staticmethod
    def button_order() -> Literal["""📦 Индексация"""]: ...

    @staticmethod
    def button_tier() -> Literal["""📦 TIER-Ссылки"""]: ...

    @staticmethod
    def button_profile() -> Literal["""👤 Профиль"""]: ...

    @staticmethod
    def button_deposit() -> Literal["""💰 Пополнить баланс"""]: ...

    @staticmethod
    def button_settings() -> Literal["""⚙️ Настройки"""]: ...

    @staticmethod
    def suma_to_deposit() -> Literal["""Введите суму для пополнения. 1 ссылка = $0.20"""]: ...

    @staticmethod
    def pre_confirm_text(*, count, usdt_amount) -> Literal["""Количество ссылок: { $count }
К оплате: { $usdt_amount } $"""]: ...

    @staticmethod
    def message_order_not_found() -> Literal["""Заказ не найден"""]: ...

    @staticmethod
    def pay_message(*, usd_amount, link) -> Literal["""Сумма к оплате: { $usd_amount } $
Ссылка на оплату: { $link }"""]: ...

    @staticmethod
    def pay_button() -> Literal["""Оплатить"""]: ...

    @staticmethod
    def not_digits() -> Literal["""Вы ввели не число! Попробуйте еще раз"""]: ...

    @staticmethod
    def enter_deposit_amount() -> Literal["""Введите сумму в $ для пополнения"""]: ...

    @staticmethod
    def choose_payment_method() -> Literal["""Выберите метод платежа"""]: ...

    @staticmethod
    def wayforpay() -> Literal["""WayForPay"""]: ...

    @staticmethod
    def nowpayments() -> Literal["""NowPayments"""]: ...

    @staticmethod
    def language_changed() -> Literal["""Язык изменен на русский"""]: ...

    @staticmethod
    def choose_crypto_currency() -> Literal["""Выберите криптовалюту"""]: ...

    @staticmethod
    def pay_message_crypto(*, crypto_amount, currency, address, crypto_amount) -> Literal["""Пожалуйста, отправьте не менее { $crypto_amount } { $currency } на адрес ниже. Пополняйте не менее указанной суммы.
Вы будете уведомлены, когда платеж будет получен.

🔎 Адрес: &lt;code&gt;{ $address }&lt;/code&gt;
💰 Сумма: &lt;code&gt;{ $crypto_amount }&lt;/code&gt;"""]: ...

    @staticmethod
    def amount_less_35() -> Literal["""Сумма не может быть меньше 7 доларов для оплаты криптовалютой"""]: ...

    @staticmethod
    def confirmed_by_payment(*, amount) -> Literal["""Ваш платеж подтвержден. На ваш счет добавлено { $amount } $"""]: ...

    @staticmethod
    def min_deposit() -> Literal["""Сумма не может быть меньше 7$"""]: ...

    @staticmethod
    def select_package() -> Literal["""Выберите пакет:"""]: ...

    @staticmethod
    def when_selected(*, quantity, price, balance) -> Literal["""Вы выбрали пакет:

&lt;b&gt;{ $quantity }, его цена { $price }&lt;/b&gt;

Эта сумма будет списана с вашего счета.

На вашем счету: &lt;b&gt;${ $balance }&lt;/b&gt;

Продолжить 🤔?"""]: ...

    @staticmethod
    def send_info_tier() -> Literal["""Отправьте ссылки файлом или текстом"""]: ...

    @staticmethod
    def buyed_packeg(*, package) -> Literal["""Готово! Вы купили пакет: { $package }

Отправьте ссылки файлом или текстом в следующем сообщении"""]: ...

    @staticmethod
    def when_send() -> Literal["""Отлично! Ваши ссылки были отправлены менеджеру.

После обработки заказа вы получите файл"""]: ...

    @staticmethod
    def when_get_file() -> Literal["""Ваш заказ был принят в работу!
Ожидайте, выполнение заказа может занять до 12 дней"""]: ...

    @staticmethod
    def on_result() -> Literal["""Ваш заказ был выполнен! Отчет в этом файле"""]: ...

    @staticmethod
    def yes() -> Literal["""Да"""]: ...

    @staticmethod
    def no() -> Literal["""Нет"""]: ...

    @staticmethod
    def decline() -> Literal["""Услуга была отменена"""]: ...


class Dialogs:
    buttons: DialogsButtons


class DialogsButtons:
    @staticmethod
    def change_language() -> Literal["""Изменить язык"""]: ...

    @staticmethod
    def ukranian() -> Literal["""Українська"""]: ...

    @staticmethod
    def russian() -> Literal["""Русский"""]: ...

