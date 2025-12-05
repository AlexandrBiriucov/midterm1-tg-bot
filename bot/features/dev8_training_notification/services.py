"""
Background services and database operations for training notifications.
All database operations integrated here.
"""
import asyncio
from datetime import datetime, timedelta, time
from typing import Dict, List, Tuple, Optional
from aiogram import Bot

from localization.utils import t
from bot.core.database import get_session
from bot.core.models import TrainingNotification

# Store schedules: chat_id -> list of (weekday_int, time_obj, reminder_minutes, task)
schedules: Dict[int, List[Tuple]] = {}


# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

def save_training(chat_id: int, weekday: int, train_time: time, reminder_minutes: int) -> bool:
    """
    Save a new training notification to the database.
    Returns True if successful, False otherwise.
    """
    try:
        with get_session() as session:
            notification = TrainingNotification(
                user_id=chat_id,
                weekday=weekday,
                hour=train_time.hour,
                minute=train_time.minute,
                reminder_minutes=reminder_minutes
            )
            session.add(notification)
        return True
    except Exception as e:
        print(f"Error saving training: {e}")
        return False


def load_trainings(chat_id: int) -> List[Tuple[int, time, int]]:
    """
    Load all training notifications for a specific user.
    Returns list of (weekday, time, reminder_minutes) tuples.
    """
    try:
        with get_session() as session:
            notifications = session.query(TrainingNotification)\
                .filter(TrainingNotification.user_id == chat_id)\
                .order_by(
                    TrainingNotification.weekday,
                    TrainingNotification.hour,
                    TrainingNotification.minute
                )\
                .all()

            return [
                (n.weekday, time(n.hour, n.minute), n.reminder_minutes)
                for n in notifications
            ]
    except Exception as e:
        print(f"Error loading trainings: {e}")
        return []


def update_training(chat_id: int, index: int, weekday: int, train_time: time, reminder_minutes: int) -> bool:
    """
    Update an existing training notification.
    Returns True if successful, False otherwise.
    """
    try:
        with get_session() as session:
            notifications = session.query(TrainingNotification)\
                .filter(TrainingNotification.user_id == chat_id)\
                .order_by(
                    TrainingNotification.weekday,
                    TrainingNotification.hour,
                    TrainingNotification.minute
                )\
                .all()

            if 0 <= index < len(notifications):
                notification = notifications[index]
                notification.weekday = weekday
                notification.hour = train_time.hour
                notification.minute = train_time.minute
                notification.reminder_minutes = reminder_minutes
                return True
            return False
    except Exception as e:
        print(f"Error updating training: {e}")
        return False


def delete_training(chat_id: int, index: int) -> bool:
    """
    Delete a training notification by index.
    Returns True if successful, False otherwise.
    """
    try:
        with get_session() as session:
            notifications = session.query(TrainingNotification)\
                .filter(TrainingNotification.user_id == chat_id)\
                .order_by(
                    TrainingNotification.weekday,
                    TrainingNotification.hour,
                    TrainingNotification.minute
                )\
                .all()

            if 0 <= index < len(notifications):
                notification = notifications[index]
                session.delete(notification)
                return True
            return False
    except Exception as e:
        print(f"Error deleting training: {e}")
        return False


def get_notification_count(chat_id: int) -> int:
    """Get the total count of notifications for a user."""
    try:
        with get_session() as session:
            count = session.query(TrainingNotification)\
                .filter(TrainingNotification.user_id == chat_id)\
                .count()
            return count
    except Exception as e:
        print(f"Error getting notification count: {e}")
        return 0


# ============================================================================
# HELPER FUNCTION - получение языка пользователя
# ============================================================================

def get_user_lang(chat_id: int) -> str:
    """
    Get user's language from database.
    Returns 'en' by default if not found.
    """
    try:
        from bot.features.dev1_workout_tracking.services import get_lang
        return get_lang(chat_id)
    except Exception:
        return "en"


# ============================================================================
# BACKGROUND TASK MANAGEMENT
# ============================================================================

