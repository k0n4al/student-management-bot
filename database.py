import aiosqlite
import os

# Путь к папке с проектом (где лежит database.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "students.db")

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        # Таблица студентов
        await db.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                full_name TEXT,
                pc_code TEXT,
                phone TEXT,
                gitlab_link TEXT,
                redmine_link TEXT,
                task_text TEXT,
                photo_id TEXT
            )
        """)
        
        # Таблица расписания
        await db.execute("""
            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                day_of_week TEXT,
                start_time TEXT,
                end_time TEXT
            )
        """)
        
        # Таблица пользователей
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                is_admin INTEGER DEFAULT 0
            )
        """)
        
        await db.commit()

# Функции для студентов
async def add_student(telegram_id: int, full_name: str):
    """Добавить студента. Возвращает True если успешно, False если уже существует"""
    async with aiosqlite.connect(DB_NAME) as db:
        # Проверяем есть ли уже студент с таким ID
        cursor = await db.execute(
            "SELECT id FROM students WHERE telegram_id = ?",
            (telegram_id,)
        )
        exists = await cursor.fetchone()
        if exists:
            return False
        
        await db.execute(
            "INSERT INTO students (telegram_id, full_name) VALUES (?, ?)",
            (telegram_id, full_name)
        )
        await db.commit()
        return True

async def student_exists(telegram_id: int) -> bool:
    """Проверить существует ли студент"""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT id FROM students WHERE telegram_id = ?",
            (telegram_id,)
        )
        return await cursor.fetchone() is not None

async def pc_exists(pc_code: str) -> bool:
    """Проверить существует ли ПК с таким кодом"""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT id FROM students WHERE pc_code = ?",
            (pc_code,)
        )
        return await cursor.fetchone() is not None

async def get_student(telegram_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM students WHERE telegram_id = ?",
            (telegram_id,)
        )
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None

async def update_student_pc(telegram_id: int, pc_code: str) -> dict:
    """
    Назначить ПК студенту.
    Возвращает dict: {'success': True/False, 'message': 'текст'}
    """
    async with aiosqlite.connect(DB_NAME) as db:
        # Проверяем существует ли студент
        cursor = await db.execute(
            "SELECT id FROM students WHERE telegram_id = ?",
            (telegram_id,)
        )
        student = await cursor.fetchone()
        if not student:
            return {'success': False, 'message': 'Студент с таким ID не найден'}
        
        # Проверяем не занят ли ПК другим студентом
        cursor = await db.execute(
            "SELECT id FROM students WHERE pc_code = ? AND telegram_id != ?",
            (pc_code, telegram_id)
        )
        pc_busy = await cursor.fetchone()
        if pc_busy:
            return {'success': False, 'message': f'ПК {pc_code} уже занят другим студентом'}
        
        await db.execute(
            "UPDATE students SET pc_code = ? WHERE telegram_id = ?",
            (pc_code, telegram_id)
        )
        await db.commit()
        return {'success': True, 'message': f'ПК {pc_code} назначен'}

async def get_all_students():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM students")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

# Функции для админов
async def add_admin(telegram_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR REPLACE INTO users (telegram_id, is_admin) VALUES (?, 1)",
            (telegram_id,)
        )
        await db.commit()

async def is_admin(telegram_id: int) -> bool:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT is_admin FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )
        result = await cursor.fetchone()
        return bool(result and result[0])

async def delete_student(telegram_id: int) -> bool:
    """Удалить студента. Возвращает True если успешно"""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT id FROM students WHERE telegram_id = ?",
            (telegram_id,)
        )
        exists = await cursor.fetchone()
        if not exists:
            return False
        
        await db.execute("DELETE FROM students WHERE telegram_id = ?", (telegram_id,))
        await db.commit()
        return True

async def update_student_field(telegram_id: int, field: str, value: str) -> dict:
    """
    Обновить поле студента.
    field: 'full_name', 'pc_code', 'phone', 'gitlab_link', 'redmine_link', 'task_text'
    Возвращает dict: {'success': True/False, 'message': 'текст'}
    """
    async with aiosqlite.connect(DB_NAME) as db:
        # Проверяем существует ли студент
        cursor = await db.execute(
            "SELECT id FROM students WHERE telegram_id = ?",
            (telegram_id,)
        )
        student = await cursor.fetchone()
        if not student:
            return {'success': False, 'message': 'Студент с таким ID не найден'}
        
        # Проверяем что поле существует
        allowed_fields = ['full_name', 'pc_code', 'phone', 'gitlab_link', 'redmine_link', 'task_text']
        if field not in allowed_fields:
            return {'success': False, 'message': 'Недопустимое поле'}

        await db.execute(
            f"UPDATE students SET {field} = ? WHERE telegram_id = ?",
            (value, telegram_id)
        )
        await db.commit()
        return {'success': True, 'message': f'Поле {field} обновлено'}


# ========== ФУНКЦИИ ДЛЯ РАСПИСАНИЯ ==========

async def add_schedule(telegram_id: int, day_of_week: str, start_time: str, end_time: str) -> dict:
    # Добавить запись в расписание студента. Возвращает dict: {'success': True/False, 'message': 'текст'}
    async with aiosqlite.connect(DB_NAME) as db:
        # Проверяем существует ли студент и получаем его внутренний ID
        cursor = await db.execute(
            "SELECT id FROM students WHERE telegram_id = ?",
            (telegram_id,)
        )
        student = await cursor.fetchone()
        if not student:
            return {'success': False, 'message': 'Студент с таким ID не найден'}
        
        # Сохраняем внутренний ID студента, а не telegram_id
        await db.execute(
            "INSERT INTO schedule (student_id, day_of_week, start_time, end_time) VALUES (?, ?, ?, ?)",
            (student[0], day_of_week, start_time, end_time)
        )
        await db.commit()
        return {'success': True, 'message': 'Расписание добавлено'}


async def get_schedule(student_id: int):
    # Получить расписание студента по telegram_id
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM schedule WHERE student_id = (SELECT id FROM students WHERE telegram_id = ?) ORDER BY id",
            (student_id,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows] if rows else []


async def delete_schedule(schedule_id: int) -> bool:
    # Удалить запись расписания по ID
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM schedule WHERE id = ?", (schedule_id,))
        await db.commit()
        return True