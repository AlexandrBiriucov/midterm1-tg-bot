from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Tuple, Optional
from datetime import time

day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_codes = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']


def create_main_keyboard():
    """Create the main menu keyboard for training notifications"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Add Training", callback_data="notif_action_add")],
        [InlineKeyboardButton(text="📋 View List", callback_data="notif_action_list")],
        [InlineKeyboardButton(text="🔧 Change Trainings", callback_data="notif_action_change")],
    ])


def create_change_keyboard():
    """Create the change trainings menu keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Replace Training", callback_data="notif_action_replace")],
        [InlineKeyboardButton(text="🗑 Delete Training", callback_data="notif_action_delete")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="notif_back_to_main")],
    ])


def create_day_keyboard(action: str, num: Optional[int] = None):
    """Create day selection keyboard"""
    buttons = [[InlineKeyboardButton(text=day, callback_data=f"notif_{action}_day_{code}")] 
               for day, code in zip(day_names, day_codes)]
    
    if action == 'replace' and num is not None:
        for button in buttons:
            button[0].callback_data += f"_{num}"
    
    back_callback = "notif_back_to_change" if action in ['replace', 'delete'] else "notif_back_to_main"
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data=back_callback)])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def create_reminder_keyboard(action: str):
    """Create reminder time selection keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏱ 15 minutes before", callback_data=f"notif_{action}_reminder_15")],
        [InlineKeyboardButton(text="⏱ 30 minutes before", callback_data=f"notif_{action}_reminder_30")],
        [InlineKeyboardButton(text="⏱ 1 hour before", callback_data=f"notif_{action}_reminder_60")],
        [InlineKeyboardButton(text="⏱ 2 hours before", callback_data=f"notif_{action}_reminder_120")],
        [InlineKeyboardButton(text="✏️ Custom time", callback_data=f"notif_{action}_reminder_custom")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="notif_back_to_main")]
    ])


def format_reminder(reminder_minutes: int) -> str:
    """Format reminder time in human-readable format"""
    if reminder_minutes >= 60:
        hours = reminder_minutes // 60
        mins = reminder_minutes % 60
        return f"{hours} hour{'s' if hours > 1 else ''}" + (f" {mins} min" if mins else "")
    return f"{reminder_minutes} min"


def create_schedule_keyboard(schedules: List[Tuple], action_type: str):
    """Create keyboard showing list of scheduled trainings"""
    if not schedules:
        return None
    
    buttons = []
    for i, (weekday, train_time, reminder_minutes, _) in enumerate(schedules):
        reminder_str = format_reminder(reminder_minutes)
        text = f"{day_names[weekday]} {train_time.hour:02}:{train_time.minute:02} ({reminder_str} before)"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"notif_{action_type}_num_{i}")])
    
    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="notif_back_to_change")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)