async def reminder_loop(bot: Bot, chat_id: int, weekday: int, train_time: time, reminder_minutes: int):
    """
    Background loop for sending reminders.
    Runs continuously and sends notifications at the scheduled time.
    """
    while True:
        try:
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

            next_reminder_dt = next_train_dt - timedelta(minutes=reminder_minutes)

            if next_reminder_dt <= now:
                next_train_dt += timedelta(days=7)
                next_reminder_dt = next_train_dt - timedelta(minutes=reminder_minutes)

            wait_seconds = (next_reminder_dt - now).total_seconds()
            await asyncio.sleep(wait_seconds)

            # Get user's language
            lang = get_user_lang(chat_id)

            # Format time string - используем переводы
            if reminder_minutes >= 60:
                hours = reminder_minutes // 60
                mins = reminder_minutes % 60

                if hours == 1:
                    time_str = t("notif_time_1hour", lang)
                else:
                    time_str = t("notif_time_hours", lang, hours=hours)

                if mins:
                    min_str = t("notif_time_minutes", lang, minutes=mins)
                    time_str = f"{time_str} {min_str}"
            else:
                time_str = t("notif_time_minutes", lang, minutes=reminder_minutes)

            # Send reminder message
            await bot.send_message(chat_id, t("notif_reminder_message", lang, time_str=time_str))
            
        except asyncio.CancelledError:
            # Task was cancelled, exit gracefully
            break
        except Exception as e:
            print(f"Error in reminder loop: {e}")
            # Wait a bit before retrying to avoid rapid error loops
            await asyncio.sleep(60)


def load_schedules_from_db(bot: Bot, chat_id: int):
    """
    Load schedules from database and start background tasks.
    Called when user starts /notification command.
    """
    trainings = load_trainings(chat_id)
    
    if chat_id not in schedules:
        schedules[chat_id] = []
    
    # Cancel existing tasks
    for _, _, _, task in schedules[chat_id]:
        task.cancel()
    
    schedules[chat_id] = []
    
    # Create new tasks for each training
    for weekday, train_time, reminder_minutes in trainings:
        task = asyncio.create_task(
            reminder_loop(bot, chat_id, weekday, train_time, reminder_minutes)
        )
        schedules[chat_id].append((weekday, train_time, reminder_minutes, task))


def get_schedules(chat_id: int) -> List[Tuple]:
    """
    Get in-memory schedules for a specific chat_id.
    Returns list of (weekday, time, reminder_minutes, task) tuples.
    """
    return schedules.get(chat_id, [])


def add_schedule(chat_id: int, weekday: int, train_time: time, reminder_minutes: int, task):
    """
    Add a new schedule to in-memory storage.
    Should be called after saving to database.
    """
    if chat_id not in schedules:
        schedules[chat_id] = []
    schedules[chat_id].append((weekday, train_time, reminder_minutes, task))


def update_schedule(chat_id: int, index: int, weekday: int, train_time: time, reminder_minutes: int, task):
    """
    Update an existing schedule in in-memory storage.
    Should be called after updating database.
    """
    if chat_id in schedules and 0 <= index < len(schedules[chat_id]):
        # Cancel old task
        old_task = schedules[chat_id][index][3]
        old_task.cancel()
        # Update with new data
        schedules[chat_id][index] = (weekday, train_time, reminder_minutes, task)


def delete_schedule(chat_id: int, index: int):
    """
    Delete a schedule from in-memory storage.
    Should be called after deleting from database.
    """
    if chat_id in schedules and 0 <= index < len(schedules[chat_id]):
        # Cancel the task
        task = schedules[chat_id][index][3]
        task.cancel()
        # Remove from list
        del schedules[chat_id][index]


def cleanup_user_schedules(chat_id: int):
    """
    Cancel all background tasks for a user.
    Useful for cleanup when user is blocked or deleted.
    """
    if chat_id in schedules:
        for _, _, _, task in schedules[chat_id]:
            task.cancel()
        del schedules[chat_id]