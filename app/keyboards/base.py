from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


start = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='👤 Мой профиль', callback_data='profile')],
    [InlineKeyboardButton(text='🔐 Мои прокси', callback_data='my_proxy')],
    [InlineKeyboardButton(text='🛒 Купить прокси', callback_data='buy_proxy'),
     InlineKeyboardButton(text='🔄 Продлить прокси', callback_data='prolong_proxy')],
    [InlineKeyboardButton(text='💬 Поддержка', callback_data='support')]
])

return_on_start = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⬅️ Назад на главную', callback_data='return_to_start')]
])


contacts = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='GitHub', url='https://github.com/V1vaak'), 
     InlineKeyboardButton(text='YouTube', url='https://www.youtube.com/@novikovyo')],
    [InlineKeyboardButton(text='⬅️ Назад на главную', callback_data='return_to_start')]
])

in_buy_proxy_after_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Выбрать прокси', callback_data='selected:buy')],
    [InlineKeyboardButton(text='Корзина🗑️', callback_data='selected:basket')],
    [InlineKeyboardButton(text='⬅️ Назад на главную', callback_data='return_to_start')]
])

select_proxy_version = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='IPv4🟢', callback_data='version:4')],
    [InlineKeyboardButton(text='IPv4 Shared🔵', callback_data='version:3')],  # ipv4_shared
    [InlineKeyboardButton(text='IPv6🟢', callback_data='version:6')],
    [InlineKeyboardButton(text='⬅️ Назад', callback_data='buy_proxy')]
])

select_proxy_type = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='HTTPS', callback_data='type:http')],
    [InlineKeyboardButton(text='SOCKS5', callback_data='type:socks')],
    [InlineKeyboardButton(text='⬅️ Назад', callback_data='return_to_select_proxy_version')]
])

after_added_proxy_at_basket = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔐 Мои прокси', callback_data='my_proxy')],
    [InlineKeyboardButton(text='Выбрать еще прокси', callback_data='selected:buy')],
    [InlineKeyboardButton(text='В корзину🗑️', callback_data='selected:basket')],
    [InlineKeyboardButton(text='⬅️ Назад на главную', callback_data='return_to_start')]
])

in_basket_if_no_proxy = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Выбрать прокси', callback_data='selected:buy')],
    [InlineKeyboardButton(text='⬅️ На главную', callback_data='return_to_start')]
])

after_buyed_proxy = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔐 Мои прокси', callback_data='my_proxy')],
    [InlineKeyboardButton(text='⬅️ Назад на главную', callback_data='return_to_start')]
])