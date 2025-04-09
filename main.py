from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = '7533167948:AAGBrlpf1zMrN_WGWut64zM8oMSgt6F6KaI'


# Команда /menu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Информация", callback_data='info'),
            InlineKeyboardButton("Секрет", callback_data='secret'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выбери действие:", reply_markup=reply_markup)

# Обработка нажатий на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Обязательно подтверждаем callback
    data = query.data

    if data == "info":
        await query.edit_message_text("Это простой бот, созданный с огоньком 🔥")
    elif data == "secret":
        await query.edit_message_text("Секретное сообщение: жизнь будет приподносить неожиданные"
                                      "и приятные сюрпризы 🕺")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))

app.run_polling()
