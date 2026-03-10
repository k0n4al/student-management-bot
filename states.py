from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    # Состояния для добавления студента
    waiting_for_student_id = State()  # Ждём ID студента
    waiting_for_student_name = State()  # Ждём ФИО студента
    
    # Состояния для назначения ПК
    waiting_for_pc_student_id = State()  # Ждём ID студента для ПК
    waiting_for_pc_code = State()  # Ждём код ПК
    
    # Состояния для редактирования студента
    waiting_for_edit_student_id = State()  # Ждём ID студента для редактирования
    waiting_for_edit_choice = State()  # Ждём выбор что редактировать
    waiting_for_edit_value = State()  # Ждём новое значение
    
    # Состояния для удаления студента
    waiting_for_delete_student_id = State()  # Ждём ID студента для удаления
    waiting_for_delete_confirm = State()  # Ждём подтверждение удаления
    
    # Состояния для расписания
    waiting_for_schedule_student_id = State()  # Ждём ID студента для расписания
    waiting_for_schedule_day = State()  # Ждём день недели
    waiting_for_schedule_start = State()  # Ждём время начала
    waiting_for_schedule_end = State()  # Ждём время конца
    waiting_for_schedule_view_id = State()  # Ждём ID студента для просмотра расписания
