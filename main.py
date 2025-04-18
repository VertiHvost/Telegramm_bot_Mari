from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.environ.get("TOKEN")

# Состояния диалога
(
    CHOOSING_COLOR,  # Выбор цветотипа
    CHOOSING_SHAPE,  # Выбор типа фигуры
    SHOWING_SKIRT,  # Показ юбок
    SHOWING_BLOUSE,  # Показ блузок
    SHOWING_JACKET,  # Показ курток
    SHOWING_PANTS,   #Показ трусов
    FINAL_STEP  # Завершение
) = range()  # Создаем 6 состояний

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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало диалога, возвращаем первое состояние"""
    keyboard = [["Определить цветотип"]]
    await update.message.reply_text(
        "Привет! Пора заняться внешним видом.",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return CHOOSING_COLOR


async def handle_color_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора цветотипа, возвращаем то же состояние"""
    await update.message.reply_text(
        "Выберите цветотип:",
        reply_markup=ReplyKeyboardMarkup([["Теплый", "Холодный"]], resize_keyboard=True)
    )
    return CHOOSING_COLOR


async def handle_color_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбранного цветотипа, переходим к выбору фигуры"""
    context.user_data['color_type'] = update.message.text
    await update.message.reply_text(
        "Теперь определим тип фигуры:",
        reply_markup=ReplyKeyboardMarkup(
            [["Песочные часы", "Круг"], ["Прямоугольник", "Треугольник"]],
            resize_keyboard=True
        )
    )
    return CHOOSING_SHAPE  # Важно: возвращаем следующее состояние


async def handle_shape_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора типа фигуры, начинаем показ рекомендаций"""
    shape = update.message.text
    context.user_data['shape_type'] = shape
    context.user_data['current_step'] = SHOWING_SKIRT  # Начинаем с юбок
    return await show_recommendation(update, context)


async def show_recommendation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Общая функция показа рекомендаций"""
    shape = context.user_data['shape_type']
    current_step = context.user_data['current_step']

    # Определяем тип одежды для текущего шага
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
        await update.message.reply_photo(
            photo=open(recommendation["photo"], "rb"),
            caption=recommendation["text"],
            reply_markup=ReplyKeyboardMarkup([["Дальше ➡️"]], resize_keyboard=True)
        )
    except FileNotFoundError:
        await update.message.reply_text(
            recommendation["text"],
            reply_markup=ReplyKeyboardMarkup([["Дальше ➡️"]], resize_keyboard=True)
        )

    return current_step  # Возвращаем текущее состояние


async def handle_next_step(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка кнопки 'Дальше'"""
    current_step = context.user_data['current_step']

    if current_step == SHOWING_SKIRT:
        context.user_data['current_step'] = SHOWING_BLOUSE
    elif current_step == SHOWING_BLOUSE:
        context.user_data['current_step'] = SHOWING_JACKET
    else:
        await update.message.reply_text(
            "Рекомендации завершены!",
            reply_markup=ReplyKeyboardRemove()
        )
        return FINAL_STEP

    return await show_recommendation(update, context)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик отмены"""
    await update.message.reply_text(
        'Диалог прерван. Начните заново с /start',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main():
    print("Бот запущен...")
    application = ApplicationBuilder().token(TOKEN).build()

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
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()