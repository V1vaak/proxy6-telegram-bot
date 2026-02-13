# 🤖 Proxy6 Telegram Bot

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Aiogram](https://img.shields.io/badge/aiogram-3.x-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)
![AIOSQLite](https://img.shields.io/badge/aiosqlite-0.20+-9cf.svg)
![Proxy6 API](https://img.shields.io/badge/Proxy6-API-orange.svg)
![Yookassa](https://img.shields.io/badge/yookassa-3.0+-brightgreen.svg)
![python-dotenv](https://img.shields.io/badge/python--dotenv-1.0+-ff69b4.svg)
![Docker](https://img.shields.io/badge/docker-✓-blue.svg?logo=docker)
![Docker Compose](https://img.shields.io/badge/compose-✓-2496ED.svg?logo=docker)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)
![GitHub last commit](https://img.shields.io/github/last-commit/V1vaak/PROXY6-Telegram-bot)

Telegram-бот для покупки прокси через сервис Proxy6 с интеграцией платежей ЮKassa. 

Проект полностью готов к деплою на сервер через **Docker Compose** 🐳

## 📋 Содержание
- [🔗 Полезные ссылки](#-полезные-ссылки)
- [🚀 Запуск](#-запуск)
- [📊 База данных](#-база-данных)
- [💳 Платежная система](#-платежная-система)
- [🏗️ Архитектура](#-архитектура)
- [🔧 Конфигурация](#-конфигурация)
- [📄 Лицензия](#-лицензия)

## 🔗 Полезные ссылки

#### Документация

- [📚 Документация Aiogram 3.x](https://docs.aiogram.dev/)
- [🌐 Proxy6 API Documentation](https://px6.me/ru/developers)
- [💳 ЮKassa API Documentation](https://yookassa.ru/developers/api)
- [🐍 SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/)

#### API ключи
- [Telegram Bot Token](https://t.me/BotFather)
- [Proxy6 API Key](https://px6.me/ru/user/developers)
- [ЮKassa Ключи](https://yookassa.ru/my/)



## 🚀 Полный запуск проекта на новом сервере (Ubuntu)

### 1️⃣ Обновление системы

```bash
sudo apt update && sudo apt upgrade -y
```

---

### 2️⃣ Установка Git

```bash
sudo apt install git -y
```

Проверка:

```bash
git --version
```

---

### 3️⃣ Установка Docker

#### Добавить GPG-ключ Docker

```bash
sudo apt update
sudo apt install ca-certificates curl -y
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

---

#### Добавить репозиторий Docker

```bash
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF
```

---

#### Установить Docker

```bash
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
```

---


Проверка:

```bash
sudo docker --version
sudo docker compose version
```


### 4️⃣ Клонировать репозиторий

```bash
git clone https://github.com/V1vaak/proxy6-telegram-bot.git
cd proxy6-telegram-bot
```

---

### 5️⃣ Создать файл окружения

Создайте `.env` на основе шаблона:

```bash
cp .env.example .env
```

Откройте файл и заполните переменные:

```env
PROXY6_API_KEY=your_proxy6_api_key
YOOKASSA_API_KEY=your_yookassa_api_key
YOOKASSA_SHOP_ID=your_shop_id

DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/proxydb
```

---

### 6️⃣ Запуск через Docker Compose

```bash
sudo docker compose up -d --build
```

Флаг `-d` запускает контейнеры в фоне.

---

### 7️⃣ Проверка логов

```bash
sudo docker compose logs -f
```

---

### 8️⃣ Остановка проекта

```bash
sudo docker compose down
```

---

## 🐳 Что запускается

* `bot` — Python приложение
* `db` — PostgreSQL 15
* Данные базы сохраняются в Docker volume `postgres_data`




## <img src="image_for_readme/image_bd.png" width="40" height="40" alt="" style="margin-bottom: -8px;"> База данных

**PostgreSQL** + **asyncpg** + **SQLAlchemy**

### **Модели (SQLAlchemy ORM)**
- **[👤 User](app/database/models.py#L16)** — данные пользователей Telegram
- **[🔌 Proxy](app/database/models.py#L25)** — купленные прокси 
- **[🛒 Basket](app/database/models.py#L46)** — товары в корзине перед оплатой
- **[💰 Spending](app/database/models.py#L68)** — история платежей и трат
- **[💾 PriceCache](app/database/models.py#L94)** — кэш цен от Proxy6 API


## <img src="image_for_readme/image_pay.png" width="40" height="40" alt="" style="margin-bottom: -12px;"> Платежная система

**ЮKassa** для обработки онлайн-платежей через официальную библиотеку [`yookassa`](https://pypi.org/project/yookassa/).

### 🔧 **Основные функции:**
- **[`create_payment()`](app/services/yookassa/payment.py#L11)** — создание платежной ссылки
- **[`get_status()`](app/services/yookassa/payment.py#L35)** — проверка статуса оплаты
- **[`cancel_payment()`](app/services/yookassa/payment.py#L43)** — отмена платежа
- **[`payment_confirmation()`](app/services/yookassa/payment.py#L47)** — ручное подтверждение


### <img src="image_for_readme/image_arch.png" width="50" height="40" alt="" style="margin-bottom: -8px;"> Архитектура

### **🗃️ База данных (`app/database/`)**

| Файл | Ссылка | Назначение |
|------|--------|------------|
| **Модели** | [`models.py`](app/database/models.py) | SQLAlchemy модели (User, Proxy, Basket, Spending) |
| **Движок БД** | [`engine.py`](app/database/engine.py) | Создание/удаление таблиц, сессии |
| **Запросы User** | [`orm_user.py`](app/database/queries/orm_user.py) | CRUD операции для пользователей |
| **Запросы Proxy** | [`orm_proxy.py`](app/database/queries/orm_proxy.py) | Прокси пользователей |
| **Запросы Basket** | [`orm_basket.py`](app/database/queries/orm_basket.py) | Корзина покупок |
| **Запросы Spending** | [`orm_spending.py`](app/database/queries/orm_spending.py) | История расходов |

### **🔗 Middleware (`app/middlewares/`)**

| Файл | Ссылка | Назначение |
|------|--------|------------|
| **База данных** | [`db.py`](app/middlewares/db.py) | Инъекция сессии БД в хендлеры |

### **🔌 Внешние сервисы (`app/services/`)**

#### **Proxy6 интеграция**
| Файл | Ссылка | Описание |
|------|--------|----------|
| **Клиент API** | [`client.py`](app/services/proxy6/client.py) | Синхронный и асинхронный клиенты Proxy6 |
| **Движок** | [`engine.py`](app/services/proxy6/engine.py) | Инициализация клиента |
| **Кэш** | [`cache.py`](app/services/proxy6/cache.py) | Кэширование стран и цен |

#### **ЮKassa платежи**
| Файл | Ссылка | Описание |
|------|--------|----------|
| **Оплата** | [`payment.py`](app/services/yookassa/payment.py) | Создание платежей, проверка статуса |



## <img src="image_for_readme/image_config.png" width="40" height="40" alt="" style="margin-bottom: -8px;"> Конфигурация

### Получение API ключей

1. **[Telegram Bot Token](https://t.me/BotFather)**
2. **[Proxy6 API Key](https://px6.me/ru/user/developers)**
3. **[ЮKassa Ключи](https://yookassa.ru/my/)**

### Файл `.env`
```env
# Обязательные поля
BOT_TOKEN=your_telegram_bot_token
PROXY6_API_KEY=your_proxy6_api_key
YOOKASSA_SHOP_ID=your_yookassa_shop_id
YOOKASSA_API_KEY=your_yookassa_secret_key

# Опционально
DATABASE_URL=sqlite+aiosqlite:///database.db
```


## <img src="image_for_readme/image_lic.png" width="40" height="40" alt="" style="margin-bottom: -8px;"> Лицензия

Распространяется под лицензией MIT. Подробнее см. в файле [`LICENSE`](LICENSE).


---

<div align="center">

**Разработано с ❤️ [V1vaak](https://github.com/V1vaak)**

[📧 Telegram](https://t.me/novikovyo) | [💻 GitHub](https://github.com/V1vaak) | [🚀 Другие проекты](https://github.com/V1vaak?tab=repositories)

</div>
