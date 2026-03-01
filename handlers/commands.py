from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Команда /start - приветствие"""
    await message.answer(
        f"Привет, {message.from_user.first_name}!\n\n"
        "Я бот для учёта студентов.\n"
        "Нажми /help чтобы узнать команды."
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Команда /help - справка"""
    await message.answer(
        "Справка по командам:\n\n"
        "/start - Запустить бота\n"
        "/help - Эта справка\n"
        "/profile - Мой профиль\n"
        "/admin - Админ панель (только админ)"
    )
