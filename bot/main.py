import os
import asyncio
from aiogram import Bot, Router, types, F
from aiogram.types import InputFile, ChatMemberUpdated
from aiogram.enums import ChatType
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command, CommandObject
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging
import time
import aiohttp
import re
import aiogram
from collections import defaultdict
from datetime import datetime, timedelta, date
import uvicorn
import json
import random
import requests
from vosk import Model, KaldiRecognizer
import wave
from pydub import AudioSegment
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()

# Включаем логирование
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Объект бота
storage = MemoryStorage()
token = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token)

model = Model("models/vosk-model-small-ru-0.22")

router = Router()
API_URL = os.getenv("API_URL")

# Загрузка списка пользователей и групп
joinedFile = open("joined.txt", "r")
joinedUsers = set()
for line in joinedFile:
    joinedUsers.add(line.strip())
joinedFile.close()

groupFile = open("group.txt", "r")
joinedGroups = set()
for line in groupFile:
    joinedGroups.add(line.strip())
groupFile.close()

async def send_broadcast(message: str):
    with open('joined.txt', 'r') as file:
        user_ids = file.readlines()

    for user_id in user_ids:
        try:
            await bot.send_message(chat_id=int(user_id.strip()), text=message)
            print(f"Сообщение отправлено пользователю с ID {user_id.strip()}")
        except Exception as e:
            print(f"Ошибка при отправке сообщения пользователю с ID {user_id.strip()}: {e}")

async def generate_with_ai(user_id: int, message: str) -> str:
    async with aiohttp.ClientSession() as session:
        payload = {
            "user_id": user_id,
            "message": message
        }
        try:
            async with session.post(f"{API_URL}generate-response", json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['response']
                logging.error(f"API error: {await resp.text()}")
                return None
        except Exception as e:
            logging.error(f"Connection error: {e}")
            return None

# Функция для распознавания аудио с помощью Vosk
def transcribe_audio(wav_filename: str) -> str:
    wf = wave.open(wav_filename, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() not in [8000, 16000]:
        raise ValueError("Аудиофайл должен быть моно, 16 бит, 8 или 16 кГц")

    rec = KaldiRecognizer(model, wf.getframerate())
    result = ""
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            result += res.get("text", "") + " "
    res = json.loads(rec.FinalResult())
    result += res.get("text", "")
    return result.strip()

@router.message(Command("start"))
async def start(message: types.Message):
    global username
    global userlastname
    global user_id
    global chat_id
    username = message.from_user.first_name
    userlastname = message.from_user.full_name
    nickname = message.from_user.username
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Если это личный чат, записываем user_id
    if message.chat.type == ChatType.PRIVATE:
        if not str(message.chat.id) in joinedUsers:
            joinedFile = open("joined.txt", "a")
            joinedFile.write(str(message.chat.id) + "\n")
            joinedUsers.add(message.chat.id)
            # URL эндпоинта
            url = "http://127.0.0.1:9999/join"

            # Данные для отправки (JSON-тело запроса)
            data = {
                "user_id": user_id  # Замените на нужный user_id (chat_id)
            }

            # Отправка POST-запроса
            response = requests.post(url, json=data)

            # Проверка ответа
            if response.status_code == 200:
                print("Запрос выполнен успешно!")
                print("Ответ сервера:", response.json())
            else:
                print("Ошибка при выполнении запроса:", response.status_code)
                print("Ответ сервера:", response.text)
    # Если это группа, записываем group_id
    elif message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        if not str(message.chat.id) in joinedGroups:
            groupFile = open("group.txt", "a")
            groupFile.write(str(message.chat.id) + "\n")
            joinedGroups.add(message.chat.id)

    await message.answer(f"Привет! Я бот для Мехмат ЮФУ.\nТы можешь мне задать любой интересующий вопрос 😊")
    print("first name:", username)
    print("last name:", userlastname)
    print("nickname:", nickname)
    print("user id:", user_id)
    print("бот запущен!")

# Обработчик добавления бота в группу
@router.chat_member()
async def on_chat_member_update(chat_member: ChatMemberUpdated):
    if chat_member.new_chat_member.status == "member":
        if not str(chat_member.chat.id) in joinedGroups:
            groupFile = open("group.txt", "a")
            groupFile.write(str(chat_member.chat.id) + "\n")
            joinedGroups.add(chat_member.chat.id)

# Обработчик текстовых сообщений
@router.message(F.text)
async def handle_message(message: types.Message):
    # Получаем username бота
    bot_username = (await bot.get_me()).username

    # Проверяем, упоминается ли бот в сообщении
    if message.chat.type != "private" and f"@{bot_username}" in message.text:
        # Убираем упоминание бота из текста сообщения
        question = message.text.replace(f"@{bot_username}", "").strip()

        # Если после удаления упоминания остался текст, обрабатываем его как вопрос
        if question:
            user_id = int(message.from_user.id)
            response = await generate_with_ai(user_id, question)
            
            if response:
                await message.reply(response)  # Отвечаем на сообщение с упоминанием
            else:
                await message.reply("Извините, произошла ошибка обработки запроса.")
        else:
            await message.reply("Вы упомянули меня, но не задали вопрос. 😊")
    
    # Обработка сообщений в личных чатах
    elif message.chat.type == "private":
        user_id = int(message.from_user.id)
        message_text = str(message.text)
        
        response = await generate_with_ai(user_id, message_text)
        
        if response:
            await message.answer(response)
        else:
            await message.answer("Извините, произошла ошибка обработки запроса.")

@router.message(F.voice)
async def handle_voice(message: types.Message):
    # Проверяем, что сообщение пришло не из группы или супергруппы
    if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return  # Игнорируем голосовые сообщения в группах

    # Получаем информацию о файле
    file_info = await bot.get_file(message.voice.file_id)
    file_path = file_info.file_path
    fname = os.path.basename(file_path).split('.')[0]  # Имя файла без расширения

    # Скачиваем файл
    doc = requests.get(f'https://api.telegram.org/file/bot{token}/{file_path}')
    with open(f'{fname}.oga', 'wb') as f:
        f.write(doc.content)

    # Конвертируем ogg в wav с помощью pydub
    audio = AudioSegment.from_ogg(f"{fname}.oga")
    
    # Устанавливаем параметры аудио: моно, 16 бит, 16 кГц
    audio = audio.set_channels(1)  # Моно
    audio = audio.set_sample_width(2)  # 16 бит
    audio = audio.set_frame_rate(16000)  # 16 кГц

    wav_filename = f"{fname}.wav"
    audio.export(wav_filename, format="wav")

    # Распознаем текст с помощью Vosk
    text = transcribe_audio(wav_filename)

    # Удаляем временные файлы
    os.remove(f"{fname}.oga")
    os.remove(wav_filename)

    if text:
        user_id = int(message.from_user.id)
        message_text = str(text)
        
        response = await generate_with_ai(user_id, message_text)
        
        if response:
            await message.answer(response)
        else:
            await message.answer("Извините, произошла ошибка обработки запроса")
    else:
        await message.answer("Не удалось распознать текст. Попробуйте ещё раз или отправьте текстовое сообщение")

async def main():
    logging.info("Запуск бота")
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    logging.info("Бот запущен!")
    asyncio.run(main())