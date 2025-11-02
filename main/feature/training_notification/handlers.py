import re
import asyncio
from datetime import time
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from .keyboards import (
    create_main_keyboard,
    create_change_keyboard,
    create_day_keyboard,
    create_reminder_keyboard,
    create_schedule_keyboard,
    format_reminder,
    day_names,
    day_codes
)
from .database import (
    init_db,
    save_training,
    load_trainings,
    update_training,
    delete_training
)
from .services import (
    reminder_loop,
    load_schedules_from_db,
    get_schedules,
    add_schedule,
    update_schedule,
    delete_schedule
)
from .states import NotificationStates

router = Router()

day_map = {'Mo': 0, 'Tu': 1, 'We': 2, 'Th': 3, 'Fr': 4, 'Sa': 5, 'Su': 6}


@router.message(Command("notification"))
async def notification_start(message: Message, state: FSMContext):
    """Handle /notification command"""
    chat_id = message.from_user.id
    
    # Initialize database
    init_db()
    
    # Load existing schedules
    load_schedules_from_db(message.bot, chat_id)
    
    await state.clear()
    
    await message.answer(
        "🔔 <b>Training Notifications</b>\n\n"
        "Manage your training reminders. Set custom reminder times for each workout!\n\n"
        "Choose an action:",
        reply_markup=create_main_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.in_(['notif_action_back', 'notif_back_to_main']))
async def handle_back_to_main(callback: CallbackQuery, state: FSMContext):
    """Handle back to main menu"""
    await state.clear()
    
    try:
        await callback.message.edit_text(
            "🔔 <b>Training Notifications</b>\n\n"
            "Manage your training reminders. Set custom reminder times for each workout!\n\n"
            "Choose an action:",
            reply_markup=create_main_keyboard(),
            parse_mode="HTML"
        )
    except Exception:
        await callback.message.answer(
            "🔔 <b>Training Notifications</b>\n\n"
            "Manage your training reminders. Set custom reminder times for each workout!\n\n"
            "Choose an action:",
            reply_markup=create_main_keyboard(),
            parse_mode="HTML"
        )
    
    await callback.answer()


@router.callback_query(F.data == 'notif_back_to_change')
async def handle_back_to_change(callback: CallbackQuery, state: FSMContext):
    """Handle back to change menu"""
    await state.clear()
    
    try:
        await callback.message.edit_text(
            "🔧 <b>Change Trainings</b>\n\n"
            "What would you like to do?",
            reply_markup=create_change_keyboard(),
            parse_mode="HTML"
        )
    except Exception:
        await callback.message.answer(
            "🔧 <b>Change Trainings</b>\n\n"
            "What would you like to do?",
            reply_markup=create_change_keyboard(),
            parse_mode="HTML"
        )
    
    await callback.answer()


