import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from .services import timers, settings, Timer, presets
from .keyboards import (
    build_timer_keyboard, 
    build_presets_menu_keyboard,
    build_presets_list_keyboard
)
from datetime import time

from .services import (
    schedules, user_states, day_map, day_names,
    TimeFormatFilter, reminder_loop
)
from .keyboards import create_main_keyboard, create_day_keyboard, create_schedule_keyboard

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
    user_presets = presets.get(user_id, [])
    
    if len(user_presets) >= 10:
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
    if user_id not in presets:
        presets[user_id] = []
    
    presets[user_id].append({
        "name": preset_name,
        "seconds": total_seconds
    })
    
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
    user_presets = presets.get(user_id, [])
    
    if not user_presets:
        await callback.message.edit_text(
            "📋 No presets saved.\n\nClick Add to create your first preset!",
            reply_markup=build_presets_menu_keyboard()
        )
    else:
        await callback.message.edit_text(
            "📋 Your presets (click to load):",
            reply_markup=build_presets_list_keyboard(user_id, action="load")
        )
    await callback.answer()


@router.callback_query(F.data.startswith("preset_load_"))
async def preset_load(callback: CallbackQuery):
    user_id = callback.from_user.id
    preset_index = int(callback.data.split("_")[2])
    
    user_presets = presets.get(user_id, [])
    if preset_index >= len(user_presets):
        await callback.answer("❌ Preset not found", show_alert=True)
        return
    
    preset = user_presets[preset_index]
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
    user_presets = presets.get(user_id, [])
    
    if not user_presets:
        await callback.message.edit_text(
            "📋 No presets to replace.",
            reply_markup=build_presets_menu_keyboard()
        )
    else:
        await callback.message.edit_text(
            "✏️ Select preset to replace:",
            reply_markup=build_presets_list_keyboard(user_id, action="replace")
        )
    await callback.answer()


@router.callback_query(F.data.startswith("preset_replace_"))
async def preset_replace_select(callback: CallbackQuery, state: FSMContext):
    preset_index = int(callback.data.split("_")[2])
    
    await state.update_data(replace_index=preset_index)
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
    replace_index = data.get("replace_index")
    
    user_id = message.from_user.id
    
    if user_id not in presets or replace_index >= len(presets[user_id]):
        await message.answer("❌ Preset not found")
        await state.clear()
        return
    
    presets[user_id][replace_index] = {
        "name": preset_name,
        "seconds": total_seconds
    }
    
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
    user_presets = presets.get(user_id, [])
    
    if not user_presets:
        await callback.message.edit_text(
            "📋 No presets to delete.",
            reply_markup=build_presets_menu_keyboard()
        )
    else:
        await callback.message.edit_text(
            "🗑 Select preset to delete:",
            reply_markup=build_presets_list_keyboard(user_id, action="delete")
        )
    await callback.answer()


@router.callback_query(F.data.startswith("preset_delete_"))
async def preset_delete_confirm(callback: CallbackQuery):
    user_id = callback.from_user.id
    preset_index = int(callback.data.split("_")[2])
    
    user_presets = presets.get(user_id, [])
    if preset_index >= len(user_presets):
        await callback.answer("❌ Preset not found", show_alert=True)
        return
    
    deleted_preset = user_presets.pop(preset_index)
    
    await callback.message.edit_text(
        f"✅ Preset '{deleted_preset['name']}' deleted!",
        reply_markup=build_presets_menu_keyboard()
    )
    await callback.answer()


# ===== Хэндлеры =====
@router.message(Command("make_a_plan"))
async def start(message: Message):
    chat_id = message.chat.id
    user_states[chat_id] = {'state': 'idle'}
    await message.answer("Hello! Choose an action:", reply_markup=create_main_keyboard())


