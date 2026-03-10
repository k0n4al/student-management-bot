from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import is_admin, add_admin, get_all_students, add_student, update_student_pc, student_exists, pc_exists, delete_student, update_student_field, add_schedule, get_schedule
from states import AdminStates

router = Router()


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    # Команда /admin - админ панель
    # Проверяем является ли админом
    if not await is_admin(message.from_user.id):
        await message.answer("У вас нет прав администратора.")
        return

    # Создаём кнопки админки с кнопкой Назад
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Добавить студента", callback_data="admin_add_student")],
            [InlineKeyboardButton(text="Список студентов", callback_data="admin_list_students")],
            [InlineKeyboardButton(text="Назначить ПК", callback_data="admin_set_pc")],
            [InlineKeyboardButton(text="Редактировать студента", callback_data="admin_edit_student")],
            [InlineKeyboardButton(text="Удалить студента", callback_data="admin_delete_student")],
            [InlineKeyboardButton(text="Расписание", callback_data="admin_schedule")],
            [InlineKeyboardButton(text="Закрыть", callback_data="admin_close")],
        ]
    )

    await message.answer("Админ панель:", reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "admin_close")
async def admin_close_callback(callback: CallbackQuery):
    # Кнопка Закрыть
    await callback.message.delete()


@router.callback_query(lambda c: c.data == "admin_add_student")
async def admin_add_student_callback(callback: CallbackQuery, state: FSMContext):
    # Кнопка - добавить студента
    await callback.answer()  # Подтверждаем нажатие кнопки
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")],
        ]
    )
    await callback.message.answer("Введите Telegram ID студента (число):", reply_markup=keyboard)
    await state.set_state(AdminStates.waiting_for_student_id)


@router.callback_query(lambda c: c.data == "admin_cancel")
async def admin_cancel_callback(callback: CallbackQuery, state: FSMContext):
    # Кнопка Отмена - очищаем состояние и удаляем сообщение
    await state.clear()
    await callback.answer()
    await callback.message.delete()


@router.message(AdminStates.waiting_for_student_id)
async def process_student_id(message: Message, state: FSMContext):
    # Получаем ID студента
    student_id = message.text.strip()

    # Проверяем что это число
    if not student_id.isdigit():
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")],
            ]
        )
        await message.answer("Пожалуйста, введите корректный Telegram ID (число):", reply_markup=keyboard)
        return

    # Сохраняем ID во временное хранилище
    await state.update_data(student_id=int(student_id))
    await state.set_state(AdminStates.waiting_for_student_name)
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")],
        ]
    )
    await message.answer("Теперь введите ФИО студента:", reply_markup=keyboard)


@router.message(AdminStates.waiting_for_student_name)
async def process_student_name(message: Message, state: FSMContext):
    # Получаем ФИО
    full_name = message.text.strip()

    # Получаем ID из хранилища
    data = await state.get_data()
    student_id = data.get("student_id")

    # Добавляем студента в базу
    result = await add_student(student_id, full_name)
    
    if result:
        await message.answer(f"Студент {full_name} добавлен! ID: {student_id}")
    else:
        await message.answer(f"Студент с ID {student_id} уже существует!")
    
    await state.clear()


@router.callback_query(lambda c: c.data == "admin_list_students")
async def admin_list_students_callback(callback: CallbackQuery):
    # Кнопка - список студентов
    await callback.answer()  # Подтверждаем нажатие кнопки
    
    students = await get_all_students()
    if not students:
        await callback.message.answer("Список студентов пуст.")
        return

    text = "Список студентов:\n\n"
    for s in students:
        text += f"ФИО: {s['full_name']}\n"
        text += f"   Telegram ID: {s['telegram_id']}\n"
        text += f"   ПК: {s['pc_code'] or 'не назначен'}\n"
        text += f"   Телефон: {s['phone'] or 'не указан'}\n"
        text += f"   GitLab: {s['gitlab_link'] or 'не указан'}\n"
        text += f"   Redmine: {s['redmine_link'] or 'не указан'}\n"
        text += f"   Задача: {s['task_text'] or 'нет задачи'}\n"
        text += "\n"

    await callback.message.answer(text)


@router.callback_query(lambda c: c.data == "admin_set_pc")
async def admin_set_pc_callback(callback: CallbackQuery, state: FSMContext):
    # Кнопка - назначить ПК
    await callback.answer()  # Подтверждаем нажатие кнопки
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")],
        ]
    )
    await callback.message.answer("Введите Telegram ID студента:", reply_markup=keyboard)
    await state.set_state(AdminStates.waiting_for_pc_student_id)


@router.message(AdminStates.waiting_for_pc_student_id)
async def process_pc_student_id(message: Message, state: FSMContext):
    # Получаем ID студента
    student_id = message.text.strip()

    if not student_id.isdigit():
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")],
            ]
        )
        await message.answer("Пожалуйста, введите корректный Telegram ID (число):", reply_markup=keyboard)
        return

    await state.update_data(student_id=int(student_id))
    await state.set_state(AdminStates.waiting_for_pc_code)
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")],
        ]
    )
    await message.answer("Введите код ПК (например, АТ0012345):", reply_markup=keyboard)


