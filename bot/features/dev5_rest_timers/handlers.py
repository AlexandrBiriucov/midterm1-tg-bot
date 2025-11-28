"""
Handlers for timer functionality.
Rest timers between sets and custom timer presets.
"""
import asyncio
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from .states import TimerPresetForm
from .keyboards import (
    build_timer_keyboard,
    presets_menu_keyboard,
    preset_list_keyboard
)
from .services import (
    add_timer_preset,
    get_user_timer_presets,
    get_timer_preset_by_id,
    delete_timer_preset,
    update_timer_preset,
    parse_time_string,
    format_time_display
)
from bot.features.dev1_workout_tracking.services import get_or_create_user

router = Router(name="timer")


# ==========================================
# TIMER CLASS
# ==========================================

class Timer:
    """Simple timer class for tracking time"""
    def __init__(self, duration_seconds: int):
        self.duration = duration_seconds
        self.start_time = None
        self.task = None
        self.message_id = None  # Store message ID for updating

    def start(self):
        self.start_time = datetime.now()

    def remaining_seconds(self) -> int:
        if not self.start_time:
            return self.duration
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return max(0, self.duration - int(elapsed))


# In-memory storage for active timers and user settings
active_timers: dict[int, Timer] = {}
timer_settings: dict[int, dict[str, int]] = {}


# ==========================================
# HELPER FUNCTIONS
# ==========================================

async def refresh_timer_message(callback: CallbackQuery, user_id: int):
    """Refresh the timer configuration message"""
    settings = timer_settings.get(user_id, {"hours": 0, "minutes": 0, "seconds": 0})
    await callback.message.edit_text(
        "⏱ Configure your timer:",
        reply_markup=build_timer_keyboard(
            settings["hours"],
            settings["minutes"],
            settings["seconds"]
        )
    )


def init_timer_settings(user_id: int):
    """Initialize timer settings for user if not exists"""
    if user_id not in timer_settings:
        timer_settings[user_id] = {"hours": 0, "minutes": 0, "seconds": 0}


