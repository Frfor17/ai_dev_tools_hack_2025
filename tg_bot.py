from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import tg_bot_config
import asyncio

# Обработчик команды /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("start")

# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower().strip()
    if text == "hello world":
        await update.message.reply_text("start")

# Главная функция запуска бота
def main():
    # Создаем приложение с токеном из конфига
    app = Application.builder().token(tg_bot_config.TOKEN).build()
    
    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    print("Бот запущен и ожидает сообщений...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

# Точка входа в программу
if __name__ == "__main__":
    main()