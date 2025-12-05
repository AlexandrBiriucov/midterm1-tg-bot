"""
Handlers for custom workout routines (Dev4 feature).
Updated to use unified database via SQLAlchemy and FSM states.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from localization.utils import t
from bot.features.dev1_workout_tracking.services import get_lang

from .services import (
    save_custom_routine,
    get_user_routines,
    get_routine_by_id,
    delete_routine,
    update_routine_usage,
    get_routine_stats
)
from .states import RoutineCreationForm

# Create router
routine_router = Router()

# Preset routines defined in code
PRESET_ROUTINES = {
    "beginner_fullbody": {
        "name": "🟢 Full Body (Beginner)",
        "level": "beginner",
        "description": "Basic program for beginners, 3 times per week",
        "schedule": "Mon, Wed, Fri",
        "exercises": [
            "🏋️ Barbell Squats - 3x10",
            "💪 Bench Press - 3x10",
            "🔥 Bent-over Barbell Row - 3x10",
            "🦵 Lunges - 3x12",
            "📊 Plank - 3x30 sec"
        ]
    },

    "beginner_ppl": {
        "name": "🟢 PPL (Beginner)",
        "level": "beginner",
        "description": "Push-Pull-Legs for beginners",
        "schedule": "Mon: Push, Tue: Pull, Wed: Legs, Thu: Rest, Fri: Repeat",
        "exercises": [
            "Day 1 (Push):",
            "- Bench Press 3x10",
            "- Dumbbell Press 3x12",
            "- Push-ups 3xMAX",
            "",
            "Day 2 (Pull):",
            "- Barbell Row 3x10",
            "- Pull-ups/Lat Pulldown 3x10",
            "- Hyperextensions 3x15",
            "",
            "Day 3 (Legs):",
            "- Squats 3x10",
            "- Deadlift 3x10",
            "- Leg Extensions 3x12"
        ]
    },

    "intermediate_upper_lower": {
        "name": "🟡 Upper/Lower (Intermediate)",
        "level": "intermediate",
        "description": "Upper/Lower split for intermediate lifters",
        "schedule": "Mon: Upper, Tue: Lower, Wed: Rest, Thu: Upper, Fri: Lower",
        "exercises": [
            "Day 1 (Upper Body):",
            "- Bench Press 4x8",
            "- Barbell Row 4x8",
            "- Dumbbell Press 3x10",
            "- Pull-ups 3xMAX",
            "",
            "Day 2 (Lower Body):",
            "- Squats 4x8",
            "- Deadlift 3x8",
            "- Leg Press 3x10",
            "- Calf Raises 4x15"
        ]
    },

    "advanced_ppl": {
        "name": "🔴 PPL Advanced",
        "level": "advanced",
        "description": "Advanced Push-Pull-Legs program",
        "schedule": "6 days per week, 2 PPL cycles",
        "exercises": [
            "Push Day:",
            "- Bench Press 5x5",
            "- Incline Dumbbell Press 4x8",
            "- Overhead Press 4x8",
            "- Tricep Extensions 3x10",
            "",
            "Pull Day:",
            "- Deadlift 5x5",
            "- Pull-ups 4xMAX",
            "- Barbell Row 4x8",
            "- Bicep Curls 3x12",
            "",
            "Leg Day:",
            "- Squats 5x5",
            "- Romanian Deadlift 4x8",
            "- Bulgarian Split Squats 3x10",
            "- Calf Raises 4x15"
        ]
    }
}


# ============================================================================
# COMMAND HANDLERS
# ============================================================================

@routine_router.message(Command("routines"))
async def show_routines(message: Message, state: FSMContext):
    """Show routine level selection"""
    lang = get_lang(message.from_user.id)
    await state.update_data(lang=lang)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("routine_beginner_button", lang), callback_data="level_beginner")],
        [InlineKeyboardButton(text=t("routine_intermediate_button", lang), callback_data="level_intermediate")],
        [InlineKeyboardButton(text=t("routine_advanced_button", lang), callback_data="level_advanced")]
    ])

    await message.answer(
        t("routine_choose_level", lang),
        reply_markup=keyboard
    )


@routine_router.message(Command("custom_routines"))
async def custom_routines(message: Message, state: FSMContext):
    """Show custom routine management"""
    lang = get_lang(message.from_user.id)
    await state.update_data(lang=lang)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("routine_create_button", lang), callback_data="create_routine")],
        [InlineKeyboardButton(text=t("routine_my_routines_button", lang), callback_data="my_routines")],
        [InlineKeyboardButton(text=t("routine_stats_button", lang), callback_data="routine_stats")]
    ])

    await message.answer(
        t("routine_custom_management", lang),
        reply_markup=keyboard
    )


# ============================================================================
# CALLBACK HANDLERS - Level Selection
# ============================================================================

@routine_router.callback_query(F.data.startswith("level_"))
async def show_level_routines(callback: CallbackQuery, state: FSMContext):
    """Show routines for selected level"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    level = callback.data.replace('level_', '')

    # Filter preset routines by level
    level_routines = {k: v for k, v in PRESET_ROUTINES.items() if v['level'] == level}

    if not level_routines:
        await callback.message.answer(t("routine_no_programs", lang))
        await callback.answer()
        return

    # Build keyboard
    keyboard_buttons = []
    for routine_id, routine in level_routines.items():
        keyboard_buttons.append([InlineKeyboardButton(
            text=routine['name'],
            callback_data=f"show_preset_{routine_id}"
        )])

    # Add back button
    keyboard_buttons.append([InlineKeyboardButton(
        text=t("routine_back_button", lang),
        callback_data="back_to_levels"
    )])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    level_key = f"routine_{level}_label"

    await callback.message.edit_text(
        t("routine_choose_program", lang, level=t(level_key, lang)),
        reply_markup=keyboard
    )
    await callback.answer()


