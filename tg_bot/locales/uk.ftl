    hello =
    Вас вітає телеграм бот, який допоможе  з індексацією URL-адрес в Google.


main_menu_name = Головне меню


profile =
    Ваш профіль:
    Ім'я: { $username }
    Баланс: { $balance } монет

back_button = Назад

order =
    Для того, Щоб Вам замовити індексацію, потрібно відправити URL-адреси в форматі txt файлу або повідомленням.
    Приклад:
    https://soundcloud.com
    https://www.youtube.com
    1 url = 1 монета

confirm_order =
    Підтвердження замовлення

confirm_button = Підтвердити

money_hrn = Гривні
money_crypto = Кріптовалюта

on_cofrim = Ваше замовлення перевіряється адміністратором, очікуйте повідомлення від бота.
confrirm_by_user =
    ID замовлення: {$order_id}
    ID користувача: {$id}
    Кількість посилань: {$count_links}
    Посилання:
    https://soundcloud.com
    https://www.youtube.com

message_when_confirm_admin = Посилання індексуються, очікуйте завершення індексації від кількох годин до кількох днів

not_enough_balance = Недостатньо монет на рахунку. Будь ласка, поповніть баланс

on_confirm_sum =
    Сума до сплати: {$suma}
    Посилання на оплату: {$link}

less_than_10_links = Кількість посилань не може бути меншою ніж 10


undefined_type_document = Невідомий тип документу


button_order = 📦 Замовлення
button_profile = 👤 Профіль
button_deposit = 💰 Поповнити баланс
button_settings = ⚙️ Налаштування

message_order_not_found = Замовлення не знайдено

suma_to_deposit = Введіть скільки монет ви хочете поповнити. 1 монета = $0.20

pre_confirm_text =
    Кількість посилань: { $count }
    До сплати: { $count } монет

language_changed = Мова змінена на українську



pay_message =
    Сума до сплати: ${ $usd_amount }
    Кількість отриманих монет: 1 монета = $0.20
    Всього монет до зачислення: { $coins }
    Посилання на оплату: { $link }

pay_button = Оплатити

not_digit = Ви ввели не число! Спробуйте ще раз


dialogs-buttons-change_language = Змінити мову
dialogs-buttons-ukranian = Українська
dialogs-buttons-russian = Русский

enter_deposit_amount = Введіть суму монет для поповнення
choose_payment_method = Оберіть спосіб оплати
wayforpay = WayForPay
nowpayments = NowPayments

choose_crypto_currency = Оберіть криптовалюту


pay_message_crypto =
    Будь ласка, відправте не менше свої { $currency } на адресу нижче. Поповнюйте не менше вказаної суми.
    Ви будете повідомлені, коли платіж буде отриманий.

    🔎 Адреса: <code>{ $address }</code>
    💰 Сума: <code>{ $crypto_amount }</code>

amount_less_35 = Сума не може бути менше 35 монет для оплати криптовалютою

success_payment = Дякуємо за оплату! Ваші токени {$tx.tokens_num} додано до вашого облікового запису!

confirmed_by_payment = Ваш платіж підтверджено. {$tx.amount_points} балів додано на ваш рахунок