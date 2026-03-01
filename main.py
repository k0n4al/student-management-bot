import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def main():
    """Запуск бота"""
    logging.info("Бот запускается...")
    
    # Запуск polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен")