@router.callback_query(F.data.startswith('action_'))
async def handle_action(callback: CallbackQuery):
    action = callback.data.split('_')[1]
    chat_id = callback.message.chat.id

    if action == 'list':
        if chat_id not in schedules or not schedules[chat_id]:
            await callback.message.edit_text("No trainings added", reply_markup=create_main_keyboard())
            return
        sorted_schedules = sorted(schedules[chat_id], key=lambda x: x[0])
        lst = '\n'.join(f"{day_names[d]} {t.hour:02}:{t.minute:02}" for d, t, _ in sorted_schedules)
        await callback.message.edit_text(f"Your trainings:\n{lst}", reply_markup=create_main_keyboard())

    elif action == 'add':
        user_states[chat_id] = {'state': 'select_day_add'}
        await callback.message.edit_text("Choose day of the week:", reply_markup=create_day_keyboard('add'))

    elif action == 'replace':
        keyboard = create_schedule_keyboard(chat_id)
        if not keyboard:
            await callback.message.edit_text("No trainings to replace", reply_markup=create_main_keyboard())
            return
        user_states[chat_id] = {'state': 'select_num_replace'}
        await callback.message.edit_text("Choose training to replace:", reply_markup=keyboard)

    await callback.answer()


@router.callback_query(F.data.startswith('replace_num_'))
async def handle_replace_num(callback: CallbackQuery):
    num = int(callback.data.split('_')[2])
    chat_id = callback.message.chat.id

    if chat_id not in schedules or num < 0 or num >= len(schedules[chat_id]):
        await callback.message.edit_text("Invalid training number", reply_markup=create_main_keyboard())
        user_states[chat_id] = {'state': 'idle'}
        return

    user_states[chat_id] = {'state': 'select_day_replace', 'selected_num': num}
    await callback.message.edit_text("Choose day of the week:", reply_markup=create_day_keyboard('replace', num))
    await callback.answer()


@router.callback_query(F.data.startswith('add_day_') | F.data.startswith('replace_day_'))
async def handle_day_selection(callback: CallbackQuery):
    parts = callback.data.split('_')
    action = parts[0]
    day_code = parts[2]
    chat_id = callback.message.chat.id

    if day_code not in day_map:
        await callback.message.edit_text("Invalid day", reply_markup=create_main_keyboard())
        user_states[chat_id] = {'state': 'idle'}
        return

    num = int(parts[3]) if action == 'replace' and len(parts) > 3 else None
    user_states[chat_id].update({
        'state': f'enter_time_{action}',
        'selected_day': day_code,
        'selected_num': num
    })

    await callback.message.edit_text("Enter time (e.g., 18:30):")
    await callback.answer()


@router.message(TimeFormatFilter())
async def handle_time_input(message: Message):
    chat_id = message.chat.id

    if chat_id not in user_states or user_states[chat_id]['state'] not in ['enter_time_add', 'enter_time_replace']:
        await message.answer("Please use buttons to start the process", reply_markup=create_main_keyboard())
        return

    time_str = message.text
    try:
        h, m = map(int, time_str.split(':'))
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError
        train_time = time(h, m)
    except:
        await message.answer("Invalid time format (HH:MM, 00:00-23:59)", reply_markup=create_main_keyboard())
        user_states[chat_id] = {'state': 'idle'}
        return

    state = user_states[chat_id]['state']
    day_code = user_states[chat_id]['selected_day']
    weekday = day_map[day_code]

    if state == 'enter_time_add':
        if chat_id not in schedules:
            schedules[chat_id] = []
        if len(schedules[chat_id]) >= 5:
            lst = '\n'.join(f"{day_names[d]} {t.hour:02}:{t.minute:02}" for d, t, _ in schedules[chat_id])
            await message.answer(f"Already 5 trainings:\n{lst}\nChoose Replace to modify", reply_markup=create_main_keyboard())
            user_states[chat_id] = {'state': 'idle'}
            return

        task = asyncio.create_task(reminder_loop(message, weekday, train_time))
        schedules[chat_id].append((weekday, train_time, task))
        await message.answer("Training added!", reply_markup=create_main_keyboard())

    else:  # enter_time_replace
        num = user_states[chat_id]['selected_num']
        if chat_id not in schedules or num < 0 or num >= len(schedules[chat_id]):
            await message.answer("Invalid training number", reply_markup=create_main_keyboard())
            user_states[chat_id] = {'state': 'idle'}
            return

        old_task = schedules[chat_id][num][2]
        old_task.cancel()
        try:
            await old_task
        except asyncio.CancelledError:
            pass

        task = asyncio.create_task(reminder_loop(message, weekday, train_time))
        schedules[chat_id][num] = (weekday, train_time, task)
        await message.answer("Training replaced!", reply_markup=create_main_keyboard())

    user_states[chat_id] = {'state': 'idle'}