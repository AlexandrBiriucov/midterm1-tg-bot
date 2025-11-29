"""
Inline keyboards for timer functionality.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .services import get_user_timer_presets, format_time_display


def build_timer_keyboard(hours: int, minutes: int, seconds: int) -> InlineKeyboardMarkup:
    """Build the main timer configuration keyboard"""
    time_display = f"⏱ {hours}h {minutes}m {seconds}s"
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Hours", callback_data="timer_add_hour"),
            InlineKeyboardButton(text="➕ Minutes", callback_data="timer_add_minute"),
            InlineKeyboardButton(text="➕ Seconds", callback_data="timer_add_second"),
        ],
        [
            InlineKeyboardButton(text="➖ Hours", callback_data="timer_sub_hour"),
            InlineKeyboardButton(text="➖ Minutes", callback_data="timer_sub_minute"),
            InlineKeyboardButton(text="➖ Seconds", callback_data="timer_sub_second"),
        ],
        [InlineKeyboardButton(text="Start ✅", callback_data="timer_start")],
        [InlineKeyboardButton(text="Stop ⛔", callback_data="timer_stop")],
        [InlineKeyboardButton(text="⚙️ Presets", callback_data="timer_presets_menu")],
        [InlineKeyboardButton(text=time_display, callback_data="timer_noop")],
    ])


def presets_menu_keyboard() -> InlineKeyboardMarkup:
    """Build the presets management menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Add", callback_data="timer_preset_add"),
            InlineKeyboardButton(text="📋 List", callback_data="timer_preset_list")
        ],
        [
            InlineKeyboardButton(text="✏️ Replace", callback_data="timer_preset_replace"),
            InlineKeyboardButton(text="🗑 Delete", callback_data="timer_preset_delete")
        ],
        [InlineKeyboardButton(text="🔙 Back", callback_data="timer_go_main")],
    ])


def preset_list_keyboard(telegram_id: int, action: str = "load") -> InlineKeyboardMarkup:
    """Build keyboard with list of user's presets"""
    presets = get_user_timer_presets(telegram_id)
    buttons = []
    
    for preset in presets:
        time_str = format_time_display(preset.hours, preset.minutes, preset.seconds)
        buttons.append([InlineKeyboardButton(
            text=f"{preset.name} ({time_str})",
            callback_data=f"timer_preset_{action}_{preset.timer_preset_id}"
        )])
    
    buttons.append([InlineKeyboardButton(text="🔙 Back", callback_data="timer_presets_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)