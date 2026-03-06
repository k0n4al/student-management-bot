import logging
from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from database import get_student, is_admin

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("profile"))
async def cmd_profile(message: Message, user_id: int = None):
    # Команда /profile - личный кабинет студента
    # Если user_id передан (из callback) - используем его, иначе берём из message
    telegram_id = user_id if user_id else message.from_user.id
    
    student = await get_student(telegram_id)
    
    # Логгируем что получили
    logger.info(f"Profile request for user {telegram_id}: student={student}")

    # Если студент найден - показываем профиль
    if student:
        profile_text = (
            f"Личный кабинет\n\n"
            f"ФИО: {student['full_name']}\n"
            f"Telegram ID: {student['telegram_id']}\n"
            f"ПК: {student['pc_code'] or 'не назначен'}\n"
            f"Телефон: {student['phone'] or 'не указан'}\n"
            f"GitLab: {student['gitlab_link'] or 'не указан'}\n"
            f"Задача: {student['task_text'] or 'нет задачи'}\n"
        )
        await message.answer(profile_text)
        return

    # Студента нет в базе
    admin_check = await is_admin(telegram_id)
    logger.info(f"User {telegram_id} is_admin={admin_check}")
    
    if admin_check:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Админ панель", callback_data="admin")],
            ]
        )
        await message.answer(
            f"{message.from_user.first_name}, вас нет в базе студентов.\n\n"
            f"Но у вас есть права администратора.",
            reply_markup=keyboard
        )
    else:
        await message.answer(
            f"{message.from_user.first_name}, у вас нет профиля в системе.\n\n"
            f"Обратитесь к администратору для создания профиля."
        )
