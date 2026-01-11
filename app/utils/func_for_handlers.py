from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.models import User, Proxy, Basket

from app.services.proxy6.engine import proxy_client
from app.services.proxy6.client import Proxy6Error
from app.services.proxy6.cache import get_price_cache, save_price_cache

from app.utils.constants import (COUNTRY_NAMES, COUNTRY_FLAGS, 
                                 PROXY_VERSION_MAP, PROXY_TYPE_MAP)


def get_profile_text(user: User) -> str:
    """
    Формирует текст профиля пользователя для отображения в Telegram-боте.

    В тексте отображаются:
    - Telegram ID пользователя
    - username (если указан)
    - имя и фамилия
    - дата регистрации
    - время, проведённое в системе (дни и часы)

    Parameters
    ----------
    user : User
        ORM-модель пользователя SQLAlchemy.

    Returns
    -------
    str
        Готовый HTML-текст для отправки или редактирования сообщения
        в Telegram-боте.
    """

    username = f'@{user.username}' if user.username else 'не указан'

    now = datetime.utcnow()
    delta = now - user.created_at

    days = delta.days
    hours = delta.seconds // 3600

    return (
        "<b>👤 ПРОФИЛЬ</b>\n\n"
        f"<b>🆔 ID:</b> <code>{user.tg_id}</code>\n"
        f"<b>👤 Юзернейм:</b> {username}\n"
        f"<b>📛 Имя:</b> {user.first_name or 'не указано'}\n"
        f"<b>📛 Фамилия:</b> {user.last_name or 'не указана'}\n"
        f"<b>📅 Дата регистрации:</b> {user.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        f"<b>⏳ В системе:</b> {days} дн. {hours} ч." 
    )


