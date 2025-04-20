from telegram import Update, ReplyKeyboardMarkup, MenuButtonCommands, BotCommand, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

import os
import gspread


# Настройки Google Sheets
SHEET_CREDENTIALS = 'credentials.json'  # Файл с ключами доступа
SHEET_URL = 'https://docs.google.com/spreadsheets/d/14dJ2Bv1QseBRtNbpygGZc0rHZXVzE55z_3Ji40yotNA/edit?gid=0#gid=0'

load_dotenv()
TOKEN = os.environ.get("TOKEN")

# Состояния диалога
(
    CHOOSING_COLOR,  # Выбор цветотипа
    CHOOSING_SHAPE,  # Выбор типа фигуры
    SHOWING_SKIRT,  # Показ юбок
    SHOWING_BLOUSE,  # Показ блузок
    SHOWING_JACKET,  # Показ курток
    FINAL_STEP  # Завершение
) = range(6)

# Словарь рекомендаций
CLOTHING_RECOMMENDATIONS = {
    "Песочные часы": {
        "skirt": {"photo": "hourglass_skirt.jpg", "text": "Юбка-карандаш подчеркнет вашу талию"},
        "blouse": {"photo": "hourglass_blouse.jpg", "text": "Приталенная блузка идеально подойдет"},
        "jacket": {"photo": "hourglass_jacket.jpg", "text": "Жакет с поясом подчеркнет пропорции"}
    },
    "Круг": {
        "skirt": {"photo": "round_skirt.jpg", "text": "Юбка А-силуэта визуально вытянет фигуру"},
        "blouse": {"photo": "round_blouse.jpg", "text": "Блузка с V-образным вырезом стройнит"},
        "jacket": {"photo": "round_jacket.jpg", "text": "Прямой жакет создаст стройный силуэт"}
    }
}


async def post_init(application):
    """Установка команд меню после инициализации бота"""
    commands = [
        BotCommand("start", "Начать диалог с ботом"),
        BotCommand("help", "Помощь по использованию бота"),
        BotCommand("reset", "Сбросить текущий диалог"),
        BotCommand("cancel", "Отменить текущее действие")
    ]
    await application.bot.set_my_commands(commands)
    await application.bot.set_chat_menu_button(menu_button=MenuButtonCommands())


async def is_user_allowed(user_id: int, username: str) -> bool:
    """Проверяет, есть ли пользователь в белом списке"""
    try:
        # Авторизация в Google Sheets
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(SHEET_CREDENTIALS, scope)
        client = gspread.authorize(creds)

        # Открытие таблицы
        sheet = client.open_by_url(SHEET_URL).sheet1
        users = sheet.get_all_records()

        # Проверка по ID или username
        for user in users:

            print("id = ", user_id, "  ", user.get('id', ''), "  ", username, "user = ", user)
            if  username.lower() == user.get('username', '').lower():
                return True
        return False
    except Exception as e:
        print(f"Ошибка проверки пользователя: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало диалога с проверкой доступа"""
    user = update.effective_user

    if not await is_user_allowed(user.id, user.username):
        await update.message.reply_text(
            "⛔ Извините, у вас нет доступа к этому боту.\n"
            "Обратитесь к администратору для добавления в белый список."
        )
        return ConversationHandler.END

    context.user_data.clear()
    keyboard = [["Определить цветотип"]]
    await update.message.reply_text(
        f"Привет, {user.first_name}! Я помогу подобрать одежду по вашему типу фигуры.",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return CHOOSING_COLOR


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показ помощи"""
    help_text = (
        "🤖 <b>Помощь по боту</b>\n\n"
        "Этот бот помогает подобрать одежду по вашему типу фигуры.\n"
        "Доступные команды:\n"
        "/start - начать диалог\n"
        "/help - эта справка\n"
        "/reset - сбросить текущий диалог\n"
        "/cancel - отменить текущее действие\n\n"
        "Просто следуйте инструкциям бота!"
    )
    await update.message.reply_html(help_text)


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сброс диалога"""
    context.user_data.clear()
    await update.message.reply_text(
        "Диалог сброшен. Начните заново с /start",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def handle_color_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора цветотипа"""
    await update.message.reply_text(
        "Выберите цветотип:",
        reply_markup=ReplyKeyboardMarkup([["Теплый", "Холодный"]], resize_keyboard=True)
    )
    return CHOOSING_COLOR


async def handle_color_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбранного цветотипа"""
    context.user_data['color_type'] = update.message.text
    await update.message.reply_text(
        "Теперь определим тип фигуры:",
        reply_markup=ReplyKeyboardMarkup(
            [["Песочные часы", "Круг"], ["Прямоугольник", "Треугольник"]],
            resize_keyboard=True
        )
    )
    return CHOOSING_SHAPE


async def handle_shape_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора типа фигуры"""
    shape = update.message.text
    context.user_data['shape_type'] = shape
    context.user_data['current_step'] = SHOWING_SKIRT
    return await show_recommendation(update, context)


async def show_recommendation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Показ рекомендаций по одежде с обработкой ошибок"""
    shape = context.user_data['shape_type']
    current_step = context.user_data['current_step']

    if current_step == SHOWING_SKIRT:
        item_type = "skirt"
        next_step = SHOWING_BLOUSE
    elif current_step == SHOWING_BLOUSE:
        item_type = "blouse"
        next_step = SHOWING_JACKET
    else:
        item_type = "jacket"
        next_step = FINAL_STEP

    recommendation = CLOTHING_RECOMMENDATIONS[shape][item_type]

    try:
        with open(recommendation["photo"], "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=recommendation["text"],
                reply_markup=ReplyKeyboardMarkup([["Дальше ➡️"]], resize_keyboard=True)
            )
    except FileNotFoundError:
        await update.message.reply_text(
            f"⚠️ Фото не найдено.\n{recommendation['text']}",
            reply_markup=ReplyKeyboardMarkup([["Дальше ➡️"]], resize_keyboard=True)
        )

    context.user_data['current_step'] = next_step  # Обновляем шаг заранее
    return current_step


async def handle_next_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка кнопки 'Дальше'"""
    current_step = context.user_data['current_step']

    if current_step == FINAL_STEP:
        await update.message.reply_text(
            "Рекомендации завершены! Используйте /start для нового диалога.",
            reply_markup=ReplyKeyboardRemove()
        )
        return FINAL_STEP

    return await show_recommendation(update, context)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена текущего действия"""
    await update.message.reply_text(
        'Действие отменено. Используйте /start для начала.',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main():
    """Основная функция запуска бота"""
    if not TOKEN:
        print("Ошибка: TOKEN не найден в .env!")
        return

    print("Бот запущен...")
    application = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

    # Обработчики команд
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(CommandHandler("cancel", cancel))

    # Обработчик диалога
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_COLOR: [
                MessageHandler(filters.Text("Определить цветотип"), handle_color_type),
                MessageHandler(filters.Text(["Теплый", "Холодный"]), handle_color_choice)
            ],
            CHOOSING_SHAPE: [
                MessageHandler(filters.Text(["Песочные часы", "Круг", "Прямоугольник", "Треугольник"]),
                               handle_shape_choice)
            ],
            SHOWING_SKIRT: [
                MessageHandler(filters.Text("Дальше ➡️"), handle_next_step)
            ],
            SHOWING_BLOUSE: [
                MessageHandler(filters.Text("Дальше ➡️"), handle_next_step)
            ],
            SHOWING_JACKET: [
                MessageHandler(filters.Text("Дальше ➡️"), handle_next_step)
            ]
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("start", start)  # Позволяет перезапустить диалог
        ]
    )
    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    main()