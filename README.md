# Поздравления на карте

Python Telegram-бот принимает поздравления, сохраняет записи и медиа в Supabase. React/Vite-фронтенд показывает карту. В `scripts/` находятся ручные инструменты импорта; запуск приложения их не запускает.

## Установка и настройки

Нужны Python 3.9+ и Node.js 20+. Для бота:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r bot/requirements.txt
cp bot/.env.example bot/.env
```

Заполните `bot/.env`: Telegram token, адрес Supabase, серверный `SUPABASE_SERVICE_KEY` и адрес фронтенда. Серверный ключ может быть современным `sb_secret_…`; он не должен попадать во фронтенд или Git. В Supabase Python 2.16.0 устранена проверка, ограничивавшая ключи форматом JWT. Та же версия закреплена для ручных скриптов импорта.

Для фронтенда:

```sh
cd frontend
npm ci
cp .env.example .env
```

В `frontend/.env` укажите URL Supabase и публичный publishable key в `VITE_SUPABASE_ANON_KEY`. Имя переменной сохранено для совместимости. Все переменные `VITE_` доступны посетителю; серверный secret key здесь использовать нельзя. Файлы `.env` не коммитятся.

## Локальный запуск

Бот: из каталога `bot` запустите `python main.py` с активированным Python-окружением. Это запускает обычный Telegram polling; не запускайте вторую копию поверх production-бота.

Фронтенд: из `frontend` используйте `npm run dev`. Для production-сборки выполните `npm run build`, затем `PORT=4173 npm run start`.

## Проверки

```sh
python -m unittest discover -s bot/tests -v
cd frontend
npm run build
```

Python-тест создаёт настоящие Supabase SDK-клиенты с синтетическими secret, publishable и legacy JWT ключами. Сетевые запросы заблокированы; строки БД, файлы Storage и Telegram-сообщения не создаются. Vite-сборка проверяет фронтенд отдельно.

После деплоя владелец проверяет обычный сценарий: открытие карты и работу бота. Проверка конструктора SDK не заменяет проверку загрузки медиа и отображения поздравления.

## Railway

Оба сервиса используют GitHub `main`: корень бота `/bot`, фронтенда `/frontend`. Для бота установите переменные из `bot/.env.example`; для фронтенда — из `frontend/.env.example`. Команды запуска заданы в соответствующих `railway.json`.

После merge в `main` дождитесь успешного Railway build/deploy. Для прямого CLI-деплоя используйте чистый checkout этого же коммита и явно выбранные project/environment/service: `railway up --project <project-id> --environment <environment-id> --service <service-id>`.

Изменение публичного ключа требует **новой Vite-сборки**: одного изменения Railway-переменной или перезапуска прежнего образа недостаточно. Перед отключением legacy API keys нужно обновить бота, фронтенд и используемые ручные импорты. Эта версия сама не создаёт и не отзывает ключи, не меняет схему и данные Supabase. SQL-файлы в `scripts/` запускаются отдельно только при отдельной необходимости.

## Текущее ограничение

Исправление совместимости SDK должно попасть в upstream `main` до ротации production-ключей. Деплой этой ветки или смена Railway source на fork автоматически не выполняются.
