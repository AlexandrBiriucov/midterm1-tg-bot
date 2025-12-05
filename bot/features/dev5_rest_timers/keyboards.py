"""
Inline keyboards for timer functionality.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from localization.utils import t

from .services import get_user_timer_presets, format_time_display


def build_timer_keyboard(hours: int, minutes: int, seconds: int, lang: str = "en") -> InlineKeyboardMarkup:
    """Build the main timer configuration keyboard"""
    time_display = f"⏱ {hours}h {minutes}m {seconds}s"

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("timer_btn_add_h", lang), callback_data="timer_add_hour"),
            InlineKeyboardButton(text=t("timer_btn_add_m", lang), callback_data="timer_add_minute"),
            InlineKeyboardButton(text=t("timer_btn_add_s", lang), callback_data="timer_add_second"),
        ],
        [
            InlineKeyboardButton(text=t("timer_btn_sub_h", lang), callback_data="timer_sub_hour"),
            InlineKeyboardButton(text=t("timer_btn_sub_m", lang), callback_data="timer_sub_minute"),
            InlineKeyboardButton(text=t("timer_btn_sub_s", lang), callback_data="timer_sub_second"),
        ],
        [InlineKeyboardButton(text=t("timer_btn_start", lang), callback_data="timer_start")],
        [InlineKeyboardButton(text=t("timer_btn_stop", lang), callback_data="timer_stop")],
        [InlineKeyboardButton(text=t("timer_btn_presets", lang), callback_data="timer_presets_menu")],
        [InlineKeyboardButton(text=time_display, callback_data="timer_noop")],
    ])


def presets_menu_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    """Build the presets management menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("timer_btn_add", lang), callback_data="timer_preset_add"),
            InlineKeyboardButton(text=t("timer_btn_list", lang), callback_data="timer_preset_list")
        ],
        [
            InlineKeyboardButton(text=t("timer_btn_replace", lang), callback_data="timer_preset_replace"),
            InlineKeyboardButton(text=t("timer_btn_delete", lang), callback_data="timer_preset_delete")
        ],
        [InlineKeyboardButton(text=t("timer_btn_back", lang), callback_data="timer_go_main")],
    ])


def preset_list_keyboard(telegram_id: int, action: str = "load", lang: str = "en") -> InlineKeyboardMarkup:
    """Build keyboard with list of user's presets"""
    presets = get_user_timer_presets(telegram_id)
    buttons = []

    for preset in presets:
        time_str = format_time_display(preset.hours, preset.minutes, preset.seconds)
        buttons.append([InlineKeyboardButton(
            text=f"{preset.name} ({time_str})",
            callback_data=f"timer_preset_{action}_{preset.timer_preset_id}"
        )])

    buttons.append([InlineKeyboardButton(text=t("timer_btn_back", lang), callback_data="timer_presets_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)