@routine_router.callback_query(F.data == "back_to_levels")
async def back_to_levels(callback: CallbackQuery, state: FSMContext):
    """Return to level selection"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("routine_beginner_button", lang), callback_data="level_beginner")],
        [InlineKeyboardButton(text=t("routine_intermediate_button", lang), callback_data="level_intermediate")],
        [InlineKeyboardButton(text=t("routine_advanced_button", lang), callback_data="level_advanced")]
    ])

    await callback.message.edit_text(
        t("routine_choose_level", lang),
        reply_markup=keyboard
    )
    await callback.answer()


# ============================================================================
# CALLBACK HANDLERS - Show Routine Details
# ============================================================================

@routine_router.callback_query(F.data.startswith("show_preset_"))
async def show_preset_details(callback: CallbackQuery, state: FSMContext):
    """Show details of a preset routine"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    routine_id = callback.data.replace('show_preset_', '')
    routine = PRESET_ROUTINES.get(routine_id)

    if not routine:
        await callback.answer(t("routine_not_found", lang), show_alert=True)
        return

    exercises_text = "\n".join(routine['exercises'])

    response = t("routine_details", lang,
                 name=routine['name'],
                 description=routine['description'],
                 schedule=routine['schedule'],
                 exercises=exercises_text)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=t("routine_save_button", lang),
            callback_data=f"save_preset_{routine_id}"
        )],
        [InlineKeyboardButton(
            text=t("routine_back_levels_button", lang),
            callback_data=f"level_{routine['level']}"
        )]
    ])

    await callback.message.answer(response, reply_markup=keyboard)
    await callback.answer()


@routine_router.callback_query(F.data.startswith("save_preset_"))
async def save_preset_routine(callback: CallbackQuery, state: FSMContext):
    """Save a preset routine to user's collection"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    routine_id = callback.data.replace('save_preset_', '')
    user_id = callback.from_user.id
    routine = PRESET_ROUTINES.get(routine_id)

    if not routine:
        await callback.answer(t("routine_not_found", lang), show_alert=True)
        return

    try:
        # Save to database
        saved_routine = save_custom_routine(
            user_id=user_id,
            name=routine['name'],
            description=routine['description'],
            level=routine['level'],
            schedule=routine['schedule'],
            exercises={"exercises": routine['exercises']},
            is_preset=True
        )

        await callback.answer(t("routine_saved", lang, name=routine['name']))

        # Show saved routines
        await show_user_routines(callback.message, user_id, lang)

    except Exception as e:
        await callback.answer(t("routine_save_error", lang, error=str(e)), show_alert=True)


# ============================================================================
# CUSTOM ROUTINE CREATION
# ============================================================================

@routine_router.callback_query(F.data == "create_routine")
async def create_routine(callback: CallbackQuery, state: FSMContext):
    """Start custom routine creation"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    await state.set_state(RoutineCreationForm.waiting_for_routine_data)
    await callback.message.answer(t("routine_creation_instructions", lang),parse_mode="HTML")
    await callback.answer()


@routine_router.message(RoutineCreationForm.waiting_for_routine_data)
async def process_routine_creation(message: Message, state: FSMContext):
    """Process custom routine creation input"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    user_id = message.from_user.id

    lines = [line.strip() for line in message.text.split('\n') if line.strip()]

    if len(lines) < 4:
        await message.answer(t("routine_not_enough_data", lang))
        return

    try:
        # Save to database
        saved_routine = save_custom_routine(
            user_id=user_id,
            name=lines[0],
            description=lines[1],
            schedule=lines[2],
            exercises={"exercises": lines[3:]},
            level=None,
            is_preset=False
        )

        # Clear state
        await state.clear()

        await message.answer(
            t("routine_created_success", lang,
              name=saved_routine.name,
              description=saved_routine.description,
              schedule=saved_routine.schedule,
              count=len(lines[3:]))
        )

    except Exception as e:
        await message.answer(t("routine_creation_error", lang, error=str(e)))


# ============================================================================
# MY ROUTINES
# ============================================================================

@routine_router.callback_query(F.data == "my_routines")
async def my_routines_callback(callback: CallbackQuery, state: FSMContext):
    """Show user's saved routines (callback version)"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    await show_user_routines(callback.message, callback.from_user.id, lang)
    await callback.answer()


