from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import is_admin, add_admin, get_all_students, add_student, update_student_pc

router = Router()


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    # Команда /admin - админ панель
    # Проверяем является ли админом
    if not await is_admin(message.from_user.id):
        await message.answer("У вас нет прав администратора.")
        return
    
    # Создаём кнопки админки
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Добавить студента", callback_data="admin_add_student")],
            [InlineKeyboardButton(text="Список студентов", callback_data="admin_list_students")],
            [InlineKeyboardButton(text="Назначить ПК", callback_data="admin_set_pc")],
        ]
    )
    
    await message.answer("Админ панель:", reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "admin_add_student")
async def admin_add_student_callback(callback: CallbackQuery):
    # Кнопка - добавить студента
    await callback.message.answer("Введите ФИО студента:")


@router.callback_query(lambda c: c.data == "admin_list_students")
async def admin_list_students_callback(callback: CallbackQuery):
    # Кнопка - список студентов
    students = await get_all_students()
    if not students:
        await callback.message.answer("Список студентов пуст.")
        return
    
    text = "Список студентов:\n\n"
    for s in students:
        text += f"• {s['full_name']} (ПК: {s['pc_code'] or 'не назначен'})\n"
    
    await callback.message.answer(text)


@router.callback_query(lambda c: c.data == "admin_set_pc")
async def admin_set_pc_callback(callback: CallbackQuery):
    # Кнопка - назначить ПК
    await callback.message.answer("Введите Telegram ID студента и номер ПК (пример: 123456789 АТ0012345):")
