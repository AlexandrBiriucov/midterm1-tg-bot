from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .services import settings
from .services import schedules, day_names, day_codes


def build_timer_keyboard(user_id: int) -> InlineKeyboardMarkup:
    s = settings.get(user_id, {"hours": 0, "minutes": 0, "seconds": 0})
    text = f"⏱ {s['hours']}h {s['minutes']}m {s['seconds']}s"

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Hours", callback_data="add_hour"),
            InlineKeyboardButton(text="➕ Minutes", callback_data="add_minute"),
            InlineKeyboardButton(text="➕ Seconds", callback_data="add_second"),
        ],
        [
            InlineKeyboardButton(text="➖ Hours", callback_data="sub_hour"),
            InlineKeyboardButton(text="➖ Minutes", callback_data="sub_minute"),
            InlineKeyboardButton(text="➖ Seconds", callback_data="sub_second"),
        ],
        [InlineKeyboardButton(text="Start ✅", callback_data="start_timer")],
        [InlineKeyboardButton(text="Stop ⛔", callback_data="stop_timer")],
        [InlineKeyboardButton(text=text, callback_data="noop")],
    ])

def create_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Add", callback_data="action_add"),
            InlineKeyboardButton(text="List", callback_data="action_list"),
            InlineKeyboardButton(text="Replace", callback_data="action_replace")
        ]
    ])

def create_day_keyboard(action: str, num: int = None):
    buttons = [[InlineKeyboardButton(text=day, callback_data=f"{action}_day_{code}")]
               for day, code in zip(day_names, day_codes)]
    if action == 'replace' and num is not None:
        for button in buttons:
            button[0].callback_data += f"_{num}"
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def create_schedule_keyboard(chat_id: int):
    if chat_id not in schedules or not schedules[chat_id]:
        return None
    buttons = []
    for i, (weekday, train_time, _) in enumerate(schedules[chat_id]):
        text = f"{day_names[weekday]} {train_time.hour:02}:{train_time.minute:02}"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"replace_num_{i}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