def build_stop_timer_keyboard() -> InlineKeyboardMarkup:
    """Build keyboard with Stop Timer button"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏹ Stop Timer", callback_data="timer_stop_active")]
    ])


# ==========================================
# COMMAND HANDLERS
# ==========================================

@router.message(Command("timer"))
async def cmd_timer(message: Message):
    """Start timer interface"""
    user_id = message.from_user.id
    
    # Ensure user exists in database
    get_or_create_user(
        telegram_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    init_timer_settings(user_id)
    
    await message.answer(
        "⏱ Configure your timer:",
        reply_markup=build_timer_keyboard(
            timer_settings[user_id]["hours"],
            timer_settings[user_id]["minutes"],
            timer_settings[user_id]["seconds"]
        )
    )


# ==========================================
# TIME ADJUSTMENT HANDLERS
# ==========================================

@router.callback_query(F.data == "timer_add_hour")
async def add_hour(callback: CallbackQuery):
    """Add 1 hour to timer"""
    user_id = callback.from_user.id
    init_timer_settings(user_id)
    
    timer_settings[user_id]["hours"] += 1
    await refresh_timer_message(callback, user_id)
    await callback.answer("➕ 1 hour")


@router.callback_query(F.data == "timer_add_minute")
async def add_minute(callback: CallbackQuery):
    """Add 1 minute to timer"""
    user_id = callback.from_user.id
    init_timer_settings(user_id)
    
    if timer_settings[user_id]["minutes"] < 59:
        timer_settings[user_id]["minutes"] += 1
    else:
        timer_settings[user_id]["minutes"] = 0
        timer_settings[user_id]["hours"] += 1
    
    await refresh_timer_message(callback, user_id)
    await callback.answer("➕ 1 minute")


@router.callback_query(F.data == "timer_add_second")
async def add_second(callback: CallbackQuery):
    """Add 1 second to timer"""
    user_id = callback.from_user.id
    init_timer_settings(user_id)
    
    if timer_settings[user_id]["seconds"] < 59:
        timer_settings[user_id]["seconds"] += 1
    else:
        timer_settings[user_id]["seconds"] = 0
        if timer_settings[user_id]["minutes"] < 59:
            timer_settings[user_id]["minutes"] += 1
        else:
            timer_settings[user_id]["minutes"] = 0
            timer_settings[user_id]["hours"] += 1
    
    await refresh_timer_message(callback, user_id)
    await callback.answer("➕ 1 second")


@router.callback_query(F.data == "timer_sub_hour")
async def sub_hour(callback: CallbackQuery):
    """Subtract 1 hour from timer"""
    user_id = callback.from_user.id
    init_timer_settings(user_id)
    
    if timer_settings[user_id]["hours"] > 0:
        timer_settings[user_id]["hours"] -= 1
    
    await refresh_timer_message(callback, user_id)
    await callback.answer("➖ 1 hour")


@router.callback_query(F.data == "timer_sub_minute")
async def sub_minute(callback: CallbackQuery):
    """Subtract 1 minute from timer"""
    user_id = callback.from_user.id
    init_timer_settings(user_id)
    
    if timer_settings[user_id]["minutes"] > 0:
        timer_settings[user_id]["minutes"] -= 1
    elif timer_settings[user_id]["hours"] > 0:
        timer_settings[user_id]["hours"] -= 1
        timer_settings[user_id]["minutes"] = 59
    
    await refresh_timer_message(callback, user_id)
    await callback.answer("➖ 1 minute")


@router.callback_query(F.data == "timer_sub_second")
async def sub_second(callback: CallbackQuery):
    """Subtract 1 second from timer"""
    user_id = callback.from_user.id
    init_timer_settings(user_id)
    
    if timer_settings[user_id]["seconds"] > 0:
        timer_settings[user_id]["seconds"] -= 1
    elif timer_settings[user_id]["minutes"] > 0:
        timer_settings[user_id]["minutes"] -= 1
        timer_settings[user_id]["seconds"] = 59
    elif timer_settings[user_id]["hours"] > 0:
        timer_settings[user_id]["hours"] -= 1
        timer_settings[user_id]["minutes"] = 59
        timer_settings[user_id]["seconds"] = 59
    
    await refresh_timer_message(callback, user_id)
    await callback.answer("➖ 1 second")


# ==========================================
# TIMER CONTROL HANDLERS
# ==========================================

@router.callback_query(F.data == "timer_start")
async def start_timer(callback: CallbackQuery):
    """Start the timer"""
    user_id = callback.from_user.id
    init_timer_settings(user_id)
    
    settings = timer_settings[user_id]
    total_seconds = settings["hours"] * 3600 + settings["minutes"] * 60 + settings["seconds"]

    if total_seconds <= 0:
        await callback.answer("⚠️ Time is not set", show_alert=True)
        return

    timer = Timer(total_seconds)
    timer.start()
    active_timers[user_id] = timer

    async def notify():
        try:
            await asyncio.sleep(total_seconds)
            if user_id in active_timers and active_timers[user_id] == timer:
                del active_timers[user_id]
                timer_settings[user_id] = {"hours": 0, "minutes": 0, "seconds": 0}
                
                # Try to remove the stop button from the timer message
                try:
                    if timer.message_id:
                        await callback.bot.edit_message_reply_markup(
                            chat_id=callback.message.chat.id,
                            message_id=timer.message_id,
                            reply_markup=None
                        )
                except Exception:
                    pass  # Message might be deleted or inaccessible
                
                await callback.message.answer(
                    "✅ Timer completed!\n\n🔄 Do you want to start a new one?",
                    reply_markup=build_timer_keyboard(0, 0, 0)
                )
        except asyncio.CancelledError:
            pass

    timer.task = asyncio.create_task(notify())
    
    time_str = format_time_display(settings["hours"], settings["minutes"], settings["seconds"])
    sent_message = await callback.message.answer(
        f"⏳ Timer for {time_str} started!",
        reply_markup=build_stop_timer_keyboard()
    )
    
    # Store message ID for later reference
    timer.message_id = sent_message.message_id
    
    await callback.answer()


@router.callback_query(F.data == "timer_stop_active")
async def stop_active_timer(callback: CallbackQuery):
    """Stop the currently running timer from the stop button"""
    user_id = callback.from_user.id
    timer = active_timers.get(user_id)

    if not timer:
        await callback.answer("⚠️ No active timer.", show_alert=True)
        return

    # Cancel the timer task
    if timer.task:
        timer.task.cancel()
    
    # Calculate elapsed time
    elapsed = (datetime.now() - timer.start_time).total_seconds() if timer.start_time else 0
    remaining = timer.remaining_seconds()
    
    # Remove from active timers
    del active_timers[user_id]
    timer_settings[user_id] = {"hours": 0, "minutes": 0, "seconds": 0}
    
    # Remove the stop button
    await callback.message.edit_reply_markup(reply_markup=None)
    
    # Send confirmation message
    await callback.message.answer(
        "⏹ Timer stopped.\n\n🔄 Do you want to start a new one?",
        reply_markup=build_timer_keyboard(0, 0, 0)
    )
    await callback.answer("Timer stopped!")


@router.callback_query(F.data == "timer_stop")
async def stop_timer(callback: CallbackQuery):
    """Stop the active timer (from main menu)"""
    user_id = callback.from_user.id
    timer = active_timers.get(user_id)

    if not timer:
        await callback.answer("⚠️ No active timer.", show_alert=True)
        return

    if timer.task:
        timer.task.cancel()
    
    # Try to remove the stop button from the timer message
    try:
        if timer.message_id:
            await callback.bot.edit_message_reply_markup(
                chat_id=callback.message.chat.id,
                message_id=timer.message_id,
                reply_markup=None
            )
    except Exception:
        pass  # Message might be deleted or inaccessible
    
    del active_timers[user_id]

    timer_settings[user_id] = {"hours": 0, "minutes": 0, "seconds": 0}
    await callback.message.answer(
        "⏹ Timer stopped.\n\n🔄 Do you want to start a new one?",
        reply_markup=build_timer_keyboard(0, 0, 0)
    )
    await callback.answer()


# ==========================================
# PRESET MENU HANDLERS
# ==========================================

@router.callback_query(F.data == "timer_presets_menu")
async def presets_menu(callback: CallbackQuery):
    """Show presets management menu"""
    await callback.message.edit_text(
        "⚙️ Timer Preset Settings",
        reply_markup=presets_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "timer_go_main")
async def go_main(callback: CallbackQuery):
    """Return to main timer interface"""
    user_id = callback.from_user.id
    init_timer_settings(user_id)
    await refresh_timer_message(callback, user_id)
    await callback.answer()


# ==========================================
# ADD PRESET HANDLERS
# ==========================================

@router.callback_query(F.data == "timer_preset_add")
async def preset_add(callback: CallbackQuery, state: FSMContext):
    """Start preset creation process"""
    await state.set_state(TimerPresetForm.waiting_for_name)
    await callback.message.edit_text("✏️ Enter the preset name (e.g., Plank, Rest):")
    await callback.answer()


@router.message(TimerPresetForm.waiting_for_name)
async def process_preset_name(message: Message, state: FSMContext):
    """Process preset name input"""
    await state.update_data(name=message.text)
    await state.set_state(TimerPresetForm.waiting_for_time)
    await message.answer(
        "⏱ Enter the time in format HH:MM:SS or MM:SS or SS\n"
        "(e.g., 8:00 or 0:8:0 or 480)"
    )


@router.message(TimerPresetForm.waiting_for_time)
async def process_preset_time(message: Message, state: FSMContext):
    """Process preset time input"""
    user_id = message.from_user.id
    
    # Parse time string
    time_tuple, error_msg = parse_time_string(message.text)
    
    if not time_tuple:
        await message.answer(error_msg)
        return
    
    hours, minutes, seconds = time_tuple
    
    # Get preset name from state
    data = await state.get_data()
    name = data.get('name', 'Unnamed')
    
    # Check if this is a replace operation
    replace_id = data.get('replace_id')
    
    if replace_id:
        # Update existing preset
        preset = update_timer_preset(replace_id, name, hours, minutes, seconds)
        action_text = "✅ Preset updated!"
    else:
        # Create new preset
        preset = add_timer_preset(user_id, name, hours, minutes, seconds)
        action_text = "✅ Preset added!"
    
    await state.clear()
    
    time_str = format_time_display(hours, minutes, seconds)
    await message.answer(
        f"{action_text}\n\nName: {name}\nTime: {time_str}",
        reply_markup=presets_menu_keyboard()
    )


# ==========================================
# LIST PRESETS HANDLERS
# ==========================================

@router.callback_query(F.data == "timer_preset_list")
async def preset_list(callback: CallbackQuery):
    """Show list of user's presets"""
    user_id = callback.from_user.id
    presets = get_user_timer_presets(user_id)
    
    if not presets:
        await callback.answer("No presets found!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📋 Your presets (click to load):",
        reply_markup=preset_list_keyboard(user_id, "load")
    )
    await callback.answer()