@router.callback_query(F.data.startswith('notif_action_'))
async def handle_action(callback: CallbackQuery, state: FSMContext):
    """Handle main menu actions"""
    action = callback.data.split('_')[2]
    chat_id = callback.from_user.id
    
    if action == 'back':
        return
    
    if action == 'change':
        await state.clear()
        try:
            await callback.message.edit_text(
                "🔧 <b>Change Trainings</b>\n\n"
                "What would you like to do?",
                reply_markup=create_change_keyboard(),
                parse_mode="HTML"
            )
        except Exception:
            pass
    
    elif action == 'list':
        schedules = get_schedules(chat_id)
        
        if not schedules:
            try:
                await callback.message.edit_text(
                    "📋 <b>Your Training Notifications</b>\n\n"
                    "No trainings added yet.\n\n"
                    "💡 <i>Use 'Add Training' to create your first notification.</i>",
                    reply_markup=create_main_keyboard(),
                    parse_mode="HTML"
                )
            except Exception:
                pass
            await callback.answer()
            return
        
        sorted_schedules = sorted(schedules, key=lambda x: x[0])
        lst = ''.join([f"• {day_names[d]} {t.hour:02}:{t.minute:02} ({format_reminder(r)} before)\n" 
                       for d, t, r, _ in sorted_schedules])
        
        try:
            await callback.message.edit_text(
                f"📋 <b>Your Training Notifications</b>\n\n{lst}\n"
                "💡 You'll receive reminders at your chosen times before each training session.",
                reply_markup=create_main_keyboard(),
                parse_mode="HTML"
            )
        except Exception:
            pass
    
    elif action == 'add':
        await state.update_data(action='add')
        try:
            await callback.message.edit_text(
                "📅 <b>Add Training Notification</b>\n\n"
                "Choose the day of the week for your training:",
                reply_markup=create_day_keyboard('add'),
                parse_mode="HTML"
            )
        except Exception:
            pass
    
    elif action == 'replace':
        schedules = get_schedules(chat_id)
        keyboard = create_schedule_keyboard(schedules, 'replace')
        
        if not keyboard:
            try:
                await callback.message.edit_text(
                    "✏️ <b>Replace Training Notification</b>\n\n"
                    "No trainings to replace.\n\n"
                    "💡 <i>Use 'Add Training' to create notifications first.</i>",
                    reply_markup=create_change_keyboard(),
                    parse_mode="HTML"
                )
            except Exception:
                pass
            await callback.answer()
            return
        
        try:
            await callback.message.edit_text(
                "✏️ <b>Replace Training Notification</b>\n\n"
                "Select the notification you want to replace:",
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        except Exception:
            pass
    
    elif action == 'delete':
        schedules = get_schedules(chat_id)
        keyboard = create_schedule_keyboard(schedules, 'delete')
        
        if not keyboard:
            try:
                await callback.message.edit_text(
                    "🗑 <b>Delete Training Notification</b>\n\n"
                    "No trainings to delete.\n\n"
                    "💡 <i>Use 'Add Training' to create notifications first.</i>",
                    reply_markup=create_change_keyboard(),
                    parse_mode="HTML"
                )
            except Exception:
                pass
            await callback.answer()
            return
        
        try:
            await callback.message.edit_text(
                "🗑 <b>Delete Training Notification</b>\n\n"
                "Select the notification you want to delete:",
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        except Exception:
            pass
    
    await callback.answer()


@router.callback_query(F.data.startswith('notif_replace_num_'))
async def handle_replace_num(callback: CallbackQuery, state: FSMContext):
    """Handle replace training number selection"""
    num = int(callback.data.split('_')[3])
    chat_id = callback.from_user.id
    schedules = get_schedules(chat_id)
    
    if num < 0 or num >= len(schedules):
        try:
            await callback.message.edit_text(
                "❌ Invalid training number",
                reply_markup=create_change_keyboard(),
                parse_mode="HTML"
            )
        except Exception:
            pass
        await state.clear()
        return
    
    await state.update_data(action='replace', selected_num=num)
    
    try:
        await callback.message.edit_text(
            "✏️ <b>Replace Training Notification</b>\n\n"
            "Choose the day of the week for your training:",
            reply_markup=create_day_keyboard('replace', num),
            parse_mode="HTML"
        )
    except Exception:
        pass
    
    await callback.answer()


@router.callback_query(F.data.startswith('notif_delete_num_'))
async def handle_delete_num(callback: CallbackQuery, state: FSMContext):
    """Handle delete training number selection"""
    num = int(callback.data.split('_')[3])
    chat_id = callback.from_user.id
    schedules = get_schedules(chat_id)
    
    if num < 0 or num >= len(schedules):
        try:
            await callback.message.edit_text(
                "❌ Invalid training number",
                reply_markup=create_change_keyboard(),
                parse_mode="HTML"
            )
        except Exception:
            pass
        await callback.answer()
        return
    
    # Get training info before deletion
    weekday, train_time, reminder_minutes, _ = schedules[num]
    day_name = day_names[weekday]
    time_str = f"{train_time.hour:02}:{train_time.minute:02}"
    
    # Delete from database and memory
    delete_training(chat_id, num)
    delete_schedule(chat_id, num)
    
    await state.clear()
    
    try:
        await callback.message.edit_text(
            f"✅ <b>Training Notification Deleted!</b>\n\n"
            f"Removed: <b>{day_name} {time_str}</b>\n\n"
            f"The notification has been removed from your schedule.",
            reply_markup=create_main_keyboard(),
            parse_mode="HTML"
        )
    except Exception:
        await callback.message.answer(
            f"✅ <b>Training Notification Deleted!</b>\n\n"
            f"Removed: <b>{day_name} {time_str}</b>\n\n"
            f"The notification has been removed from your schedule.",
            reply_markup=create_main_keyboard(),
            parse_mode="HTML"
        )
    
    await callback.answer()


@router.callback_query(F.data.startswith('notif_add_day_') | F.data.startswith('notif_replace_day_'))
async def handle_day_selection(callback: CallbackQuery, state: FSMContext):
    """Handle day selection"""
    parts = callback.data.split('_')
    action = parts[1]  # 'add' or 'replace'
    day_code = parts[3]
    
    if day_code not in day_map:
        try:
            await callback.message.edit_text(
                "❌ Invalid day",
                reply_markup=create_main_keyboard(),
                parse_mode="HTML"
            )
        except Exception:
            pass
        await state.clear()
        return
    
    data = await state.get_data()
    await state.update_data(selected_day=day_code)
    
    day_name = day_names[day_map[day_code]]
    
    try:
        await callback.message.edit_text(
            f"⏰ <b>Set Training Time</b>\n\n"
            f"Selected day: <b>{day_name}</b>\n\n"
            f"Please enter the training time in HH:MM format (24-hour):\n\n"
            f"<i>Examples: 09:30, 18:00, 20:15</i>",
            parse_mode="HTML"
        )
    except Exception:
        pass
    
    await state.set_state(NotificationStates.waiting_for_time)
    await callback.answer()


@router.message(NotificationStates.waiting_for_time)
async def handle_time_input(message: Message, state: FSMContext):
    """Handle time input"""
    # Check time format
    if not re.match(r'^\d{2}:\d{2}$', message.text):
        await message.answer(
            "❌ Invalid time format. Please use HH:MM (00:00-23:59)",
            parse_mode="HTML"
        )
        return
    
    try:
        h, m = map(int, message.text.split(':'))
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError
        train_time = time(h, m)
    except Exception:
        await message.answer(
            "❌ Invalid time format. Please use HH:MM (00:00-23:59)",
            parse_mode="HTML"
        )
        return
    
    data = await state.get_data()
    action = data.get('action', 'add')
    
    await state.update_data(selected_time=train_time)
    
    await message.answer(
        "🔔 <b>Select Reminder Time</b>\n\n"
        "When do you want to be reminded before your training?\n\n"
        "Choose a preset time or enter a custom value:",
        reply_markup=create_reminder_keyboard(action),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith('notif_add_reminder_') | F.data.startswith('notif_replace_reminder_'))
async def handle_reminder_selection(callback: CallbackQuery, state: FSMContext):
    """Handle reminder time selection"""
    parts = callback.data.split('_')
    action = parts[1]  # 'add' or 'replace'
    reminder_type = parts[3]
    
    if reminder_type == 'custom':
        await state.set_state(NotificationStates.waiting_for_custom_reminder)
        
        try:
            await callback.message.edit_text(
                "✏️ <b>Custom Reminder Time</b>\n\n"
                "Enter the number of minutes before training (1-1440):\n\n"
                "<i>Examples:\n"
                "• 15 = 15 minutes\n"
                "• 45 = 45 minutes\n"
                "• 90 = 1 hour 30 minutes</i>",
                parse_mode="HTML"
            )
        except Exception:
            pass
        
        await callback.answer()
        return
    
    reminder_minutes = int(reminder_type)
    await finalize_training(callback.from_user.id, callback.message, state, reminder_minutes)
    await callback.answer()


@router.message(NotificationStates.waiting_for_custom_reminder)
async def handle_custom_reminder_input(message: Message, state: FSMContext):
    """Handle custom reminder time input"""
    try:
        reminder_minutes = int(message.text)
        if not (1 <= reminder_minutes <= 1440):
            raise ValueError
    except Exception:
        await message.answer(
            "❌ Please enter a number between 1 and 1440 (minutes).",
            parse_mode="HTML"
        )
        return
    
    await finalize_training(message.from_user.id, message, state, reminder_minutes)


async def finalize_training(chat_id: int, message_obj, state: FSMContext, reminder_minutes: int):
    """Finalize training addition or replacement"""
    data = await state.get_data()
    
    day_code = data.get('selected_day')
    train_time = data.get('selected_time')
    action = data.get('action', 'add')
    
    if not day_code or not train_time:
        await message_obj.answer("❌ Error: Missing data. Please start again.")
        await state.clear()
        return
    
    weekday = day_map[day_code]
    reminder_str = format_reminder(reminder_minutes)
    
    if action == 'add':
        schedules = get_schedules(chat_id)
        
        if len(schedules) >= 5:
            lst = ''.join([f"• {day_names[d]} {t.hour:02}:{t.minute:02} ({format_reminder(r)} before)\n" 
                          for d, t, r, _ in schedules])
            
            await message_obj.answer(
                f"❌ <b>Maximum Trainings Reached</b>\n\n"
                f"Already 5 trainings:\n{lst}\n"
                f"💡 Use 'Replace Training' to modify existing notifications.",
                reply_markup=create_main_keyboard(),
                parse_mode="HTML"
            )
            await state.clear()
            return
        
        # Save to database
        save_training(chat_id, weekday, train_time, reminder_minutes)
        
        # Create background task
        task = asyncio.create_task(reminder_loop(message_obj.bot, chat_id, weekday, train_time, reminder_minutes))
        add_schedule(chat_id, weekday, train_time, reminder_minutes, task)
        
        await message_obj.answer(
            f"✅ <b>Training Notification Added!</b>\n\n"
            f"📅 Day: <b>{day_names[weekday]}</b>\n"
            f"⏰ Time: <b>{train_time.hour:02}:{train_time.minute:02}</b>\n"
            f"🔔 Reminder: <b>{reminder_str} before</b>\n\n"
            f"You'll be notified at the specified time! 🔔",
            reply_markup=create_main_keyboard(),
            parse_mode="HTML"
        )
    
    else:  # replace
        num = data.get('selected_num')
        schedules = get_schedules(chat_id)
        
        if num is None or num < 0 or num >= len(schedules):
            await message_obj.answer(
                "❌ Invalid training number",
                reply_markup=create_main_keyboard(),
                parse_mode="HTML"
            )
            await state.clear()
            return
        
        # Update in database
        update_training(chat_id, num, weekday, train_time, reminder_minutes)
        
        # Create new background task
        task = asyncio.create_task(reminder_loop(message_obj.bot, chat_id, weekday, train_time, reminder_minutes))
        update_schedule(chat_id, num, weekday, train_time, reminder_minutes, task)
        
        await message_obj.answer(
            f"✅ <b>Training Notification Replaced!</b>\n\n"
            f"📅 Day: <b>{day_names[weekday]}</b>\n"
            f"⏰ Time: <b>{train_time.hour:02}:{train_time.minute:02}</b>\n"
            f"🔔 Reminder: <b>{reminder_str} before</b>\n\n"
            f"You'll be notified at the specified time! 🔔",
            reply_markup=create_main_keyboard(),
            parse_mode="HTML"
        )
    
    await state.clear()