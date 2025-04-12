from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, Application, \
    MessageHandler, filters
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.environ.get("TOKEN")

# Функция команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Определить цветотип"]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await update.message.reply_text(
        "Привет! Пора заняться внешним видом.\n"
        "Для начала необходимо определить три параметра:\n"
        "- Твой цветотип\n"
        "- Форма головы\n"
        "- Тип фигуры",
        reply_markup=reply_markup
    )

# Функция для обработки нажатия "Определить цветотип"
async def handle_color_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Создаем новую клавиатуру с вариантами цветотипов
    color_types_keyboard = [
        ["Весна", "Лето"],
        ["Осень", "Зима"],
        ["Назад"]
    ]
    reply_markup = ReplyKeyboardMarkup(
        color_types_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await update.message.reply_text(
        "Выбери свой цветотип:",
        reply_markup=reply_markup
    )

# Функция для обработки выбора цветотипа
async def handle_color_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chosen_color = update.message.text
    if chosen_color in ["Весна", "Лето", "Осень", "Зима"]:
        await update.message.reply_text(
            f"Ты выбрал(a) {chosen_color}! Отличный выбор!",
            reply_markup=ReplyKeyboardRemove()  # Убираем клавиатуру
        )
    elif chosen_color == "Назад":
        await start(update, context)  # Возвращаемся в начало

def main():
    application = Application.builder().token(TOKEN).build()
    print('Бот запущен...')

    # Обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Text("Определить цветотип"), handle_color_type))
    application.add_handler(MessageHandler(filters.Text(["Весна", "Лето", "Осень", "Зима", "Назад"]), handle_color_choice))

    application.run_polling()

if __name__ == "__main__":
    main()