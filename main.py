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
    color_types_keyboard = [["Теплый", "Холодный"]]
    chat_id = update.effective_chat.id
    photo_path = "color_type.jpg"  # Укажите путь к файлу
    caption = "Вот наглядный пример как определить! 🌟"
    reply_markup = ReplyKeyboardMarkup(
        color_types_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=open(photo_path, "rb"),  # Открываем файл в бинарном режиме
        caption=caption,
        reply_markup=reply_markup
    )

# Функция для обработки выбора цветотипа
async def handle_color_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Создаем новую клавиатуру с вариантами цветотипов
    chosen_color = update.message.text
    await update.message.reply_text(f"Обычно людям с {chosen_color.lower()} типом кожы чаще"
                                        " улыбаются люди 😊")
    await update.message.reply_text("Теперь давай определим твой тпи фигуры"
                                    ", это достаточно прост. Необходимы: \n"
                                    "1. Зеркало\n"
                                    "2. Подсказка, которую прикрепила снизу")
    color_types_keyboard = [["Песочные часы"], ["Круг", "Квадрат"],
                             ["Перевернутый треугольник", " Треугольник"]]
    chat_id = update.effective_chat.id
    photo_path = "shape_type.jpeg"  # Укажите путь к файлу
    caption = "мы сейчас тут"
    reply_markup = ReplyKeyboardMarkup(
        color_types_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=open(photo_path, "rb"),  # Открываем файл в бинарном режиме
        caption=caption,
        reply_markup=reply_markup
    )



def main():
    application = Application.builder().token(TOKEN).build()
    print('Бот запущен...')

    # Обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Text("Определить цветотип"), handle_color_type))
    application.add_handler(MessageHandler(filters.Text(["Теплый", "Холодный"]), handle_color_choice))

    application.run_polling()

if __name__ == "__main__":
    main()