from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.services.yookassa.payment import create_payment

from app.utils.func_for_handlers import BasketGroup


def basket_keyboard(groups: list[BasketGroup]) -> InlineKeyboardMarkup:
    """
    Создаёт inline-клавиатуру для управления корзиной пользователя.

    Для каждой группы элементов корзины добавляется кнопка удаления,
    передающая в callback_data идентификаторы всех связанных записей корзины.
    Также добавляются кнопки для перехода к оплате и возврата назад.

    Parameters
    ----------
    groups : list[BasketGroup]
        Список сгруппированных элементов корзины пользователя.
        Каждый объект `BasketGroup` должен содержать список идентификаторов
        элементов корзины (`basket_ids`), относящихся к одной группе.

    Returns
    -------
    InlineKeyboardMarkup
        Inline-клавиатура для отображения корзины и управления её содержимым
        в Telegram-боте.
    """
    keyboard = []

    for i, group in enumerate(groups, start=1):
        ids = ','.join(map(str, group.basket_ids))
        keyboard.append([
            InlineKeyboardButton(
                text=f'❌ Удалить {i}',
                callback_data=f'basket:delete:{ids}'
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text='💳 Купить',
            callback_data='basket:pay'
        ),
        InlineKeyboardButton(
            text='⬅️ Назад',
            callback_data='buy_proxy'
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def pay_in_basket(
    price: int | float,
    pay_url: str | None = None,
    pay_id: str | None = None
) -> tuple[InlineKeyboardMarkup, str, str]:
    """
    Создаёт inline-клавиатуру для оплаты содержимого корзины.

    Если ссылка на оплату и идентификатор платежа не переданы, функция
    инициализирует новый платёж через платёжный сервис и возвращает
    необходимые данные для последующей проверки статуса оплаты.

    Parameters
    ----------
    price : int | float
        Общая сумма оплаты в копейках.
    pay_url : str | None, optional
        URL для перехода к оплате. Если не указан, создаётся новый платёж.
    pay_id : str | None, optional
        Идентификатор платежа в платёжной системе. Если не указан,
        создаётся новый платёж.

    Returns
    -------
    tuple[InlineKeyboardMarkup, str, str]
        Кортеж из:
        - inline-клавиатуры с кнопками оплаты корзины,
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
                callback_data='iampayed:in_basket'
            )],
            [InlineKeyboardButton(
                text='⬅️ Назад',
                callback_data='return_from_pay_in_basket'
            )]
        ]
    )

    return inline_kb, pay_url, pay_id