@router.message(AdminStates.waiting_for_pc_code)
async def process_pc_code(message: Message, state: FSMContext):
    # Получаем код ПК
    pc_code = message.text.strip()

    # Получаем ID студента из хранилища
    data = await state.get_data()
    student_id = data.get("student_id")
    
    # Назначаем ПК студенту (с проверками)
    result = await update_student_pc(student_id, pc_code)

    await message.answer(result['message'])
    await state.clear()


# ========== РЕДАКТИРОВАНИЕ СТУДЕНТА ==========

@router.callback_query(lambda c: c.data == "admin_edit_student")
async def admin_edit_student_callback(callback: CallbackQuery, state: FSMContext):
    # Кнопка - редактировать студента
    await callback.answer()
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")],
        ]
    )
    await callback.message.answer("Введите ID студента которого хотите редактировать:", reply_markup=keyboard)
    await state.set_state(AdminStates.waiting_for_edit_student_id)


@router.message(AdminStates.waiting_for_edit_student_id)
async def process_edit_student_id(message: Message, state: FSMContext):
    student_id = message.text.strip()
    
    if not student_id.isdigit():
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")],
            ]
        )
        await message.answer("Введите корректный ID (число):", reply_markup=keyboard)
        return
    
    # Проверяем существует ли студент
    if not await student_exists(int(student_id)):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")],
            ]
        )
        await message.answer(f"Студент с ID {student_id} не найден!", reply_markup=keyboard)
        return
    
    await state.update_data(student_id=int(student_id))
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="ФИО", callback_data="edit_field_full_name")],
            [InlineKeyboardButton(text="ПК", callback_data="edit_field_pc_code")],
            [InlineKeyboardButton(text="Телефон", callback_data="edit_field_phone")],
            [InlineKeyboardButton(text="GitLab", callback_data="edit_field_gitlab_link")],
            [InlineKeyboardButton(text="Задача", callback_data="edit_field_task_text")],
            [InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")],
        ]
    )
    await message.answer("Выберите что хотите изменить:", reply_markup=keyboard)
    await state.set_state(AdminStates.waiting_for_edit_choice)


@router.callback_query(lambda c: c.data.startswith("edit_field_"))
async def process_edit_choice(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    field = callback.data.replace("edit_field_", "")
    await state.update_data(edit_field=field)
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")],
        ]
    )
    
    field_names = {
        'full_name': 'ФИО',
        'pc_code': 'ПК',
        'phone': 'Телефон',
        'gitlab_link': 'GitLab',
        'task_text': 'Задача'
    }
    
    await callback.message.answer(f"Введите новое значение для поля '{field_names.get(field, field)}':", reply_markup=keyboard)
    await state.set_state(AdminStates.waiting_for_edit_value)


@router.message(AdminStates.waiting_for_edit_value)
async def process_edit_value(message: Message, state: FSMContext):
    new_value = message.text.strip()
    data = await state.get_data()
    student_id = data.get('student_id')
    field = data.get('edit_field')

    result = await update_student_field(student_id, field, new_value)
    await message.answer(result['message'])
    
    # Не очищаем состояние, а возвращаемся к выбору поля
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="ФИО", callback_data="edit_field_full_name")],
            [InlineKeyboardButton(text="ПК", callback_data="edit_field_pc_code")],
            [InlineKeyboardButton(text="Телефон", callback_data="edit_field_phone")],
            [InlineKeyboardButton(text="GitLab", callback_data="edit_field_gitlab_link")],
            [InlineKeyboardButton(text="Redmine", callback_data="edit_field_redmine_link")],
            [InlineKeyboardButton(text="Задача", callback_data="edit_field_task_text")],
            [InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")],
        ]
    )
    await message.answer("Выберите что хотите изменить ещё:", reply_markup=keyboard)


# ========== УДАЛЕНИЕ СТУДЕНТА ==========

@router.callback_query(lambda c: c.data == "admin_delete_student")
async def admin_delete_student_callback(callback: CallbackQuery, state: FSMContext):
    # Кнопка - удалить студента
    await callback.answer()
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")],
        ]
    )
    await callback.message.answer("Введите ID студента которого хотите удалить:", reply_markup=keyboard)
    await state.set_state(AdminStates.waiting_for_delete_student_id)


@router.message(AdminStates.waiting_for_delete_student_id)
async def process_delete_student_id(message: Message, state: FSMContext):
    student_id = message.text.strip()
    
    if not student_id.isdigit():
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")],
            ]
        )
        await message.answer("Введите корректный ID (число):", reply_markup=keyboard)
        return
    
    # Проверяем существует ли студент
    if not await student_exists(int(student_id)):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")],
            ]
        )
        await message.answer(f"Студент с ID {student_id} не найден!", reply_markup=keyboard)
        return
    
    await state.update_data(delete_student_id=int(student_id))
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Да, удалить", callback_data="delete_confirm_yes")],
            [InlineKeyboardButton(text="Нет, отмена", callback_data="admin_cancel")],
        ]
    )
    await message.answer(f"Вы уверены что хотите удалить студента с ID {student_id}?", reply_markup=keyboard)
    await state.set_state(AdminStates.waiting_for_delete_confirm)


