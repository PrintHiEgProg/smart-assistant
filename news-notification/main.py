import requests
from bs4 import BeautifulSoup
import pandas as pd
import hashlib
import time
import schedule
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import threading
import uvicorn
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()

# FastAPI часть
app = FastAPI()

# Модель для входных данных
class UserJoinRequest(BaseModel):
    user_id: str

# Эндпоинт для POST-запроса
@app.post("/join")
def join(user_request: UserJoinRequest):
    user_id = user_request.user_id

    # Записываем user_id в файл
    try:
        with open("joined.txt", "a") as file:
            file.write(f"{user_id}\n")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при записи в файл: {e}")

    # Возвращаем успешный ответ
    return {"message": f"User {user_id} joined successfully"}

# Функция для запуска FastAPI
def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=9999)

# Функция для отправки сообщения в Telegram
def send_telegram_notification(chat_id, text):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Уведомление отправлено в Telegram.")
    else:
        print(f"Ошибка при отправке уведомления: {response.status_code}")

# Парсер новостей
def get_news():
    url = 'https://sfedu.ru/press-center/newspage/1'  # URL страницы с новостями
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        news_links = soup.find_all('a', href=True)  # Ищем все ссылки

        news_data = []
        for link in news_links:
            href = link['href']
            # Фильтруем только ссылки на новости
            if href.startswith('/press-center/news/'):
                title = link.text.strip()
                full_link = "https://sfedu.ru" + href
                # Генерация уникального хэша для каждой новости
                news_hash = hashlib.md5((title + full_link).encode()).hexdigest()
                news_data.append({'title': title, 'link': full_link, 'hash': news_hash})

        return news_data
    else:
        print(f"Ошибка при запросе: {response.status_code}")
        return []

def check_for_updates():
    # Загрузка предыдущих данных
    try:
        old_news = pd.read_csv('news_data.csv')
        old_hashes = set(old_news['hash'])
    except FileNotFoundError:
        old_hashes = set()

    # Получение текущих новостей
    current_news = get_news()
    new_news = []

    for news in current_news:
        if news['hash'] not in old_hashes:
            new_news.append(news)
            # Печать заголовка и ссылки на новость
            print(f"Новая новость: {news['title']}")
            print(f"Ссылка: {news['link']}")
            print("-" * 50)  # Разделитель для удобства чтения

            # Отправка уведомления в Telegram
            try:
                # Чтение chat_id из файла joined.txt
                with open("joined.txt", "r") as file:
                    chat_ids = file.read().splitlines()

                # Отправка уведомления каждому пользователю
                for chat_id in chat_ids:
                    text = f"Новая новость!\n\n{news['title']}\nСмотри тут: {news['link']}"
                    send_telegram_notification(chat_id, text)
            except Exception as e:
                print(f"Ошибка при отправке уведомления: {e}")

    if new_news:
        # Сохранение новых данных
        new_news_df = pd.DataFrame(new_news)
        if not old_hashes:
            new_news_df.to_csv('news_data.csv', index=False)
        else:
            new_news_df.to_csv('news_data.csv', mode='a', header=False, index=False)
    else:
        print("Новых новостей нет.")

def run_parser():
    schedule.every(10).minutes.do(check_for_updates)  # Проверка каждые 10 минут

    while True:
        schedule.run_pending()
        time.sleep(1)

# Запуск обоих компонентов
if __name__ == "__main__":
    # Запуск FastAPI в отдельном потоке
    fastapi_thread = threading.Thread(target=run_fastapi)
    fastapi_thread.daemon = True  # Поток завершится при завершении основного потока
    fastapi_thread.start()

    # Запуск парсера в основном потоке
    print("Запуск системы отслеживания новостей и FastAPI сервера...")
    run_parser()