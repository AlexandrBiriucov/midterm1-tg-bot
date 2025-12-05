"""
Handlers for training notifications feature.
All database operations integrated via services module.
"""
import re
import asyncio
from datetime import time
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from localization.utils import t
from bot.features.dev1_workout_tracking.services import get_lang

from .keyboards import (
    create_main_keyboard,
    create_change_keyboard,
    create_day_keyboard,
    create_reminder_keyboard,
    create_schedule_keyboard,
    format_reminder,
    day_codes
)
from .services import (
    save_training,
    load_trainings,
    update_training,
    delete_training,
    get_notification_count,
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

# Maximum notifications per user
MAX_NOTIFICATIONS = 5


@router.message(Command("notification"))
async def notification_start(message: Message, state: FSMContext):
    """Handle /notification command"""
    lang = get_lang(message.from_user.id)
    await state.update_data(lang=lang)

    chat_id = message.from_user.id

    # Load existing schedules from unified database
    load_schedules_from_db(message.bot, chat_id)

    await state.clear()
    await state.update_data(lang=lang)

    await message.answer(
        t("notif_main_menu", lang),
        reply_markup=create_main_keyboard(lang),
        parse_mode="HTML"
    )


@router.callback_query(F.data.in_(['notif_action_back', 'notif_back_to_main']))
async def handle_back_to_main(callback: CallbackQuery, state: FSMContext):
    """Handle back to main menu"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    await state.clear()
    await state.update_data(lang=lang)

    try:
        await callback.message.edit_text(
            t("notif_main_menu", lang),
            reply_markup=create_main_keyboard(lang),
            parse_mode="HTML"
        )
    except Exception:
        await callback.message.answer(
            t("notif_main_menu", lang),
            reply_markup=create_main_keyboard(lang),
            parse_mode="HTML"
        )

    await callback.answer()


@router.callback_query(F.data == 'notif_back_to_change')
async def handle_back_to_change(callback: CallbackQuery, state: FSMContext):
    """Handle back to change menu"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    await state.clear()
    await state.update_data(lang=lang)

    try:
        await callback.message.edit_text(
            t("notif_change_menu", lang),
            reply_markup=create_change_keyboard(lang),
            parse_mode="HTML"
        )
    except Exception:
        await callback.message.answer(
            t("notif_change_menu", lang),
            reply_markup=create_change_keyboard(lang),
            parse_mode="HTML"
        )

    await callback.answer()


@router.callback_query(F.data.startswith('notif_action_'))
async def handle_action(callback: CallbackQuery, state: FSMContext):
    """Handle main menu actions"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    action = callback.data.split('_')[2]
    chat_id = callback.from_user.id

    if action == 'back':
        return

    if action == 'change':
        await state.clear()
        await state.update_data(lang=lang)
        try:
            await callback.message.edit_text(
                t("notif_change_menu", lang),
                reply_markup=create_change_keyboard(lang),
                parse_mode="HTML"
            )
        except Exception:
            pass

    elif action == 'list':
        schedules = get_schedules(chat_id)

        if not schedules:
            try:
                await callback.message.edit_text(
                    t("notif_list_empty", lang),
                    reply_markup=create_main_keyboard(lang),
                    parse_mode="HTML"
                )
            except Exception:
                pass
            await callback.answer()
            return

        sorted_schedules = sorted(schedules, key=lambda x: x[0])
        lst = ''.join([f"• {t(f'day_name_{d}', lang)} {tm.hour:02}:{tm.minute:02} ({format_reminder(r, lang)} {t('notif_before', lang)})\n"
                       for d, tm, r, _ in sorted_schedules])

        try:
            await callback.message.edit_text(
                t("notif_list_view", lang, schedules=lst),
                reply_markup=create_main_keyboard(lang),
                parse_mode="HTML"
            )
        except Exception:
            pass

    elif action == 'add':
        await state.update_data(action='add')
        try:
            await callback.message.edit_text(
                t("notif_add_select_day", lang),
                reply_markup=create_day_keyboard('add', lang),
                parse_mode="HTML"
            )
        except Exception:
            pass

    elif action == 'replace':
        schedules = get_schedules(chat_id)
        keyboard = create_schedule_keyboard(schedules, 'replace', lang)

        if not keyboard:
            try:
                await callback.message.edit_text(
                    t("notif_replace_empty", lang),
                    reply_markup=create_change_keyboard(lang),
                    parse_mode="HTML"
                )
            except Exception:
                pass
            await callback.answer()
            return

        try:
            await callback.message.edit_text(
                t("notif_replace_select", lang),
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        except Exception:
            pass

    elif action == 'delete':
        schedules = get_schedules(chat_id)
        keyboard = create_schedule_keyboard(schedules, 'delete', lang)

        if not keyboard:
            try:
                await callback.message.edit_text(
                    t("notif_delete_empty", lang),
                    reply_markup=create_change_keyboard(lang),
                    parse_mode="HTML"
                )
            except Exception:
                pass
            await callback.answer()
            return

        try:
            await callback.message.edit_text(
                t("notif_delete_select", lang),
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        except Exception:
            pass

    await callback.answer()


@router.callback_query(F.data.startswith('notif_replace_num_'))
async def handle_replace_num(callback: CallbackQuery, state: FSMContext):
    """Handle replace training number selection"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    num = int(callback.data.split('_')[3])
    chat_id = callback.from_user.id
    schedules = get_schedules(chat_id)

    if num < 0 or num >= len(schedules):
        try:
            await callback.message.edit_text(
                t("notif_invalid_number", lang),
                reply_markup=create_change_keyboard(lang),
                parse_mode="HTML"
            )
        except Exception:
            pass
        await state.clear()
        await state.update_data(lang=lang)
        return

    await state.update_data(action='replace', selected_num=num)

    try:
        await callback.message.edit_text(
            t("notif_replace_select_day", lang),
            reply_markup=create_day_keyboard('replace', lang, num),
            parse_mode="HTML"
        )
    except Exception:
        pass

    await callback.answer()


@router.callback_query(F.data.startswith('notif_delete_num_'))
async def handle_delete_num(callback: CallbackQuery, state: FSMContext):
    """Handle delete training number selection"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    num = int(callback.data.split('_')[3])
    chat_id = callback.from_user.id
    schedules = get_schedules(chat_id)

    if num < 0 or num >= len(schedules):
        try:
            await callback.message.edit_text(
                t("notif_invalid_number", lang),
                reply_markup=create_change_keyboard(lang),
                parse_mode="HTML"
            )
        except Exception:
            pass
        await callback.answer()
        return

    # Get training info before deletion
    weekday, train_time, reminder_minutes, _ = schedules[num]
    day_name = t(f'day_name_{weekday}', lang)
    time_str = f"{train_time.hour:02}:{train_time.minute:02}"

    # Delete from database and memory
    delete_training(chat_id, num)
    delete_schedule(chat_id, num)

    await state.clear()
    await state.update_data(lang=lang)

    try:
        await callback.message.edit_text(
            t("notif_delete_success", lang, day_name=day_name, time_str=time_str),
            reply_markup=create_main_keyboard(lang),
            parse_mode="HTML"
        )
    except Exception:
        await callback.message.answer(
            t("notif_delete_success", lang, day_name=day_name, time_str=time_str),
            reply_markup=create_main_keyboard(lang),
            parse_mode="HTML"
        )

    await callback.answer()


@router.callback_query(F.data.startswith('notif_add_day_') | F.data.startswith('notif_replace_day_'))
async def handle_day_selection(callback: CallbackQuery, state: FSMContext):
    """Handle day selection"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    parts = callback.data.split('_')
    action = parts[1]  # 'add' or 'replace'
    day_code = parts[3]

    if day_code not in day_map:
        try:
            await callback.message.edit_text(
                t("notif_invalid_day", lang),
                reply_markup=create_main_keyboard(lang),
                parse_mode="HTML"
            )
        except Exception:
            pass
        await state.clear()
        await state.update_data(lang=lang)
        return

    await state.update_data(selected_day=day_code)

    day_name = t(f'day_name_{day_map[day_code]}', lang)

    try:
        await callback.message.edit_text(
            t("notif_set_time", lang, day_name=day_name),
            parse_mode="HTML"
        )
    except Exception:
        pass

    await state.set_state(NotificationStates.waiting_for_time)
    await callback.answer()


@router.message(NotificationStates.waiting_for_time)
async def handle_time_input(message: Message, state: FSMContext):
    """Handle time input"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    # Check time format
    if not re.match(r'^\d{2}:\d{2}$', message.text):
        await message.answer(
            t("notif_time_invalid_format", lang),
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
            t("notif_time_invalid_format", lang),
            parse_mode="HTML"
        )
        return

    action = data.get('action', 'add')

    await state.update_data(selected_time=train_time)

    await message.answer(
        t("notif_select_reminder", lang),
        reply_markup=create_reminder_keyboard(action, lang),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith('notif_add_reminder_') | F.data.startswith('notif_replace_reminder_'))
async def handle_reminder_selection(callback: CallbackQuery, state: FSMContext):
    """Handle reminder time selection"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    parts = callback.data.split('_')
    action = parts[1]  # 'add' or 'replace'
    reminder_type = parts[3]

    if reminder_type == 'custom':
        await state.set_state(NotificationStates.waiting_for_custom_reminder)

        try:
            await callback.message.edit_text(
                t("notif_custom_reminder_input", lang),
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
    data = await state.get_data()
    lang = data.get('lang', 'en')

    try:
        reminder_minutes = int(message.text)
        if not (1 <= reminder_minutes <= 1440):
            raise ValueError
    except Exception:
        await message.answer(
            t("notif_custom_reminder_invalid", lang),
            parse_mode="HTML"
        )
        return

    await finalize_training(message.from_user.id, message, state, reminder_minutes)


async def finalize_training(chat_id: int, message_obj, state: FSMContext, reminder_minutes: int):
    """Finalize training addition or replacement"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    day_code = data.get('selected_day')
    train_time = data.get('selected_time')
    action = data.get('action', 'add')

    if not day_code or not train_time:
        await message_obj.answer(t("notif_error_missing_data", lang))
        await state.clear()
        await state.update_data(lang=lang)
        return

    weekday = day_map[day_code]
    reminder_str = format_reminder(reminder_minutes, lang)

    if action == 'add':
        # Check if user has reached maximum notifications
        current_count = get_notification_count(chat_id)

        if current_count >= MAX_NOTIFICATIONS:
            schedules = get_schedules(chat_id)
            lst = ''.join([f"• {t(f'day_name_{d}', lang)} {tm.hour:02}:{tm.minute:02} ({format_reminder(r, lang)} {t('notif_before', lang)})\n"
                          for d, tm, r, _ in schedules])

            await message_obj.answer(
                t("notif_max_reached", lang, max_count=MAX_NOTIFICATIONS, schedules=lst),
                reply_markup=create_main_keyboard(lang),
                parse_mode="HTML"
            )
            await state.clear()
            await state.update_data(lang=lang)
            return

        # Save to unified database
        success = save_training(chat_id, weekday, train_time, reminder_minutes)

        if not success:
            await message_obj.answer(
                t("notif_error_saving", lang),
                reply_markup=create_main_keyboard(lang),
                parse_mode="HTML"
            )
            await state.clear()
            await state.update_data(lang=lang)
            return

        # Create background task
        task = asyncio.create_task(
            reminder_loop(message_obj.bot, chat_id, weekday, train_time, reminder_minutes)
        )
        add_schedule(chat_id, weekday, train_time, reminder_minutes, task)

        await message_obj.answer(
            t("notif_add_success", lang,
              day_name=t(f'day_name_{weekday}', lang),
              time_str=f"{train_time.hour:02}:{train_time.minute:02}",
              reminder_str=reminder_str),
            reply_markup=create_main_keyboard(lang),
            parse_mode="HTML"
        )

    else:  # replace
        num = data.get('selected_num')
        schedules = get_schedules(chat_id)

        if num is None or num < 0 or num >= len(schedules):
            await message_obj.answer(
                t("notif_invalid_number", lang),
                reply_markup=create_main_keyboard(lang),
                parse_mode="HTML"
            )
            await state.clear()
            await state.update_data(lang=lang)
            return

        # Update in unified database
        success = update_training(chat_id, num, weekday, train_time, reminder_minutes)

        if not success:
            await message_obj.answer(
                t("notif_error_updating", lang),
                reply_markup=create_main_keyboard(lang),
                parse_mode="HTML"
            )
            await state.clear()
            await state.update_data(lang=lang)
            return

        # Create new background task
        task = asyncio.create_task(
            reminder_loop(message_obj.bot, chat_id, weekday, train_time, reminder_minutes)
        )
        update_schedule(chat_id, num, weekday, train_time, reminder_minutes, task)

        await message_obj.answer(
            t("notif_replace_success", lang,
              day_name=t(f'day_name_{weekday}', lang),
              time_str=f"{train_time.hour:02}:{train_time.minute:02}",
              reminder_str=reminder_str),
            reply_markup=create_main_keyboard(lang),
            parse_mode="HTML"
        )

    await state.clear()
    await state.update_data(lang=lang)