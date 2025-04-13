# Импорт необходимых библиотек
import logging  # Для логирования работы бота
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove  # Компоненты Telegram API
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, \
    ConversationHandler  # Обработчики сообщений
import gspread  # Для работы с Google Sheets
from oauth2client.service_account import ServiceAccountCredentials  # Аутентификация в Google API
import random  # Для генерации случайных чисел (в демо-режиме)

# Настройка системы логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Формат логов
    level=logging.INFO  # Уровень логирования (INFO)
)
logger = logging.getLogger(__name__)  # Создание объекта логгера

# Константы состояний для машины состояний (FSM)
PHOTO, SHOULDERS, WAIST, HIPS = range(4)  # Соответствует 0, 1, 2, 3


# Функция подключения к Google Sheets
def connect_to_google_sheets():
    # Области доступа для Google API
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    # Аутентификация с использованием сервисного аккаунта
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    # Авторизация клиента
    client = gspread.authorize(creds)
    # Открытие конкретной таблицы по названию
    return client.open("Рекомендации по одежде").sheet1


# Инициализация подключения к таблице
sheet = connect_to_google_sheets()


# Обработчик команды /start
def start(update: Update, context: CallbackContext) -> None:
    # Создание клавиатуры с двумя кнопками
    reply_keyboard = [['Определить по фото', 'Ввести параметры']]

    # Отправка сообщения с клавиатурой
    update.message.reply_text(
        "Привет! Я помогу определить твой тип фигуры и дам рекомендации по одежде.\n"
        "Выбери способ определения:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
        # Автоматическое изменение размера кнопок
    )


# Начало ветки определения по фото
def request_photo(update: Update, context: CallbackContext) -> int:
    # Запрос фото у пользователя
    update.message.reply_text(
        "Отправь фото в полный рост в обтягивающей одежде (например, в леггинсах и топе).\n"
        "Лучше сделать фото на нейтральном фоне без лишних предметов.",
        reply_markup=ReplyKeyboardRemove()  # Убираем клавиатуру
    )
    # Устанавливаем состояние ожидания фото
    return PHOTO


# Обработка полученного фото
def process_photo(update: Update, context: CallbackContext) -> int:
    try:
        # В реальной реализации здесь должен быть анализ фото
        # В демо-версии просто выбираем случайный тип фигуры
        body_types = ["Прямоугольник", "Треугольник", "Перевернутый треугольник", "Круг", "Песочные часы"]
        body_type = random.choice(body_types)

        # Отправка рекомендаций
        send_recommendations(update, context, body_type)
        # Завершение диалога
        return ConversationHandler.END
    except Exception as e:
        # Логирование ошибки
        logger.error(f"Error processing photo: {e}")
        update.message.reply_text("Произошла ошибка при обработке фото. Попробуйте еще раз.")
        return ConversationHandler.END


# Начало ветки ввода параметров
def start_measurements(update: Update, context: CallbackContext) -> int:
    # Запрос обхвата плеч
    update.message.reply_text(
        "Введи обхват плеч в сантиметрах (измерь самую широкую часть):",
        reply_markup=ReplyKeyboardRemove()
    )
    # Установка состояния ожидания плеч
    return SHOULDERS


# Обработка введенных плеч
def process_shoulders(update: Update, context: CallbackContext) -> int:
    try:
        # Сохранение значения плеч в user_data
        context.user_data['shoulders'] = float(update.message.text)
        # Запрос обхвата талии
        update.message.reply_text("Теперь введи обхват талии в сантиметрах:")
        # Установка состояния ожидания талии
        return WAIST
    except ValueError:
        # Обработка нечислового ввода
        update.message.reply_text("Пожалуйста, введите число. Например: 95")
        # Повторное ожидание плеч
        return SHOULDERS


# Обработка введенной талии (аналогично плечам)
def process_waist(update: Update, context: CallbackContext) -> int:
    try:
        context.user_data['waist'] = float(update.message.text)
        update.message.reply_text("Теперь введи обхват бедер в сантиметрах:")
        return HIPS
    except ValueError:
        update.message.reply_text("Пожалуйста, введите число. Например: 85")
        return WAIST


# Обработка введенных бедер
def process_hips(update: Update, context: CallbackContext) -> int:
    try:
        # Сохранение бедер
        context.user_data['hips'] = float(update.message.text)

        # Получение всех параметров
        shoulders = context.user_data['shoulders']
        waist = context.user_data['waist']
        hips = context.user_data['hips']

        # Определение типа фигуры
        body_type = determine_body_type(shoulders, waist, hips)
        # Отправка рекомендаций
        send_recommendations(update, context, body_type)
        # Завершение диалога
        return ConversationHandler.END
    except ValueError:
        update.message.reply_text("Пожалуйста, введите число. Например: 100")
        return HIPS


# Функция определения типа фигуры по параметрам
def determine_body_type(shoulders, waist, hips):
    # Расчет соотношений параметров
    shoulder_hip_ratio = shoulders / hips
    waist_hip_ratio = waist / hips

    # Логика определения типа по соотношениям
    if 0.96 <= waist_hip_ratio <= 1.05 and 0.96 <= shoulder_hip_ratio <= 1.05:
        return "Прямоугольник"
    elif waist_hip_ratio < 0.75 and shoulder_hip_ratio < 0.85:
        return "Песочные часы"
    elif waist_hip_ratio > 0.85 and shoulder_hip_ratio < 0.9:
        return "Треугольник"
    elif shoulder_hip_ratio > 1.1:
        return "Перевернутый треугольник"
    else:
        return "Круг"


# Функция отправки рекомендаций
def send_recommendations(update: Update, context: CallbackContext, body_type: str):
    try:
        # Поиск строки с рекомендациями в таблице
        cell = sheet.find(body_type)
        # Получение всех значений строки
        row = sheet.row_values(cell.row)

        # Формирование сообщения с рекомендациями
        recommendations = (
            f"Ваш тип фигуры: {body_type}\n\n"
            f"Рекомендации:\n"
            f"• Нижнее белье: {row[1]}\n"
            f"• Юбки: {row[2]}\n"
            f"• Колготки: {row[3]}"
        )

        # Отправка сообщения пользователю
        update.message.reply_text(recommendations)
    except Exception as e:
        # Обработка ошибок при работе с таблицей
        logger.error(f"Error getting recommendations: {e}")
        update.message.reply_text("Не удалось получить рекомендации. Попробуйте позже.")


# Функция отмены диалога
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Диалог прерван. Начните заново с /start',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


# Основная функция
def main() -> None:
    # Создание объекта Updater с токеном бота
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN")

    # Получение диспетчера для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Создание обработчика диалогов
    conv_handler = ConversationHandler(
        entry_points=[  # Точки входа в диалог
            MessageHandler(Filters.regex('^Определить по фото$'), request_photo),
            MessageHandler(Filters.regex('^Ввести параметры$'), start_measurements)
        ],
        states={  # Состояния диалога
            PHOTO: [MessageHandler(Filters.photo, process_photo)],
            SHOULDERS: [MessageHandler(Filters.text & ~Filters.command, process_shoulders)],
            WAIST: [MessageHandler(Filters.text & ~Filters.command, process_waist)],
            HIPS: [MessageHandler(Filters.text & ~Filters.command, process_hips)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],  # Обработчик отмены
    )

    # Регистрация обработчиков
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(conv_handler)

    # Запуск бота
    updater.start_polling()  # Начало опроса сервера Telegram
    updater.idle()  # Ожидание новых сообщений


# Точка входа
if __name__ == '__main__':
    main()