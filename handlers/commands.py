from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    # Команда /start - приветствие
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Мой профиль", callback_data="profile")],
        ]
    )
    
    await message.answer(
        f"Привет, {message.from_user.first_name}!\n\n"
        "Я бот для учёта студентов.\n"
        "Нажми /help чтобы узнать команды.",
        reply_markup=keyboard
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    # Команда /help - справка
    await message.answer(
        "Справка по командам:\n\n"
        "/start - Запустить бота\n"
        "/help - Эта справка\n"
        "/profile - Мой профиль\n"
        "/schedule - Моё расписание\n"
        "/admin - Админ панель (только админ)"
    )


@router.callback_query(lambda c: c.data == "profile")
async def profile_callback(callback: CallbackQuery):
    # Кнопка Мой профиль под /start
    await callback.answer()  # Подтверждаем нажатие кнопки
    
    from handlers.profile import cmd_profile
    # Передаём callback.message, но профиль возьмёт callback.from_user.id
    await cmd_profile(callback.message, callback.from_user.id)
