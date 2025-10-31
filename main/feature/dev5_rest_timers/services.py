import asyncio
import re
from datetime import datetime, timedelta, time
from aiogram.filters import BaseFilter
from aiogram.types import Message

class Timer:
    def __init__(self, duration_seconds: int):
        self.duration = duration_seconds
        self.start_time = None
        self.task = None

    def start(self):
        self.start_time = datetime.now()

    def remaining_seconds(self) -> int:
        if not self.start_time:
            return self.duration
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return max(0, self.duration - int(elapsed))

# Хранилища
timers: dict[int, Timer] = {}
settings: dict[int, dict[str, int]] = {}

# ===== Хранилища =====
schedules: dict[int, list] = {}   # chat_id -> list of (weekday, time, task)
user_states: dict[int, dict] = {} # chat_id -> {state, selected_num, selected_day}

day_map = {'Mo': 0, 'Tu': 1, 'We': 2, 'Th': 3, 'Fr': 4, 'Sa': 5, 'Su': 6}
day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_codes = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']


class TimeFormatFilter(BaseFilter):
    """Фильтр для времени в формате HH:MM"""
    async def __call__(self, message: Message) -> bool:
        return bool(re.match(r'^\d{2}:\d{2}$', message.text))


async def reminder_loop(message: Message, weekday, train_time: time):
    """Фоновый цикл напоминаний"""
    chat_id = message.chat.id
    while True:
        now = datetime.now()
        days_ahead = weekday - now.weekday()
        if days_ahead < 0:
            days_ahead += 7
        next_train_dt = now + timedelta(days=days_ahead)
        next_train_dt = next_train_dt.replace(
            hour=train_time.hour,
            minute=train_time.minute,
            second=0,
            microsecond=0
        )
        if next_train_dt <= now:
            next_train_dt += timedelta(days=7)

        # напоминание за 1 час
        next_reminder_dt = next_train_dt - timedelta(hours=1)
        if next_reminder_dt <= now:
            next_train_dt += timedelta(days=7)
            next_reminder_dt = next_train_dt - timedelta(hours=1)

        wait_seconds = (next_reminder_dt - now).total_seconds()
        await asyncio.sleep(wait_seconds)

        try:
            await message.answer("🏋️ Training in one hour!")
        except Exception:
            pass  # если пользователь недоступен — игнорим