async def show_user_routines(message: Message, user_id: int, lang: str):
    """Helper function to show user's routines"""
    routines = get_user_routines(user_id)

    if not routines:
        await message.answer(t("routine_no_saved", lang))
        return

    response = t("routine_your_saved", lang) + "\n\n"

    keyboard_buttons = []

    for i, routine in enumerate(routines, 1):
        icon = "⭐" if routine.is_preset else "📝"
        response += f"{i}. {icon} {routine.name}\n"
        response += f"   {routine.description or t('routine_no_description', lang)}\n"
        response += f"   📊 {t('routine_times_used', lang)}: {routine.times_used}\n\n"

        # Add button for each routine
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"{i}. {routine.name}",
                callback_data=f"view_routine_{routine.routine_id}"
            )
        ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await message.answer(response, reply_markup=keyboard)


@routine_router.callback_query(F.data.startswith("view_routine_"))
async def view_routine(callback: CallbackQuery, state: FSMContext):
    """View details of a saved routine"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    routine_id = int(callback.data.replace('view_routine_', ''))
    user_id = callback.from_user.id

    routine = get_routine_by_id(routine_id, user_id)

    if not routine:
        await callback.answer(t("routine_not_found", lang), show_alert=True)
        return

    # Build exercises text
    exercises = routine.exercises.get('exercises', [])
    exercises_text = "\n".join(exercises)

    icon = "⭐" if routine.is_preset else "📝"

    response = t("routine_view_details", lang,
                 icon=icon,
                 name=routine.name,
                 description=routine.description or t("routine_no_description", lang),
                 schedule=routine.schedule or t("routine_not_specified", lang),
                 times_used=routine.times_used,
                 exercises=exercises_text)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=t("routine_start_button", lang),
            callback_data=f"start_routine_{routine.routine_id}"
        )],
        [InlineKeyboardButton(
            text=t("routine_delete_button", lang),
            callback_data=f"delete_routine_{routine.routine_id}"
        )],
        [InlineKeyboardButton(
            text=t("routine_back_my_routines", lang),
            callback_data="my_routines"
        )]
    ])

    await callback.message.edit_text(response, reply_markup=keyboard)
    await callback.answer()


@routine_router.callback_query(F.data.startswith("start_routine_"))
async def start_routine(callback: CallbackQuery, state: FSMContext):
    """Mark routine as started (increment usage)"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    routine_id = int(callback.data.replace('start_routine_', ''))

    try:
        update_routine_usage(routine_id)
        await callback.answer(t("routine_great_workout", lang), show_alert=True)
    except Exception as e:
        await callback.answer(t("routine_error", lang, error=str(e)), show_alert=True)


@routine_router.callback_query(F.data.startswith("delete_routine_"))
async def delete_routine_handler(callback: CallbackQuery, state: FSMContext):
    """Delete a routine"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    routine_id = int(callback.data.replace('delete_routine_', ''))

    # Confirm deletion
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t("routine_yes_delete", lang), callback_data=f"confirm_delete_{routine_id}"),
            InlineKeyboardButton(text=t("routine_cancel", lang), callback_data=f"view_routine_{routine_id}")
        ]
    ])

    await callback.message.edit_text(
        t("routine_confirm_deletion", lang),
        reply_markup=keyboard
    )
    await callback.answer()


@routine_router.callback_query(F.data.startswith("confirm_delete_"))
async def confirm_delete(callback: CallbackQuery, state: FSMContext):
    """Confirm routine deletion"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    routine_id = int(callback.data.replace('confirm_delete_', ''))
    user_id = callback.from_user.id

    success = delete_routine(routine_id, user_id)

    if success:
        await callback.answer(t("routine_deleted", lang), show_alert=True)
        await show_user_routines(callback.message, user_id, lang)
    else:
        await callback.answer(t("routine_delete_error", lang), show_alert=True)


# ============================================================================
# ROUTINE STATISTICS
# ============================================================================

@routine_router.callback_query(F.data == "routine_stats")
async def show_routine_stats(callback: CallbackQuery, state: FSMContext):
    """Show routine statistics"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    user_id = callback.from_user.id
    stats = get_routine_stats(user_id)

    if stats['total_routines'] == 0:
        await callback.message.answer(t("routine_no_stats", lang))
        await callback.answer()
        return

    await callback.message.answer(
        t("routine_stats_display", lang,
          total=stats['total_routines'],
          most_used=stats['most_used'],
          most_used_count=stats['most_used_count'],
          total_usage=stats['total_usage'])
    )
    await callback.answer()