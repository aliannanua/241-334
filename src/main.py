import logging
import random
import re
import asyncio
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Включаем логирование (удобно для отладки)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

TOKEN = "7556122464:AAH-QF7sv6rt6u10X3CYKq1Y6OAHI02Uj9g"

# Обработка команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот-рандомайзер 🎲\nВ каком диапазоне вы хотите вывести число? (например: от 0 до 100)",
        reply_markup=ReplyKeyboardRemove()
    )

# Универсальный обработчик сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text.lower() == "старт":
        await start(update, context)

    elif text == "Новое число в том же диапазоне":
        last_range = context.user_data.get("last_range")
        if last_range:
            number = random.randint(last_range[0], last_range[1])
            await send_number_with_buttons(update, context, number)
        else:
            await update.message.reply_text("Сначала задайте диапазон.")

    elif text == "Задать новый диапазон":
        await update.message.reply_text("Хорошо! Укажите новый диапазон (например: от 10 до 500):")

    elif text == "Конец":
        await update.message.reply_text(
            "Рад был вам помочь! Если когда-нибудь снова понадобится случайное число — я всегда здесь.",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Старт")]], resize_keyboard=True)
        )

    else:
        # Попытка распознать диапазон
        min_val, max_val = parse_range(text)

        if min_val is not None and max_val is not None:
            if min_val > max_val:
                min_val, max_val = max_val, min_val
            if abs(max_val - min_val) > 1_000_000:
                await update.message.reply_text("Слишком большой диапазон. Ограничьте его до миллиона.")
                return

            number = random.randint(min_val, max_val)
            context.user_data["last_range"] = (min_val, max_val)
            await send_number_with_buttons(update, context, number)

        else:
            await update.message.reply_text(
                "Не удалось распознать диапазон. Пример: от 0 до 100, 0-100 ."
            )

# Отправка числа и кнопок
async def send_number_with_buttons(update, context, number):
    keyboard = [
        [KeyboardButton("Новое число в том же диапазоне")],
        [KeyboardButton("Задать новый диапазон")],
        [KeyboardButton("Конец")]
    ]
    await update.message.reply_text(
        f"🎲 Ваше число: {number}",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# Функция парсинга диапазона
def parse_range(text):
    text = text.lower().strip()

    # Используем регулярные выражения
    match = re.search(r"(\d+)\s*(?:до|-|–|—|по)\s*(\d+)", text)
    if match:
        return int(match.group(1)), int(match.group(2))

    return None, None

# Основной запуск
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    await app.run_polling()

# Для запуска в PyCharm
if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()

    asyncio.get_event_loop().run_until_complete(main())
