import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Open WebApp", web_app=WebAppInfo(url='https://next-track.fun'))]
    ]
    await update.message.reply_text(
        "Welcome to Next Track!", reply_markup=InlineKeyboardMarkup(keyboard)
    )

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))

app.run_polling()
