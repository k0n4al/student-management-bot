import aiosqlite

DB_NAME = "students.db"

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
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR REPLACE INTO students (telegram_id, full_name) VALUES (?, ?)",
            (telegram_id, full_name)
        )
        await db.commit()

async def get_student(telegram_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM students WHERE telegram_id = ?",
            (telegram_id,)
        )
        return await cursor.fetchone()

async def update_student_pc(telegram_id: int, pc_code: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE students SET pc_code = ? WHERE telegram_id = ?",
            (pc_code, telegram_id)
        )
        await db.commit()

async def get_all_students():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM students")
        return await cursor.fetchall()

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