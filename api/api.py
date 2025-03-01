from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import httpx
import time
from datetime import datetime
from typing import Dict, List
import logging
import json
import os
from collections import defaultdict
from httpx import Client, Proxy
import requests
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()

# Настройка прокси
proxy_url = os.getenv("PROXY_URL")
proxies = {
    "http": proxy_url,
    "https": proxy_url
}

# Ваш API-ключ OpenAI
GPT_TOKEN = os.getenv("GPT_TOKEN")
# Эндпоинт OpenAI API
GPT_URL = os.getenv("GPT_URL")

app = FastAPI()
MAX_HISTORY_LENGTH = int(os.getenv("MAX_HISTORY_LENGTH"))

# Файл для хранения истории диалогов
HISTORY_FILE = os.getenv("HISTORY_FILE")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все источники
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы
    allow_headers=["*"],  # Разрешить все заголовки
)

# Словарь для хранения истории диалога
dialog_history = defaultdict(list)

# Загрузка истории диалогов из файла при запуске бота
def load_dialog_history():
    if not os.path.exists(HISTORY_FILE):
        logging.info("Файл истории диалогов не найден. Создан пустой файл.")
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump({}, file, ensure_ascii=False, indent=4)
        return {}

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            history = json.load(file)
            for user_id, messages in history.items():
                # Преобразуем строки времени обратно в объекты datetime
                dialog_history[int(user_id)] = [
                    (datetime.fromisoformat(msg[0]), msg[1]) for msg in messages
                ]
        logging.info("История диалогов загружена из файла.")
        return history
    except json.JSONDecodeError as e:
        logging.error(f"Ошибка при загрузке истории диалогов из файла: {e}")
        return {}
    except Exception as e:
        logging.error(f"Неизвестная ошибка при загрузке истории диалогов: {e}")
        return {}

# Сохранение истории диалогов в файл
def save_dialog_history():
    # Преобразуем объекты datetime в строки перед сохранением
    history_to_save = {
        user_id: [(msg[0].isoformat(), msg[1]) for msg in messages]
        for user_id, messages in dialog_history.items()
    }
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(history_to_save, file, ensure_ascii=False, indent=4)
        logging.info("История диалогов сохранена в файл.")
    except Exception as e:
        logging.error(f"Ошибка при сохранении истории диалогов в файл: {e}")

# Загрузка истории при запуске
load_dialog_history()

@app.post("/generate-response")
async def generate_response(data: dict = Body(...)):
    user_id = data.get("user_id")
    message = data.get("message")
    
    if not user_id or not message:
        raise HTTPException(status_code=400, detail="user_id и message обязательны")
    
    # Загружаем контекст
    context_data = load_dialog_history()
    current_time = datetime.now()
    dialog_history[user_id].append((current_time, f"Пользователь: {message}"))

    if len(dialog_history[user_id]) > MAX_HISTORY_LENGTH:
        dialog_history[user_id].pop(0)
        logging.info(f"История диалога для пользователя {user_id} обрезана до {MAX_HISTORY_LENGTH} сообщений.")

    context = "\n".join([msg for _, msg in dialog_history[user_id]])

    prompt = f"""
        Контекст предыдущих сообщений:
        {context}
        Вопрос пользователя: {message}
        """    

    start_time = time.time()
    
    # Инициализация переменной response_text
    response_text = "Произошла ошибка при обработке запроса."

    # Отправка POST-запроса
    try:
        # Заголовки запроса
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GPT_TOKEN}"
        }

        # Тело запроса
        data = {
            "model": "gpt-4",  # Указываем модель GPT-4
            "messages": [
                {"role": "system", "content": "Ты Умный ассистент ЮФУ. Отвечай кратко, но емко. Бери информацию с этого сайта https://sfedu.ru ты должен должен общаться на ты в дружелюбной и уважительной манере без бюрократии. Если спрашивают про расписание занятий переводи их по этой ссылке https://schedule.sfedu.ru"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7  # Уровень креативности (от 0 до 2)
        }
        response = requests.post(GPT_URL, headers=headers, json=data, proxies=proxies)
        response.raise_for_status()  # Проверка на ошибки HTTP
        result = response.json()
        response_text = result["choices"][0]["message"]["content"].strip()
        print("Ответ от GPT-4:", response_text)
    except requests.exceptions.HTTPError as e:
        print(f"Ошибка HTTP: {e}")
    except Exception as e:
        print(f"Ошибка: {e}")

    # Добавляем ответ модели в контекст
    dialog_history[user_id].append((current_time, f"Ассистент: {response_text}"))
    # Убираем префикс "Ассистент:" из ответа, если он есть
    if response_text.startswith("Ассистент:"):
        response_text = response_text.replace("Ассистент:", "").strip()

    # Сохраняем историю диалогов после каждого взаимодействия
    save_dialog_history()

    return {"response": response_text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=7270)