@router.callback_query(F.data.startswith("timer_preset_load_"))
async def preset_load(callback: CallbackQuery):
    """Load a preset into the timer"""
    user_id = callback.from_user.id
    preset_id = int(callback.data.split("_")[-1])
    preset = get_timer_preset_by_id(preset_id)
    
    if not preset:
        await callback.answer("❌ Preset not found!", show_alert=True)
        return
    
    # Verify ownership
    if preset.user_id != user_id:
        await callback.answer("❌ Access denied!", show_alert=True)
        return
    
    # Load preset into settings
    timer_settings[user_id] = {
        "hours": preset.hours,
        "minutes": preset.minutes,
        "seconds": preset.seconds
    }
    
    await callback.message.edit_text(
        f"✅ Loaded preset: {preset.name}",
        reply_markup=build_timer_keyboard(preset.hours, preset.minutes, preset.seconds)
    )
    await callback.answer()


# ==========================================
# REPLACE PRESET HANDLERS
# ==========================================

@router.callback_query(F.data == "timer_preset_replace")
async def preset_replace_menu(callback: CallbackQuery):
    """Show menu to select preset for replacement"""
    user_id = callback.from_user.id
    presets = get_user_timer_presets(user_id)
    
    if not presets:
        await callback.answer("No presets to replace!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "✏️ Select preset to replace:",
        reply_markup=preset_list_keyboard(user_id, "replace")
    )
    await callback.answer()


