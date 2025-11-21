import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from .services import timers, settings, Timer
from .keyboards import (
    build_timer_keyboard, 
    build_presets_menu_keyboard,
    build_presets_list_keyboard
)
from .database import (
    add_preset,
    get_user_presets,
    update_preset,
    delete_preset,
    get_presets_count
)

router = Router()


class PresetStates(StatesGroup):
    waiting_for_preset_name = State()
    waiting_for_preset_time = State()
    waiting_for_replace_index = State()
    waiting_for_replace_name = State()
    waiting_for_replace_time = State()


async def refresh_config_message(callback: CallbackQuery, user_id: int):
    await callback.message.edit_text(
        "Hello! 👋 Set your timer:",
        reply_markup=build_timer_keyboard(user_id)
    )

# ==== Start ====
@router.message(Command("timer"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    settings[user_id] = {"hours": 0, "minutes": 0, "seconds": 0}
    await message.answer("Hello! 👋 Set your timer:", reply_markup=build_timer_keyboard(user_id))

# ==== Increment / Decrement Handlers ====
@router.callback_query(F.data == "add_hour")
async def add_hour(callback: CallbackQuery):
    user_id = callback.from_user.id
    settings[user_id]["hours"] += 1
    await refresh_config_message(callback, user_id)
    await callback.answer("➕ 1 hour")

@router.callback_query(F.data == "add_minute")
async def add_minute(callback: CallbackQuery):
    user_id = callback.from_user.id
    if settings[user_id]["minutes"] < 59:
        settings[user_id]["minutes"] += 1
    else:
        settings[user_id]["minutes"] = 0
        settings[user_id]["hours"] += 1
    await refresh_config_message(callback, user_id)
    await callback.answer("➕ 1 minute")

@router.callback_query(F.data == "add_second")
async def add_second(callback: CallbackQuery):
    user_id = callback.from_user.id
    if settings[user_id]["seconds"] < 59:
        settings[user_id]["seconds"] += 1
    else:
        settings[user_id]["seconds"] = 0
        if settings[user_id]["minutes"] < 59:
            settings[user_id]["minutes"] += 1
        else:
            settings[user_id]["minutes"] = 0
            settings[user_id]["hours"] += 1
    await refresh_config_message(callback, user_id)
    await callback.answer("➕ 1 second")

# ==== Decrement ====
@router.callback_query(F.data == "sub_hour")
async def sub_hour(callback: CallbackQuery):
    user_id = callback.from_user.id
    if settings[user_id]["hours"] > 0:
        settings[user_id]["hours"] -= 1
    await refresh_config_message(callback, user_id)
    await callback.answer("➖ 1 hour")

@router.callback_query(F.data == "sub_minute")
async def sub_minute(callback: CallbackQuery):
    user_id = callback.from_user.id
    if settings[user_id]["minutes"] > 0:
        settings[user_id]["minutes"] -= 1
    elif settings[user_id]["hours"] > 0:
        settings[user_id]["hours"] -= 1
        settings[user_id]["minutes"] = 59
    await refresh_config_message(callback, user_id)
    await callback.answer("➖ 1 minute")

@router.callback_query(F.data == "sub_second")
async def sub_second(callback: CallbackQuery):
    user_id = callback.from_user.id
    if settings[user_id]["seconds"] > 0:
        settings[user_id]["seconds"] -= 1
    elif settings[user_id]["minutes"] > 0:
        settings[user_id]["minutes"] -= 1
        settings[user_id]["seconds"] = 59
    elif settings[user_id]["hours"] > 0:
        settings[user_id]["hours"] -= 1
        settings[user_id]["minutes"] = 59
        settings[user_id]["seconds"] = 59
    await refresh_config_message(callback, user_id)
    await callback.answer("➖ 1 second")

# ==== Start Timer ====
@router.callback_query(F.data == "start_timer")
async def start_timer(callback: CallbackQuery):
    user_id = callback.from_user.id
    s = settings[user_id]
    total_seconds = s["hours"] * 3600 + s["minutes"] * 60 + s["seconds"]

    if total_seconds <= 0:
        await callback.answer("⚠️ Time not set", show_alert=True)
        return

    timer = Timer(total_seconds)
    timer.start()
    timers[user_id] = timer

    async def notify():
        try:
            await asyncio.sleep(total_seconds)
            if user_id in timers and timers[user_id] == timer:
                del timers[user_id]
                settings[user_id] = {"hours": 0, "minutes": 0, "seconds": 0}
                await callback.message.answer(
                    "✅ Timer completed!\n\n🔄 Want to start a new one?",
                    reply_markup=build_timer_keyboard(user_id)
                )
        except asyncio.CancelledError:
            pass

    timer.task = asyncio.create_task(notify())
    await callback.message.answer(f"⏳ Timer for {total_seconds} seconds started!")
    await callback.answer()

# ==== Stop Timer ====
@router.callback_query(F.data == "stop_timer")
async def stop_timer(callback: CallbackQuery):
    user_id = callback.from_user.id
    timer = timers.get(user_id)

    if not timer:
        await callback.answer("⚠️ No active timer.", show_alert=True)
        return

    if timer.task:
        timer.task.cancel()
    del timers[user_id]
    settings[user_id] = {"hours": 0, "minutes": 0, "seconds": 0}

    await callback.message.answer(
        "⏹ Timer stopped.\n\n🔄 Want to start a new one?",
        reply_markup=build_timer_keyboard(user_id)
    )
    await callback.answer()

# ==== No-op ====
@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    await callback.answer()


# ========== PRESETS HANDLERS ==========

@router.callback_query(F.data == "presets_menu")
async def presets_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "⚙️ Preset Settings",
        reply_markup=build_presets_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "preset_back")
async def preset_back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    await callback.message.edit_text(
        "Hello! 👋 Set your timer:",
        reply_markup=build_timer_keyboard(user_id)
    )
    await callback.answer()


@router.callback_query(F.data == "preset_add")
async def preset_add(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    presets_count = await get_presets_count(user_id)
    
    if presets_count >= 10:
        await callback.answer("⚠️ Maximum 10 presets allowed", show_alert=True)
        return
    
    await state.set_state(PresetStates.waiting_for_preset_name)
    await callback.message.edit_text("Enter preset name (e.g., 'Plank'):")
    await callback.answer()


@router.message(PresetStates.waiting_for_preset_name)
async def process_preset_name(message: Message, state: FSMContext):
    name = message.text.strip()
    
    if len(name) > 50:
        await message.answer("❌ Name too long (max 50 characters). Try again:")
        return
    
    if not name:
        await message.answer("❌ Name cannot be empty. Try again:")
        return
    
    await state.update_data(preset_name=name)
    await state.set_state(PresetStates.waiting_for_preset_time)
    await message.answer("Enter time in format: HH:MM:SS or MM:SS or just seconds\nExample: 8:00 (8 minutes)")


@router.message(PresetStates.waiting_for_preset_time)
async def process_preset_time(message: Message, state: FSMContext):
    time_str = message.text.strip()
    
    try:
        # Parse different time formats
        parts = time_str.split(':')
        
        if len(parts) == 3:  # HH:MM:SS
            h, m, s = map(int, parts)
        elif len(parts) == 2:  # MM:SS
            h = 0
            m, s = map(int, parts)
        elif len(parts) == 1:  # Just seconds
            h = 0
            m = 0
            s = int(parts[0])
        else:
            raise ValueError
        
        total_seconds = h * 3600 + m * 60 + s
        
        if total_seconds <= 0:
            raise ValueError
        
        if total_seconds > 86400:  # 24 hours
            await message.answer("❌ Time too long (max 24 hours). Try again:")
            return
        
    except (ValueError, IndexError):
        await message.answer("❌ Invalid format. Use HH:MM:SS, MM:SS, or seconds. Try again:")
        return
    
    data = await state.get_data()
    preset_name = data.get("preset_name")
    
    user_id = message.from_user.id
    success = await add_preset(user_id, preset_name, total_seconds)
    
    if not success:
        await message.answer("❌ Error saving preset. Please try again.")
        await state.clear()
        return
    
    h_display = total_seconds // 3600
    m_display = (total_seconds % 3600) // 60
    s_display = total_seconds % 60
    
    await message.answer(
        f"✅ Preset added!\n\n"
        f"Name: {preset_name}\n"
        f"Time: {h_display}h {m_display}m {s_display}s",
        reply_markup=build_presets_menu_keyboard()
    )
    await state.clear()


@router.callback_query(F.data == "preset_list")
async def preset_list(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_presets = await get_user_presets(user_id)
    
    if not user_presets:
        await callback.message.edit_text(
            "📋 No presets saved.\n\nClick Add to create your first preset!",
            reply_markup=build_presets_menu_keyboard()
        )
    else:
        await callback.message.edit_text(
            "📋 Your presets (click to load):",
            reply_markup=build_presets_list_keyboard(user_id, user_presets, action="load")
        )
    await callback.answer()


@router.callback_query(F.data.startswith("preset_load_"))
async def preset_load(callback: CallbackQuery):
    user_id = callback.from_user.id
    preset_id = int(callback.data.split("_")[2])
    
    user_presets = await get_user_presets(user_id)
    preset = next((p for p in user_presets if p["id"] == preset_id), None)
    
    if not preset:
        await callback.answer("❌ Preset not found", show_alert=True)
        return
    
    total_seconds = preset["seconds"]
    
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    settings[user_id] = {
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds
    }
    
    await callback.message.edit_text(
        f"✅ Loaded preset: {preset['name']}",
        reply_markup=build_timer_keyboard(user_id)
    )
    await callback.answer()


@router.callback_query(F.data == "preset_replace")
async def preset_replace(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_presets = await get_user_presets(user_id)
    
    if not user_presets:
        await callback.message.edit_text(
            "📋 No presets to replace.",
            reply_markup=build_presets_menu_keyboard()
        )
    else:
        await callback.message.edit_text(
            "✏️ Select preset to replace:",
            reply_markup=build_presets_list_keyboard(user_id, user_presets, action="replace")
        )
    await callback.answer()


@router.callback_query(F.data.startswith("preset_replace_"))
async def preset_replace_select(callback: CallbackQuery, state: FSMContext):
    preset_id = int(callback.data.split("_")[2])
    
    await state.update_data(replace_id=preset_id)
    await state.set_state(PresetStates.waiting_for_replace_name)
    await callback.message.edit_text("Enter new preset name:")
    await callback.answer()


@router.message(PresetStates.waiting_for_replace_name)
async def process_replace_name(message: Message, state: FSMContext):
    name = message.text.strip()
    
    if len(name) > 50:
        await message.answer("❌ Name too long (max 50 characters). Try again:")
        return
    
    if not name:
        await message.answer("❌ Name cannot be empty. Try again:")
        return
    
    await state.update_data(preset_name=name)
    await state.set_state(PresetStates.waiting_for_replace_time)
    await message.answer("Enter new time (HH:MM:SS, MM:SS, or seconds):")


@router.message(PresetStates.waiting_for_replace_time)
async def process_replace_time(message: Message, state: FSMContext):
    time_str = message.text.strip()
    
    try:
        parts = time_str.split(':')
        
        if len(parts) == 3:
            h, m, s = map(int, parts)
        elif len(parts) == 2:
            h = 0
            m, s = map(int, parts)
        elif len(parts) == 1:
            h = 0
            m = 0
            s = int(parts[0])
        else:
            raise ValueError
        
        total_seconds = h * 3600 + m * 60 + s
        
        if total_seconds <= 0 or total_seconds > 86400:
            raise ValueError
        
    except (ValueError, IndexError):
        await message.answer("❌ Invalid format. Try again:")
        return
    
    data = await state.get_data()
    preset_name = data.get("preset_name")
    preset_id = data.get("replace_id")
    
    user_id = message.from_user.id
    success = await update_preset(preset_id, user_id, preset_name, total_seconds)
    
    if not success:
        await message.answer("❌ Error updating preset")
        await state.clear()
        return
    
    h_display = total_seconds // 3600
    m_display = (total_seconds % 3600) // 60
    s_display = total_seconds % 60
    
    await message.answer(
        f"✅ Preset replaced!\n\n"
        f"Name: {preset_name}\n"
        f"Time: {h_display}h {m_display}m {s_display}s",
        reply_markup=build_presets_menu_keyboard()
    )
    await state.clear()


@router.callback_query(F.data == "preset_delete")
async def preset_delete(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_presets = await get_user_presets(user_id)
    
    if not user_presets:
        await callback.message.edit_text(
            "📋 No presets to delete.",
            reply_markup=build_presets_menu_keyboard()
        )
    else:
        await callback.message.edit_text(
            "🗑 Select preset to delete:",
            reply_markup=build_presets_list_keyboard(user_id, user_presets, action="delete")
        )
    await callback.answer()


@router.callback_query(F.data.startswith("preset_delete_"))
async def preset_delete_confirm(callback: CallbackQuery):
    user_id = callback.from_user.id
    preset_id = int(callback.data.split("_")[2])
    
    user_presets = await get_user_presets(user_id)
    preset = next((p for p in user_presets if p["id"] == preset_id), None)
    
    if not preset:
        await callback.answer("❌ Preset not found", show_alert=True)
        return
    
    success = await delete_preset(preset_id, user_id)
    
    if success:
        await callback.message.edit_text(
            f"✅ Preset '{preset['name']}' deleted!",
            reply_markup=build_presets_menu_keyboard()
        )
    else:
        await callback.answer("❌ Error deleting preset", show_alert=True)
    
    await callback.answer()