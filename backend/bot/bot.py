import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = "8399376497:AAFt0RfpefTQaSX8TAWoCCL0_V7Xi3-bvFw"
WEBAPP_URL = "https://9c199927d497.ngrok-free.app/"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Open WebApp", web_app=WebAppInfo(url=WEBAPP_URL))]
    ]
    await update.message.reply_text(
        "Welcome to Next Track!", reply_markup=InlineKeyboardMarkup(keyboard)
    )

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))

app.run_polling()
