from telegram_bot.requests_handler import bot


bot.infinity_polling(timeout=10, long_polling_timeout=5)
