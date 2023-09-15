hello = Вас приветствует телеграмм бот, который поможет с индексацией URL-адресов в Google.

main_menu_name = Главное меню
profile =
    Ваш профиль:
    Имя: {$username}
    Баланс: {$balance}$


on_confirm_sum =
    Сума к оплате: {$suma}
    Ссылка на оплату: {$link}

back_button = Назад

order =
    Для того чтобы заказать индексацию, нужно отправить URL-адреса в формате txt файла или сообщением.
    Пример:
    https://soundcloud.com
    https://www.youtube.com
    1 url = ${$price}

    Ваш текущий баланс: {$balance}$
    Количество ссылок, которые доступны для вашего баланса: {$count_urls}

confirm_order =
    Подтверждение заказа

confirm_button = Подтвердить

money_hrn = Гривны
money_crypto = Криптовалюта

on_cofrim = Ваш заказ проверяется администратором, ждите уведомления от бота.
confrirm_by_user =
    ID заказа: {$order_id}
    ID пользователя: {$id}
    Количество ссылок: {$count_links}
    Ссылки:
    https://soundcloud.com
    https://www.youtube.com

message_confirm = Ссылки индексируются, ожидайте завершения индексации от нескольких часов до нескольких дней
not_enough_balance = ❌ Недостаточно денег на счету. Пожалуйста, пополните баланс
less_than_1_links = ❌ Количество ссылок не может быть меньше 1
undefined_type_document = ❌ Неизвестный тип документа

button_order = 📦 Индексация
button_tier = 📦 TIER-Ссылки
button_profile = 👤 Профиль
button_deposit = 💰 Пополнить баланс
button_settings = ⚙️ Настройки

suma_to_deposit = Введите суму для пополнения. 1 ссылка = ${$price}

pre_confirm_text =
    Количество ссылок: { $count }
    К оплате: { $usdt_amount } $

message_order_not_found = Заказ не найден



pay_message =
    Сумма к оплате: { $usd_amount } $
    Ссылка на оплату: { $link }

pay_button = Оплатить

not_digits = Вы ввели не число! Попробуйте еще раз


dialogs-buttons-change_language = Изменить язык
dialogs-buttons-ukranian = Українська
dialogs-buttons-russian = Русский

enter_deposit_amount = Введите сумму в $ для пополнения
choose_payment_method = Выберите метод платежа
wayforpay = WayForPay
nowpayments = NowPayments

language_changed = Язык изменен на русский
choose_crypto_currency = Выберите криптовалюту


pay_message_crypto =
    Пожалуйста, отправьте не менее { $crypto_amount } { $currency } на адрес ниже. Пополняйте не менее указанной суммы.
    Вы будете уведомлены, когда платеж будет получен.

    🔎 Адрес: <code>{ $address }</code>
    💰 Сумма: <code>{ $crypto_amount }</code>

amount_less_35 = Сумма не может быть меньше 7 доларов для оплаты криптовалютой

confirmed_by_payment = Ваш платеж подтвержден. На ваш счет добавлено {$amount} $


min_deposit = Сумма не может быть меньше 7$


select_package = Выберите пакет:

when_selected =
    Вы выбрали пакет:

    <b>{$package}, его цена ${$price}</b>

    Эта сумма будет списана с вашего счета.

    На вашем счету: <b>${$balance}</b>

    Продолжить 🤔?


send_info_tier = Отправьте ссылки текстом (до 15 штук). Если более 15, то отправьте файлом txt!


buyed_packeg =
    Готово! Вы выбрали пакет: {$package}

    Подтверждаете покупку?


when_send =
    Отлично! Ваши ссылки были отправлены менеджеру.

    После обработки заказа вы получите файл

when_get_file =
    Ваш заказ был принят в работу!
    Ожидайте, выполнение заказа может занять до 12 дней

on_result = Ваш заказ был выполнен! Отчет в этом файле


yes = Да
no = Нет

decline = Услуга была отменена


ref_button = Реферальная система

ref =
    Привет! 👋 У нас уже работает система рефералов, которая позволяет тебе получать бонусы за привлечение новых пользователей к нашему сервису.

    За каждую транзакцию по пополнению баланса, сделанную твоими рефералами, ты получаешь 8% от их суммы 💰

    На данный момент ты уже привлёк(ла) {$count_referrals} пользователей
    Получил {$count_money} денег от их транзакций!

    У тебя есть уникальная реферальная ссылка, по которой твой друг может присоединиться к нам 🔗

    Если твой друг зарегистрируется и пополнит баланс после перехода по этой ссылке, ты получишь 8% от суммы его пополнения.

    Не забывай приглашать еще больше друзей 🚀

    Твоя реферальная ссылка: {$referral_link}

notif_usr =
    Вы получили реферальное вознаграждение: {$referral_reward}$. 💰 Благодарим за поддержку нашего сервиса! 👍