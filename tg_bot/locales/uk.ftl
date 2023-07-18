hello =
    Вас вітає телеграм бот, який допоможе  з індексацією URL-адрес в Google.
    Головне меню за командою: /menu


main_menu_name = Головне меню

# TODO Look how variables are passed and make changes
profile =
    Ваш профіль:
    Username: { $username }
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


on_cofrim = Ваше замовлення перевіряється адміністратором, очікуйте повідомлення від бота.
confrirm_by_user =
    ID замовлення: $order_id
    ID користувача: $id
    Кількість посилань: $count_links
    Посилання:
    https://soundcloud.com
    https://www.youtube.com

message_when_confirm_admin = Посилання індексуються, очікуйте завершення індексації від кількох годин до кількох днів

not_enough_balance = Недостатньо монет на рахунку. Будь ласка, поповніть баланс

zero_links = Кількість посилань не може бути меньше 1

undefined_type_document = Невідомий тип документу

button_order = Замовлення
button_profile = Мій профіль
button_deposit = Поповнення балансу
button_settings = Налаштування

message_order_not_found = Замовлення не знайдено

# TODO: look how preformating text works. Then you use i18n.text().format(count=count)
pre_confirm_text = Кількість посилань: {{count}}\nДо сплати: {{count}} монет

language_changed = Мова змінена на українську