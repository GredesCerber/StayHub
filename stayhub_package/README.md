# StayHub

Система автоматизации работы отеля/хостела: управление бронированиями, гостями, номерами, услугами и платежами. Решение построено на базе FastAPI, SQLAlchemy, SQLite и Bootstrap и предназначено для учебных целей.

## Возможности

- **Управление номерами**: создание, редактирование, удаление номеров, контроль цен и доступности
- **Типы номеров**: создание собственного справочника с кодами, рекомендациями по вместимости и базовой цене
- **Управление гостями**: регистрация и хранение данных гостей
- **Бронирования**: создание и сопровождение заявок с проверкой доступности и автоматическим расчётом стоимости
- **Услуги**: настройка дополнительных сервисов (завтрак, прачечная, SPA и т.д.)
- **Услуги в бронировании**: добавление услуг к брони с учётом количества
- **Платежи**: учёт оплат с разными способами и статусами
- **Отчёты**: панели с показателями загрузки, доходов и статистики бронирований

## Технологии

- **Backend**: FastAPI (Python)
- **База данных**: SQLite + SQLAlchemy ORM
- **Frontend**: шаблоны Jinja2 и Bootstrap 5
- **Иконки**: Bootstrap Icons

## Структура проекта

```
├── app/
│   ├── __init__.py
│   ├── main.py              # Точка входа FastAPI-приложения
│   ├── database.py          # Настройки подключения к БД
│   ├── models/              # SQLAlchemy-модели
│   │   ├── room.py
│   │   ├── room_type.py
│   │   ├── guest.py
│   │   ├── service.py
│   │   ├── booking.py
│   │   ├── booking_service.py
│   │   └── payment.py
│   ├── schemas/             # Pydantic-схемы
│   │   ├── room.py
│   │   ├── room_type.py
│   │   ├── guest.py
│   │   ├── service.py
│   │   ├── booking.py
│   │   ├── booking_service.py
│   │   └── payment.py
│   ├── routes/              # API и web-маршруты
│   │   ├── rooms.py
│   │   ├── room_types.py
│   │   ├── guests.py
│   │   ├── services.py
│   │   ├── bookings.py
│   │   ├── booking_services.py
│   │   ├── payments.py
│   │   └── reports.py
│   ├── services/            # Бизнес-логика
│   │   ├── room_service.py
│   │   ├── room_type_service.py
│   │   ├── guest_service.py
│   │   ├── service_service.py
│   │   ├── booking_service.py
│   │   ├── payment_service.py
│   │   └── report_service.py
│   ├── templates/           # HTML-шаблоны Jinja2
│   │   ├── base/
│   │   ├── rooms/
│   │   ├── room_types/
│   │   ├── guests/
│   │   ├── bookings/
│   │   ├── services/
│   │   ├── payments/
│   │   └── reports/
│   └── static/              # Статические файлы (CSS)
├── seed_data.py             # Скрипт заполнения тестовыми данными
├── requirements.txt         # Зависимости Python
├── stayhub_launcher.bat     # Внутренний запускной скрипт (вызывается извне)
└── README.md
```

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/GredesCerber/StayHub.git
cd StayHub
```

2. Перейдите в пакет с исходниками:
```bash
cd stayhub_package
```

3. Создайте виртуальное окружение:
```bash
python -m venv venv
```

   - macOS/Linux (bash/zsh): `source venv/bin/activate`
   - Windows PowerShell: `./venv/Scripts/Activate.ps1`
   - Windows Command Prompt: `venv\Scripts\activate.bat`

   > Если PowerShell блокирует запуск, временно разрешите скрипт командой `Set-ExecutionPolicy -Scope Process RemoteSigned`, затем повторите активацию.

4. Установите зависимости:
```bash
pip install -r requirements.txt
```

5. (Опционально) заполните базу тестовыми данными:
```bash
python seed_data.py
```

6. Запустите приложение:
```bash
uvicorn app.main:app --reload
```

7. Откройте браузер и перейдите по адресам:
   - Веб-интерфейс: http://localhost:8000
   - Документация API: http://localhost:8000/docs

## Быстрый запуск (Windows)

`../StayHubStart.bat` — основной файл для запуска. Меню предлагает три действия: «Запустить сервер» (при необходимости создаёт `stayhub.db` и открывает браузер), «Заполнить базу» (повторно выполняет `seed_data.py`) и «Открыть базу» (интерактивная SQLite-консоль в отдельном окне, команда выхода — `.quit`).

`stayhub_launcher.bat` — внутренний скрипт пакета, который обеспечивает работу меню; открывается автоматически из главного файла и вручную запускать его не требуется.

## REST API

### Номера (Rooms)
- `GET /rooms/api` — список номеров
- `GET /rooms/api/{room_id}` — номер по идентификатору
- `POST /rooms/api` — создать номер
- `PUT /rooms/api/{room_id}` — обновить номер
- `DELETE /rooms/api/{room_id}` — удалить номер

### Типы номеров (Room Types)
- `GET /room-types/api` — список типов номеров
- `POST /room-types/api` — создать тип номера
- `PUT /room-types/api/{type_id}` — обновить тип номера
- `DELETE /room-types/api/{type_id}` — удалить тип номера

### Гости (Guests)
- `GET /guests/api` — список гостей
- `GET /guests/api/{guest_id}` — гость по идентификатору
- `POST /guests/api` — создать гостя
- `PUT /guests/api/{guest_id}` — обновить данные гостя
- `DELETE /guests/api/{guest_id}` — удалить гостя

### Бронирования (Bookings)
- `GET /bookings/api` — список броней
- `GET /bookings/api/{booking_id}` — бронь по идентификатору
- `GET /bookings/api/availability` — проверка доступности номеров
- `GET /bookings/api/{booking_id}/cost` — расчёт стоимости брони
- `POST /bookings/api` — создать бронь
- `PUT /bookings/api/{booking_id}` — обновить бронь
- `DELETE /bookings/api/{booking_id}` — удалить бронь

### Услуги (Services)
- `GET /services/api` — список услуг
- `GET /services/api/{service_id}` — услуга по идентификатору
- `POST /services/api` — создать услугу
- `PUT /services/api/{service_id}` — обновить услугу
- `DELETE /services/api/{service_id}` — удалить услугу

### Платежи (Payments)
- `GET /payments/api` — список платежей
- `GET /payments/api/{payment_id}` — платеж по идентификатору
- `POST /payments/api` — создать платеж
- `PUT /payments/api/{payment_id}` — обновить платеж
- `DELETE /payments/api/{payment_id}` — удалить платеж

### Отчёты (Reports)
- `GET /reports/api/summary` — сводная статистика
- `GET /reports/api/occupancy` — отчёт по загрузке

## Модели базы данных

### Room — Номер
- `id`: первичный ключ
- `room_number`: уникальный номер комнаты
- `room_type`: человеко-читаемый тип (например, «Одноместный стандарт»)
- `capacity`: максимальное число гостей
- `price_per_night`: цена за ночь
- `is_available`: признак доступности
- `description`: описание

### RoomType — Тип номера
- `id`: первичный ключ
- `code`: краткий код (латиница) для идентификации
- `name`: название типа
- `description`: произвольное описание
- `default_capacity`: рекомендуемая вместимость
- `default_price`: рекомендованная базовая цена за ночь

### Guest — Гость
- `id`: первичный ключ
- `first_name`: имя
- `last_name`: фамилия
- `email`: e-mail (уникальный)
- `phone`: телефон
- `address`: адрес
- `id_document`: документ удостоверения личности

### Booking — Бронирование
- `id`: первичный ключ
- `guest_id`: ссылка на гостя
- `room_id`: ссылка на номер
- `check_in_date`: дата заезда
- `check_out_date`: дата выезда
- `total_cost`: итоговая стоимость
- `status`: статус (в ожидании, подтверждено, отменено, завершено)

### Service — Услуга
- `id`: первичный ключ
- `name`: название
- `description`: описание
- `price`: стоимость
- `is_active`: активна ли услуга

### BookingService — Услуга в бронировании
- `id`: первичный ключ
- `booking_id`: ссылка на бронирование
- `service_id`: ссылка на услугу
- `quantity`: количество
- `subtotal`: промежуточная стоимость

### Payment — Платёж
- `id`: первичный ключ
- `booking_id`: ссылка на бронирование
- `amount`: сумма
- `payment_date`: дата платежа
- `payment_method`: способ (наличные, карта, перевод)
- `status`: статус (в ожидании, выполнен, возвращён)

## Лицензия

Проект распространяется для учебного использования.
