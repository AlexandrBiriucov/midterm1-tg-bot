import aiosqlite
from typing import List, Dict, Optional
import os

# Путь к базе данных в папке feature/dev5_rest_timers
DATABASE_PATH = os.path.join(
    os.path.dirname(__file__), 
    "timer_presets.db"
)


async def init_db():
    """Инициализация базы данных и создание таблиц"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS presets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                seconds INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_id ON presets(user_id)
        """)
        await db.commit()


async def add_preset(user_id: int, name: str, seconds: int) -> bool:
    """Добавить новый пресет"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                "INSERT INTO presets (user_id, name, seconds) VALUES (?, ?, ?)",
                (user_id, name, seconds)
            )
            await db.commit()
        return True
    except Exception as e:
        print(f"Error adding preset: {e}")
        return False


async def get_user_presets(user_id: int) -> List[Dict]:
    """Получить все пресеты пользователя"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id, name, seconds FROM presets WHERE user_id = ? ORDER BY id",
            (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [{"id": row["id"], "name": row["name"], "seconds": row["seconds"]} for row in rows]


async def update_preset(preset_id: int, user_id: int, name: str, seconds: int) -> bool:
    """Обновить существующий пресет"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                "UPDATE presets SET name = ?, seconds = ? WHERE id = ? AND user_id = ?",
                (name, seconds, preset_id, user_id)
            )
            await db.commit()
        return True
    except Exception as e:
        print(f"Error updating preset: {e}")
        return False


async def delete_preset(preset_id: int, user_id: int) -> bool:
    """Удалить пресет"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute(
                "DELETE FROM presets WHERE id = ? AND user_id = ?",
                (preset_id, user_id)
            )
            await db.commit()
        return True
    except Exception as e:
        print(f"Error deleting preset: {e}")
        return False


async def get_presets_count(user_id: int) -> int:
    """Получить количество пресетов пользователя"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) as count FROM presets WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0