import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

MESSAGES = {
    {'start':
        {
            'ru': "Если вы владелец клуба и хотите подключить это приложение — напишите @cl9bix.\n🎧 Если вы гость, просто отсканируйте QR-код в вашем клубе, чтобы перейти к голосованию за треки.",
            'en': "If you are a club owner and want to use this app — message @cl9bix.\n🎧 If you are a guest, simply scan the QR code in your club to start voting for tracks.",
            'ua': "Якщо ви власник клубу і хочете підключити цей застосунок — напишіть @cl9bix.\n🎧 Якщо ви гість — просто відскануйте QR-код, який знаходиться у вашому клубі, щоб перейти до голосування за треки."
        }
    }

}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    get_user = update.effective_user

    if not args:
        await update.message.reply_text(MESSAGES['start'][get_user.language_code])



app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))

app.run_polling()
