import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor

TOKEN = "7924710982:AAGYVLo7_XcS2yxYiVdOEnrGZpBhwXFTw8U"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Словник для збереження вільних та зайнятих користувачів
free_users = set()
active_chats = {}

@dp.message_handler(commands=['start'])
async def start(message: Message):
    await message.answer("Вітаю! Це анонімний чат. Надішліть /find для пошуку співрозмовника.")

@dp.message_handler(commands=['find'])
async def find_chat_partner(message: Message):
    user_id = message.from_user.id
    if user_id in active_chats:
        await message.answer("Ви вже знаходитесь у чаті! Вийдіть з нього командою /stop.")
        return
    
    if free_users:
        partner_id = free_users.pop()
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id
        await bot.send_message(partner_id, "Знайдено співрозмовника! Почніть спілкування.")
        await bot.send_message(user_id, "Знайдено співрозмовника! Почніть спілкування.")
    else:
        free_users.add(user_id)
        await message.answer("Очікуйте, поки знайдеться співрозмовник...")

@dp.message_handler(commands=['stop'])
async def stop_chat(message: Message):
    user_id = message.from_user.id
    if user_id in active_chats:
        partner_id = active_chats.pop(user_id)
        del active_chats[partner_id]
        await bot.send_message(partner_id, "Співрозмовник вийшов з чату. Використовуйте /find для нового пошуку.")
        await message.answer("Ви вийшли з чату. Використовуйте /find для нового пошуку.")
    elif user_id in free_users:
        free_users.remove(user_id)
        await message.answer("Ви скасували пошук.")
    else:
        await message.answer("Ви не перебуваєте у чаті.")

@dp.message_handler()
async def relay_message(message: Message):
    user_id = message.from_user.id
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        await bot.send_message(partner_id, message.text)
    else:
        await message.answer("Ви не у чаті. Використовуйте /find для пошуку співрозмовника.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
    