@router.callback_query(F.data.startswith("timer_preset_replace_"))
async def preset_replace_confirm(callback: CallbackQuery, state: FSMContext):
    """Start replace process for selected preset"""
    preset_id = int(callback.data.split("_")[-1])
    await state.update_data(replace_id=preset_id)
    await state.set_state(TimerPresetForm.waiting_for_name)
    await callback.message.edit_text("✏️ Enter the new preset name:")
    await callback.answer()


# ==========================================
# DELETE PRESET HANDLERS
# ==========================================

@router.callback_query(F.data == "timer_preset_delete")
async def preset_delete_menu(callback: CallbackQuery):
    """Show menu to select preset for deletion"""
    user_id = callback.from_user.id
    presets = get_user_timer_presets(user_id)
    
    if not presets:
        await callback.answer("No presets to delete!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🗑 Select preset to delete:",
        reply_markup=preset_list_keyboard(user_id, "delete")
    )
    await callback.answer()


@router.callback_query(F.data.startswith("timer_preset_delete_"))
async def preset_delete_confirm(callback: CallbackQuery):
    """Delete selected preset"""
    user_id = callback.from_user.id
    preset_id = int(callback.data.split("_")[-1])
    
    # Verify ownership before deletion
    preset = get_timer_preset_by_id(preset_id)
    if not preset or preset.user_id != user_id:
        await callback.answer("❌ Access denied!", show_alert=True)
        return
    
    delete_timer_preset(preset_id)
    await callback.message.edit_text(
        "✅ Preset deleted!",
        reply_markup=presets_menu_keyboard()
    )
    await callback.answer()


# ==========================================
# NO-OP HANDLER
# ==========================================

@router.callback_query(F.data == "timer_noop")
async def noop(callback: CallbackQuery):
    """No operation - for display-only buttons"""
    await callback.answer()