@router.callback_query(lambda c: c.data == "delete_confirm_yes")
async def process_delete_confirm(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    data = await state.get_data()
    student_id = data.get('delete_student_id')
    
    result = await delete_student(student_id)
    
    if result:
        await callback.message.answer(f"Студент с ID {student_id} удалён!")
    else:
        await callback.message.answer(f"Не удалось удалить студента с ID {student_id}")

    await state.clear()


# ========== РАСПИСАНИЕ ==========

@router.callback_query(lambda c: c.data == "admin_schedule")
async def admin_schedule_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Добавить запись", callback_data="schedule_add")],
            [InlineKeyboardButton(text="Посмотреть расписание", callback_data="schedule_view")],
            [InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")],
        ]
    )
    await callback.message.answer("Расписание:", reply_markup=keyboard)


@router.callback_query(lambda c: c.data == "schedule_add")
async def schedule_add_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")],
        ]
    )
    await callback.message.answer("Введите ID студента:", reply_markup=keyboard)
    await state.set_state(AdminStates.waiting_for_schedule_student_id)


@router.message(AdminStates.waiting_for_schedule_student_id)
async def process_schedule_student_id(message: Message, state: FSMContext):
    student_id = message.text.strip()
    
    if not student_id.isdigit():
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")],
            ]
        )
        await message.answer("Введите корректный ID (число):", reply_markup=keyboard)
        return
    
    if not await student_exists(int(student_id)):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")],
            ]
        )
        await message.answer(f"Студент с ID {student_id} не найден!", reply_markup=keyboard)
        return
    
    await state.update_data(student_id=int(student_id))
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Пн", callback_data="day_mon")],
            [InlineKeyboardButton(text="Вт", callback_data="day_tue")],
            [InlineKeyboardButton(text="Ср", callback_data="day_wed")],
            [InlineKeyboardButton(text="Чт", callback_data="day_thu")],
            [InlineKeyboardButton(text="Пт", callback_data="day_fri")],
            [InlineKeyboardButton(text="Сб", callback_data="day_sat")],
            [InlineKeyboardButton(text="Вс", callback_data="day_sun")],
            [InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")],
        ]
    )
    await message.answer("Выберите день недели:", reply_markup=keyboard)
    await state.set_state(AdminStates.waiting_for_schedule_day)


@router.callback_query(lambda c: c.data.startswith("day_"))
async def process_schedule_day(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    day_map = {
        'day_mon': 'Понедельник',
        'day_tue': 'Вторник',
        'day_wed': 'Среда',
        'day_thu': 'Четверг',
        'day_fri': 'Пятница',
        'day_sat': 'Суббота',
        'day_sun': 'Воскресенье'
    }
    
    day_code = callback.data.replace("day_", "")
    day_name = day_map.get(callback.data, day_code)
    
    await state.update_data(day_of_week=day_name)
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")],
        ]
    )
    await callback.message.answer(f"{day_name}. Введите время начала (например, 10:00):", reply_markup=keyboard)
    await state.set_state(AdminStates.waiting_for_schedule_start)


@router.message(AdminStates.waiting_for_schedule_start)
async def process_schedule_start(message: Message, state: FSMContext):
    start_time = message.text.strip()
    await state.update_data(start_time=start_time)
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")],
        ]
    )
    await message.answer("Введите время окончания (например, 12:00):", reply_markup=keyboard)
    await state.set_state(AdminStates.waiting_for_schedule_end)


@router.message(AdminStates.waiting_for_schedule_end)
async def process_schedule_end(message: Message, state: FSMContext):
    end_time = message.text.strip()
    data = await state.get_data()
    student_id = data.get('student_id')
    day_of_week = data.get('day_of_week')
    start_time = data.get('start_time')
    
    result = await add_schedule(student_id, day_of_week, start_time, end_time)
    await message.answer(result['message'])
    await state.clear()


@router.callback_query(lambda c: c.data == "schedule_view")
async def schedule_view_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")],
        ]
    )
    await callback.message.answer("Введите ID студента:", reply_markup=keyboard)
    await state.set_state(AdminStates.waiting_for_schedule_view_id)


@router.message(AdminStates.waiting_for_schedule_view_id)
async def process_schedule_view(message: Message, state: FSMContext):
    student_id = message.text.strip()
    
    if not student_id.isdigit():
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")],
            ]
        )
        await message.answer("Введите корректный ID (число):", reply_markup=keyboard)
        return
    
    schedules = await get_schedule(int(student_id))
    
    if not schedules:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")],
            ]
        )
        await message.answer(f"У студента с ID {student_id} нет расписания.", reply_markup=keyboard)
        return
    
    text = f"Расписание студента (ID: {student_id}):\n\n"
    
    days_order = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    
    for day in days_order:
        day_schedules = [s for s in schedules if s['day_of_week'] == day]
        if day_schedules:
            text += f"{day}:\n"
            for s in day_schedules:
                text += f"  {s['start_time']} - {s['end_time']}\n"
            text += "\n"
    
    await message.answer(text)
    await state.clear()