def get_proxy_list_text(proxies: list[Proxy]) -> str:
    """
    Формирует текстовое представление списка прокси для отображения пользователю
    в Telegram-боте.

    Каждая прокси выводится отдельным блоком с:
    - типом и версией прокси;
    - страной (с флагом);
    - количеством оставшихся дней до окончания;
    - строкой подключения в формате ``IP:PORT:LOGIN:PASSWORD``.

    Текст возвращается в HTML-формате и предназначен для использования
    в методах ``send_message`` / ``edit_text`` с ``parse_mode="HTML"``.

    Parameters
    ----------
    proxies : list[Proxy]
        Список объектов Proxy, принадлежащих пользователю.

    Returns
    -------
    str
        Готовый HTML-текст для отображения списка прокси.
        Если список пуст — возвращается сообщение-заглушка.
    """
    if not proxies:
        return (
            "<b>🔍 ВАШИ ПРОКСИ</b>\n\n"
            "📭 <i>У вас пока нет добавленных прокси.</i>\n\n"
        )

    header = (
        "<b>🔍 ВАШИ ПРОКСИ</b>\n\n"
        "📌 <b>Формат:</b>\n"
        "<code>IP:ПОРТ:ЛОГИН:ПАРОЛЬ</code>\n\n"
        "<i>Коснитесь строки с прокси, чтобы скопировать</i>\n\n"
    )

    now = datetime.utcnow()
    blocks = []

    for i, proxy in enumerate(proxies, 1):
        remaining = proxy.date_end - now
        seconds_left = max(int(remaining.total_seconds()), 0)
        days_left = seconds_left // 86400
        hours_left = ((seconds_left % 86400) // 3600)
        minutes_left = (seconds_left % 3600) // 60

        proxy_type = PROXY_TYPE_MAP.get(proxy.proxy_type, proxy.proxy_type)
        proxy_version = PROXY_VERSION_MAP.get(proxy.proxy_version, proxy.proxy_version)
        country = COUNTRY_NAMES.get(proxy.country, proxy.country.upper())
        flag = COUNTRY_FLAGS.get(proxy.country, '🏴')

        value = f"{proxy.ip}:{proxy.port}:{proxy.login}:{proxy.password}"

        blocks.append(
            f"[{i}] {proxy_type} | {proxy_version}\n"
            f"🌍 Страна: {flag}{country}\n"
            f"⏳ Осталось: {days_left} дн. {hours_left} ч. {minutes_left} м.\n" 
            f"<code>{value}</code>"
        )

    return header + '\n\n'.join(blocks)


def get_markup_contries(countries: list[str]) -> InlineKeyboardMarkup:
    """
    Формирует inline-клавиатуру со списком стран для выбора прокси.

    Для каждой страны создаётся кнопка с флагом и названием страны.
    Callback-данные имеют формат: ``country:<code>``.

    В конце клавиатуры добавляется кнопка возврата «Назад».

    Parameters
    ----------
    countries : list[str]
        Список кодов стран в формате ISO 3166-1 alpha-2
        (например: ``["ru", "us", "de"]``).

    Returns
    -------
    InlineKeyboardMarkup
        Inline-клавиатура для отправки или редактирования сообщения
        в Telegram-боте.

    Notes
    -----
    • Флаги стран берутся из словаря ``COUNTRY_FLAGS``  
    • Названия стран формируются через функцию ``get_country_name``  
    • Кнопки автоматически группируются по 3 в ряд
    """
    builder = InlineKeyboardBuilder()

    for code in countries:
        builder.button(
            text=f"{COUNTRY_FLAGS.get(code, '🏴')} {COUNTRY_NAMES.get(code, code.upper())}",
            callback_data=f"country:{code}"
        )

    builder.adjust(3)

    builder.row(
        InlineKeyboardButton(
            text='⬅️ Назад',
            callback_data='return_to_select_proxy_type'
        )
    )

    return builder.as_markup()


@dataclass
class BasketGroup:
    proxy_version: int
    proxy_type: str
    country: str
    count: int
    period: int
    basket_ids: list[int]


def group_basket_items(baskets: list[Basket]) -> list[BasketGroup]:
    """
    Группирует элементы корзины пользователя по параметрам прокси.

    Элементы корзины объединяются по следующим полям:
    - версии прокси (proxy_version)
    - типу прокси (proxy_type)
    - стране (country)
    - периоду аренды (period)

    Внутри каждой группы:
    - суммируется количество прокси (count)
    - сохраняется список ID строк корзины (basket_ids)

    Это позволяет:
    - корректно отображать корзину пользователю
    - покупать одинаковые прокси одним запросом к API
    - удалять связанные элементы корзины одной операцией

    Parameters
    ----------
    baskets : list[Basket]
        Список объектов корзины пользователя из базы данных.

    Returns
    -------
    list[BasketGroup]
        Список сгруппированных элементов корзины, где каждый объект
        содержит параметры прокси, суммарное количество и ID записей корзины.
    """

    grouped = defaultdict(lambda: {
        'count': 0,
        'period': 0,
        'basket_ids': []
    })

    for item in baskets:
        key = (item.proxy_version, item.proxy_type, item.country, item.period)
        grouped[key]['count'] += item.count
        grouped[key]['period'] = item.period
        grouped[key]['basket_ids'].append(item.id)

    result = []
    for (version, ptype, country, period), data in grouped.items():
        result.append(
            BasketGroup(
                proxy_version=version,
                proxy_type=ptype,
                country=country,
                count=data['count'],
                period=period,
                basket_ids=data['basket_ids']
            )
        )

    return result


async def calc_price_proxy6(
    *,
    proxy_version: int,
    count: int,
    period: int,
    session
) -> int:
    """
    Расчёт стоимости прокси через API Proxy6 с использованием кэша.

    Функция сначала пытается получить цену из базы данных (кэш),
    актуальный в течение 24 часов. Если кэш отсутствует или устарел,
    выполняется запрос к API Proxy6, после чего цена сохраняется
    в кэш для повторного использования.

    Parameters
    ----------
    proxy_version : int
        Версия прокси (например: IPv4 или IPv6).

    count : int
        Количество прокси.

    period : int
        Период аренды прокси (в днях).

    session : AsyncSession
        Асинхронная сессия SQLAlchemy для работы с базой данных.

    Returns
    -------
    int
        Стоимость в копейках.
        Возвращает ``0``, если произошла ошибка при запросе к API Proxy6.
    """
    cache = await get_price_cache(
        proxy_version=proxy_version,
        count=count,
        period=period,
        session=session
    )

    if cache and not cache.is_expired():
        return int(cache.price_rub * 100)

    try:
        price_rub = await proxy_client.get_price(
            count=count,
            period=period,
            version=proxy_version
        )
    except Proxy6Error:
        return 0

    await save_price_cache(
        proxy_version=proxy_version,
        count=count,
        period=period,
        price_rub=float(price_rub),
        session=session
    )

    return int(float(price_rub) * 100)


async def format_basket_proxies(
    baskets: list[Basket],
    session: AsyncSession
) -> tuple[str, int]:
    """
    Формирует текстовое представление корзины с прокси и рассчитывает итоговую стоимость.

    Прокси в корзине группируются по параметрам (версия, тип, страна, период),
    для каждой группы рассчитывается цена через API Proxy6 с использованием кэша.
    В конце формируется итоговая сумма по всем позициям.

    Parameters
    ----------
    baskets : list[Basket]
        Список объектов корзины пользователя.

    session : AsyncSession
        Асинхронная сессия SQLAlchemy для получения и кэширования цен.

    Returns
    -------
    tuple[str, int]
        Кортеж из двух элементов:

        - ``str`` — HTML-текст для отправки пользователю в Telegram.
        - ``int`` — общая стоимость корзины в копейках.

        Если корзина пуста, возвращается сообщение о пустой корзине
        и сумма ``0``.
    """

    if not baskets:
        return '🛒 <b>Ваша корзина пуста.</b>', 0

    groups = group_basket_items(baskets)

    lines = ['🛒 <b>Ваша корзина:</b>\n']
    total_price = 0

    for i, item in enumerate(groups, start=1):
        price = await calc_price_proxy6(
                proxy_version=item.proxy_version,
                count=item.count,
                period=item.period,
                session=session
            )


        total_price += price

        lines.append(
            f"<b>{i}️⃣ {PROXY_VERSION_MAP.get(item.proxy_version)} | "
            f"{PROXY_TYPE_MAP.get(item.proxy_type)} | {COUNTRY_FLAGS.get(item.country)}"
            f"{COUNTRY_NAMES.get(item.country)}</b>\n"
            f"   🔢 Кол-во: <b>{item.count}</b>\n"
            f"   ⏳ Период: <b>{item.period} дней</b>\n"
            f"   💰 Цена: <b>{price / 100:.2f} ₽</b>\n"
        )

    lines.append(
        f"\n<b>Итого:</b> 💳 <b>{total_price / 100:.2f} ₽</b>"
    )

    return "\n".join(lines), total_price