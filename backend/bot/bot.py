import asyncio, logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from dotenv import load_dotenv
load_dotenv()
import os
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

@dp.message(CommandStart(deep_link=True))
async def start(message: Message):
    payload = message.text.split(maxsplit=1)[-1].replace("/start", "").strip()
    if payload.startswith("event_"):
        token = payload[len("event_"):]
        url = f"https://your-host/webapp/index.html?start=event_{token}"
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Open Next Track", web_app=WebAppInfo(url=url))
        ]])
        await message.answer("Open WebApp to vote 👇", reply_markup=kb)
    else:
        await message.answer("Send me a QR from the club to join the event.")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
