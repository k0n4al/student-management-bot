from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from database import get_schedule

router = Router()


@router.message(Command("schedule"))
async def cmd_schedule(message: Message):
    # Команда /schedule - моё расписание
    schedules = await get_schedule(message.from_user.id)
    
    if not schedules:
        await message.answer("У вас нет расписания.\nОбратитесь к администратору.")
        return
    
    text = "Ваше расписание:\n\n"
    
    # Группируем по дням
    days_order = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    
    for day in days_order:
        day_schedules = [s for s in schedules if s['day_of_week'] == day]
        if day_schedules:
            text += f"{day}:\n"
            for s in day_schedules:
                text += f"  {s['start_time']} - {s['end_time']}\n"
            text += "\n"
    
    await message.answer(text)
