import sqlite3
from datetime import time
from typing import List, Tuple, Optional

DB_PATH = 'trainings.db'


def init_db():
    """Initialize the trainings database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trainings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            weekday INTEGER NOT NULL,
            hour INTEGER NOT NULL,
            minute INTEGER NOT NULL,
            reminder_minutes INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def save_training(chat_id: int, weekday: int, train_time: time, reminder_minutes: int):
    """Save a new training to the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO trainings (chat_id, weekday, hour, minute, reminder_minutes) VALUES (?, ?, ?, ?, ?)',
        (chat_id, weekday, train_time.hour, train_time.minute, reminder_minutes)
    )
    conn.commit()
    conn.close()


def load_trainings(chat_id: int) -> List[Tuple[int, time, int]]:
    """Load all trainings for a specific chat_id"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT weekday, hour, minute, reminder_minutes FROM trainings WHERE chat_id = ? ORDER BY weekday, hour, minute',
        (chat_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [(row[0], time(row[1], row[2]), row[3]) for row in rows]


def update_training(chat_id: int, index: int, weekday: int, train_time: time, reminder_minutes: int):
    """Update an existing training"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id FROM trainings WHERE chat_id = ? ORDER BY weekday, hour, minute',
        (chat_id,)
    )
    rows = cursor.fetchall()
    if 0 <= index < len(rows):
        training_id = rows[index][0]
        cursor.execute(
            'UPDATE trainings SET weekday = ?, hour = ?, minute = ?, reminder_minutes = ? WHERE id = ?',
            (weekday, train_time.hour, train_time.minute, reminder_minutes, training_id)
        )
        conn.commit()
    conn.close()


def delete_training(chat_id: int, index: int):
    """Delete a training by index"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id FROM trainings WHERE chat_id = ? ORDER BY weekday, hour, minute',
        (chat_id,)
    )
    rows = cursor.fetchall()
    if 0 <= index < len(rows):
        training_id = rows[index][0]
        cursor.execute('DELETE FROM trainings WHERE id = ?', (training_id,))
        conn.commit()
    conn.close()