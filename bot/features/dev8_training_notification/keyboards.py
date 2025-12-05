from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Tuple, Optional
from datetime import time

from localization.utils import t

# Оставляем только коды дней, названия теперь через переводы
day_codes = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']


def create_main_keyboard(lang: str = "en"):
    """Create the main menu keyboard for training notifications"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("notif_btn_add", lang), callback_data="notif_action_add")],
        [InlineKeyboardButton(text=t("notif_btn_list", lang), callback_data="notif_action_list")],
        [InlineKeyboardButton(text=t("notif_btn_edit", lang), callback_data="notif_action_change")],
    ])


def create_change_keyboard(lang: str = "en"):
    """Create the change trainings menu keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("notif_btn_replace", lang), callback_data="notif_action_replace")],
        [InlineKeyboardButton(text=t("notif_btn_delete", lang), callback_data="notif_action_delete")],
        [InlineKeyboardButton(text=t("notif_btn_back", lang), callback_data="notif_back_to_main")],
    ])


def create_day_keyboard(action: str, lang: str = "en", num: Optional[int] = None):
    """Create day selection keyboard"""
    # Создаём кнопки для каждого дня недели (0-6)
    buttons = [[InlineKeyboardButton(text=t(f"day_name_{i}", lang), callback_data=f"notif_{action}_day_{code}")]
               for i, code in enumerate(day_codes)]

    if action == 'replace' and num is not None:
        for button in buttons:
            button[0].callback_data += f"_{num}"

    back_callback = "notif_back_to_change" if action in ['replace', 'delete'] else "notif_back_to_main"
    buttons.append([InlineKeyboardButton(text=t("notif_btn_back", lang), callback_data=back_callback)])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def create_reminder_keyboard(action: str, lang: str = "en"):
    """Create reminder time selection keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("notif_btn_15min", lang), callback_data=f"notif_{action}_reminder_15")],
        [InlineKeyboardButton(text=t("notif_btn_30min", lang), callback_data=f"notif_{action}_reminder_30")],
        [InlineKeyboardButton(text=t("notif_btn_1hour", lang), callback_data=f"notif_{action}_reminder_60")],
        [InlineKeyboardButton(text=t("notif_btn_2hours", lang), callback_data=f"notif_{action}_reminder_120")],
        [InlineKeyboardButton(text=t("notif_btn_custom_time", lang), callback_data=f"notif_{action}_reminder_custom")],
        [InlineKeyboardButton(text=t("notif_btn_back", lang), callback_data="notif_back_to_main")]
    ])


def format_reminder(reminder_minutes: int, lang: str = "en") -> str:
    """Format reminder time in human-readable format"""
    if reminder_minutes >= 60:
        hours = reminder_minutes // 60
        mins = reminder_minutes % 60

        # Форматируем часы
        if hours == 1:
            hour_str = t("notif_time_1hour", lang)
        else:
            hour_str = t("notif_time_hours", lang, hours=hours)

        # Добавляем минуты если есть
        if mins:
            min_str = t("notif_time_minutes", lang, minutes=mins)
            return f"{hour_str} {min_str}"
        return hour_str

    return t("notif_time_minutes", lang, minutes=reminder_minutes)


def create_schedule_keyboard(schedules: List[Tuple], action_type: str, lang: str = "en"):
    """Create keyboard showing list of scheduled trainings"""
    if not schedules:
        return None

    buttons = []
    for i, (weekday, train_time, reminder_minutes, _) in enumerate(schedules):
        reminder_str = format_reminder(reminder_minutes, lang)
        day_name = t(f"day_name_{weekday}", lang)
        before_text = t("notif_before", lang)
        text = f"{day_name} {train_time.hour:02}:{train_time.minute:02} ({reminder_str} {before_text})"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"notif_{action_type}_num_{i}")])

    buttons.append([InlineKeyboardButton(text=t("notif_btn_back", lang), callback_data="notif_back_to_change")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)