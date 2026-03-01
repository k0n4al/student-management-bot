import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import router as commands_router

# Настройка логгирования
logging.basicConfig(level=logging.INFO)

# Создаём бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Подключаем обработчики
dp.include_router(commands_router)


async def main():
    """Запуск бота"""
    logging.info("Запуск бота...")
    
    # Запускаем polling (бот слушает сообщения)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен")
