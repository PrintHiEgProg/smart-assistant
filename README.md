# Проект: Умный ассистент ЮФУ

Этот проект представляет собой Telegram-бота, который использует OpenAI GPT-4 для ответов на вопросы пользователей. Бот также может распознавать голосовые сообщения и отправлять уведомления о новых новостях с сайта ЮФУ.


## Описание файлов


### `api/api.py`
FastAPI-приложение, которое обрабатывает запросы к OpenAI GPT-4 и управляет историей диалогов.

- **Функции:**
  - `generate_response`: Генерирует ответ на вопрос пользователя с помощью GPT-4.
  - `load_dialog_history`: Загружает историю диалогов из файла.
  - `save_dialog_history`: Сохраняет историю диалогов в файл.

- **Зависимости:**
  - `fastapi`: Для создания API.
  - `openai`: Для взаимодействия с OpenAI API.
  - `httpx`: Для HTTP-запросов.
  - `python-dotenv`: Для загрузки переменных окружения из `.env`.


### `bot/main.py`
Основной файл Telegram-бота, который обрабатывает команды и сообщения от пользователей.

- **Функции:**
  - `start`: Обрабатывает команду `/start` и регистрирует пользователя.
  - `handle_message`: Обрабатывает текстовые сообщения и генерирует ответы с помощью GPT-4.
  - `handle_voice`: Обрабатывает голосовые сообщения, распознает текст и генерирует ответ.
  - `send_broadcast`: Отправляет сообщения всем зарегистрированным пользователям.
  - `generate_with_ai`: Отправляет запрос к API для генерации ответа.

- **Зависимости:**
  - `aiogram`: Для работы с Telegram API.
  - `vosk`: Для распознавания голосовых сообщений.
  - `pydub`: Для конвертации аудиофайлов.
  - `python-dotenv`: Для загрузки переменных окружения из `.env`.


### `parser/main.py`
Скрипт для парсинга новостей с сайта ЮФУ и отправки уведомлений в Telegram.

- **Функции:**
  - `get_news`: Парсит новости с сайта ЮФУ.
  - `check_for_updates`: Проверяет наличие новых новостей и отправляет уведомления.
  - `send_telegram_notification`: Отправляет уведомления в Telegram.
  - `run_fastapi`: Запускает FastAPI сервер для регистрации пользователей.

- **Зависимости:**
  - `requests`: Для HTTP-запросов.
  - `beautifulsoup4`: Для парсинга HTML.
  - `pandas`: Для работы с данными новостей.
  - `fastapi`: Для создания API.
  - `python-dotenv`: Для загрузки переменных окружения из `.env`.


## Установка и запуск


1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/ваш-username/ваш-репозиторий.git
   cd ваш-репозиторий
   ```

2. **Установите зависимости:**
	```bash
	pip install -r requirements.txt
    ```

3. **Создайте файл .env:** Создайте файл .env в корневой директории проекта и добавьте туда следующие переменные:
	```env
	GPT_TOKEN=ваш_токен_openai
	TELEGRAM_BOT_TOKEN=ваш_токен_telegram
	PROXY_URL=ваш_прокси
	API_URL=http://127.0.0.1:7270/
	HISTORY_FILE=dialog_history.json
	MAX_HISTORY_LENGTH=100
	```

4. **Запустите FastAPI сервер:**
	```bash
	cd api
	python api.py
	```

5. **Запустите Telegram-бота:**
	```bash
	cd bot
	python main.py
	```

6. **Запустите парсер новостей:**
	```bash
	cd parser
	python main.py
	```

## Использование


- **Telegram-бот:**
  - Отправьте команду `/start`, чтобы начать взаимодействие с ботом.  
  - Отправьте текстовое сообщение или голосовое сообщение, чтобы получить ответ от GPT-4.

- **Парсер новостей:**
  - Парсер автоматически проверяет новости каждые 10 минут и отправляет уведомления в Telegram.

#  made by envelope() ❤️
