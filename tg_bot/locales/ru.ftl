hello =
    Вас приветствует телеграмм бот, который поможет с индексацией URL-адресов в Google.
    Главное меню по команде: /menu

main_menu_name = Главное меню
profile =
    Ваш профиль:
    Имя: {$username}
    Баланс: {$balance}


on_confirm_sum =
    Сума к оплате: {$suma}
    Ссылка на оплату: {$link}

back_button = Назад

order =
    Для того чтобы заказать индексацию, нужно отправить URL-адреса в формате txt файла или сообщением.
    Пример:
    https://soundcloud.com
    https://www.youtube.com
    1 url = 1 монета

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

message_when_confirm_admin= Ссылки индексируются, ожидайте завершения индексации от нескольких часов до нескольких дней
not_enough_balance = Недостаточно монет на счету. Пожалуйста, пополните баланс
zero_links = Количество ссылок не может быть меньше 1
undefined_type_document = Неизвестный тип документа
button_order = Заказ
button_profile = Мой профиль
button_deposit = Пополнение баланса
button_settings = Настройка

suma_to_deposit = Введите сколько монет вы хотите пополнить. 1 монета = $0.05

pre_confirm_text =
    Количество ссылок: { $count }
    К оплате: { $count } монет

message_order_not_found = Заказ не найден



pay_message =
    Сумма к оплате: ${ $usd_amount }
    Количество полученных монет: 1 монета = $0.05
    Всего монет к зачислению: { $coins }
    Ссылка на оплату: { $link }

pay_button = Оплатить

not_digits = Вы ввели не число! Попробуйте еще раз


dialogs-buttons-change_language = Изменить язык
dialogs-buttons-ukranian = Українська
dialogs-buttons-russian = Русский

enter_deposit_amount = Введите сумму монет для пополнения
choose_payment_method = Выберите метод платежа
wayforpay = WayForPay
nowpayments = NowPayments

choose_crypto_currency = Выберите криптовалюту


pay_message_crypto =
    Пожалуйста, отправьте не менее { $crypto_amount } { $currency } на адрес ниже. Пополняйте не менее указанной суммы.
    Вы будете уведомлены, когда платеж будет получен.

    🔎 Адрес: <code>{ $address }</code>
    💰 Сумма: <code>{ $crypto_amount }</code>

amount_less_100 = Сумма не может быть меньше 100 монет для оплаты криптовалютой