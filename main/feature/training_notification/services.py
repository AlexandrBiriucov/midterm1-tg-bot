import asyncio
from datetime import datetime, timedelta, time
from typing import Dict, List, Tuple
from aiogram import Bot

# Store schedules: chat_id -> list of (weekday_int, time_obj, reminder_minutes, task)
schedules: Dict[int, List[Tuple]] = {}


async def reminder_loop(bot: Bot, chat_id: int, weekday: int, train_time: time, reminder_minutes: int):
    """Background loop for sending reminders"""
    while True:
        now = datetime.now()
        days_ahead = weekday - now.weekday()
        if days_ahead < 0:
            days_ahead += 7
        
        next_train_dt = now + timedelta(days=days_ahead)
        next_train_dt = next_train_dt.replace(hour=train_time.hour, minute=train_time.minute, second=0, microsecond=0)
        
        if next_train_dt <= now:
            next_train_dt += timedelta(days=7)
        
        next_reminder_dt = next_train_dt - timedelta(minutes=reminder_minutes)
        
        if next_reminder_dt <= now:
            next_train_dt += timedelta(days=7)
            next_reminder_dt = next_train_dt - timedelta(minutes=reminder_minutes)
        
        wait_seconds = (next_reminder_dt - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        
        try:
            if reminder_minutes >= 60:
                hours = reminder_minutes // 60
                mins = reminder_minutes % 60
                time_str = f"{hours} hour{'s' if hours > 1 else ''}" + (f" {mins} min" if mins else "")
            else:
                time_str = f"{reminder_minutes} min"
            
            await bot.send_message(chat_id, f"⏰ Training in {time_str}!")
        except Exception:
            pass


def load_schedules_from_db(bot: Bot, chat_id: int):
    """Load schedules from database and start background tasks"""
    from .database import load_trainings
    
    trainings = load_trainings(chat_id)
    
    if chat_id not in schedules:
        schedules[chat_id] = []
    
    # Cancel existing tasks
    for _, _, _, task in schedules[chat_id]:
        task.cancel()
    
    schedules[chat_id] = []
    
    # Create new tasks for each training
    for weekday, train_time, reminder_minutes in trainings:
        task = asyncio.create_task(reminder_loop(bot, chat_id, weekday, train_time, reminder_minutes))
        schedules[chat_id].append((weekday, train_time, reminder_minutes, task))


def get_schedules(chat_id: int) -> List[Tuple]:
    """Get schedules for a specific chat_id"""
    return schedules.get(chat_id, [])


def add_schedule(chat_id: int, weekday: int, train_time: time, reminder_minutes: int, task):
    """Add a new schedule"""
    if chat_id not in schedules:
        schedules[chat_id] = []
    schedules[chat_id].append((weekday, train_time, reminder_minutes, task))


def update_schedule(chat_id: int, index: int, weekday: int, train_time: time, reminder_minutes: int, task):
    """Update an existing schedule"""
    if chat_id in schedules and 0 <= index < len(schedules[chat_id]):
        # Cancel old task
        old_task = schedules[chat_id][index][3]
        old_task.cancel()
        # Update with new data
        schedules[chat_id][index] = (weekday, train_time, reminder_minutes, task)


def delete_schedule(chat_id: int, index: int):
    """Delete a schedule by index"""
    if chat_id in schedules and 0 <= index < len(schedules[chat_id]):
        # Cancel the task
        task = schedules[chat_id][index][3]
        task.cancel()
        # Remove from list
        del schedules[chat_id][index]