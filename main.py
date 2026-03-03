import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, ADMIN_ID
from handlers import commands_router, admin_router
from database import init_db, add_admin

# Настройка логгирования
logging.basicConfig(level=logging.INFO)

# Создаём бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Подключаем обработчики
dp.include_router(commands_router)
dp.include_router(admin_router)


async def main():
    # Запуск бота
    logging.info("Запуск бота...")

    # Инициализация базы данных
    await init_db()
    logging.info("База данных готова")
    
    # Добавляем админа из .env
    if ADMIN_ID:
        await add_admin(ADMIN_ID)
        logging.info(f"Админ добавлен: {ADMIN_ID}")

    # Запускаем polling (бот слушает сообщения)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен")
