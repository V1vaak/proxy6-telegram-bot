from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.services.yookassa.payment import create_payment


def count_and_period(count: int, period: int) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора количества прокси и периода аренды.

    Parameters
    ----------
    count : int
        Текущее количество выбранных прокси.
    period : int
        Текущий период аренды в днях.

    Returns
    -------
    InlineKeyboardMarkup
        Inline-клавиатура управления покупкой прокси.
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='➖', callback_data='count:dec'),
            InlineKeyboardButton(text=f'{count} шт.', callback_data='noop'),
            InlineKeyboardButton(text='➕', callback_data='count:inc'),
        ],
        [
            InlineKeyboardButton(text='➖', callback_data='period:dec'),
            InlineKeyboardButton(text=f'{period} дн.', callback_data='noop'),
            InlineKeyboardButton(text='➕', callback_data='period:inc'),
        ],
        [
            InlineKeyboardButton(text='💳 Купить сейчас', callback_data='buy:now'),
        ],
        [
            InlineKeyboardButton(text='🗑️ В корзину', callback_data='buy:add_to_basket'),
        ],
        [
            InlineKeyboardButton(
                text='⬅️ Назад',
                callback_data='return_to_select_country'
            )
        ]
    ])



def pay_now(
    price: int | float,
    pay_url: str | None = None,
    pay_id: str | None = None
) -> tuple[InlineKeyboardMarkup, str, str]:
    """
    Создаёт inline-клавиатуру для оплаты и инициализирует платёж при необходимости.

    Если ссылка на оплату и идентификатор платежа не переданы, функция
    создаёт новый платёж через платёжный сервис и возвращает данные
    для последующей проверки статуса оплаты.

    Parameters
    ----------
    price : int | float
        Сумма платежа в копейках.
    pay_url : str | None, optional
        URL для перехода к оплате. Если не указан, создаётся новый платёж.
    pay_id : str | None, optional
        Идентификатор платежа в платёжной системе. Если не указан,
        создаётся новый платёж.

    Returns
    -------
    tuple[InlineKeyboardMarkup, str, str]
        Кортеж из:
        - inline-клавиатуры с кнопками оплаты,
        - URL для перехода к оплате,
        - идентификатора платежа в платёжной системе.
    """
    if not pay_url or not pay_id:
        pay_url, pay_id = create_payment(price / 100)

    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f'💳 Оплатить {price / 100:.2f} ₽',
                url=pay_url
            )],
            [InlineKeyboardButton(
                text='Я оплатил ✅',
                callback_data='iampayed'
            )],
            [InlineKeyboardButton(
                text='⬅️ Назад',
                callback_data='return_from_pay'
            )]
        ]
    )

    return inline_kb, pay_url, pay_id