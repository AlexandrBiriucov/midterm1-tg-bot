"""
Handlers for custom workout routines (Dev4 feature).
Updated to use unified database via SQLAlchemy and FSM states.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

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
async def show_routines(message: Message):
    """Show routine level selection"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Beginner", callback_data="level_beginner")],
        [InlineKeyboardButton(text="🟡 Intermediate", callback_data="level_intermediate")],
        [InlineKeyboardButton(text="🔴 Advanced", callback_data="level_advanced")]
    ])
    
    await message.answer(
        "🏋️ Choose your level:\n\n"
        "🟢 Beginner - up to 3 months of training\n"  
        "🟡 Intermediate - 3-12 months of experience\n"
        "🔴 Advanced - 1-2 years of training",
        reply_markup=keyboard
    )


@routine_router.message(Command("custom_routines"))
async def custom_routines(message: Message):
    """Show custom routine management"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Create Routine", callback_data="create_routine")],
        [InlineKeyboardButton(text="📋 My Routines", callback_data="my_routines")],
        [InlineKeyboardButton(text="📊 Statistics", callback_data="routine_stats")]
    ])
    
    await message.answer(
        "🎯 Custom Routine Management:",
        reply_markup=keyboard
    )


# ============================================================================
# CALLBACK HANDLERS - Level Selection
# ============================================================================

@routine_router.callback_query(F.data.startswith("level_"))
async def show_level_routines(callback: CallbackQuery):
    """Show routines for selected level"""
    level = callback.data.replace('level_', '')
    
    # Filter preset routines by level
    level_routines = {k: v for k, v in PRESET_ROUTINES.items() if v['level'] == level}
    
    if not level_routines:
        await callback.message.answer("❌ No programs available for this level yet")
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
        text="⬅️ Back",
        callback_data="back_to_levels"
    )])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    level_names = {
        'beginner': '🟢 Beginner',
        'intermediate': '🟡 Intermediate', 
        'advanced': '🔴 Advanced'
    }
    
    await callback.message.edit_text(
        f"{level_names[level]} - Choose a program:",
        reply_markup=keyboard
    )
    await callback.answer()


@routine_router.callback_query(F.data == "back_to_levels")
async def back_to_levels(callback: CallbackQuery):
    """Return to level selection"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Beginner", callback_data="level_beginner")],
        [InlineKeyboardButton(text="🟡 Intermediate", callback_data="level_intermediate")],
        [InlineKeyboardButton(text="🔴 Advanced", callback_data="level_advanced")]
    ])
    
    await callback.message.edit_text(
        "🏋️ Choose your level:\n\n"
        "🟢 Beginner - up to 3 months of training\n"  
        "🟡 Intermediate - 3-12 months of experience\n"
        "🔴 Advanced - 1-2 years of training",
        reply_markup=keyboard
    )
    await callback.answer()


# ============================================================================
# CALLBACK HANDLERS - Show Routine Details
# ============================================================================

@routine_router.callback_query(F.data.startswith("show_preset_"))
async def show_preset_details(callback: CallbackQuery):
    """Show details of a preset routine"""
    routine_id = callback.data.replace('show_preset_', '')
    routine = PRESET_ROUTINES.get(routine_id)
    
    if not routine:
        await callback.answer("❌ Routine not found", show_alert=True)
        return
    
    exercises_text = "\n".join(routine['exercises'])
    
    response = (
        f"🏋️ {routine['name']}\n\n"
        f"📝 Description: {routine['description']}\n"
        f"📅 Schedule: {routine['schedule']}\n\n"
        f"Exercises:\n{exercises_text}"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💾 Save Program", 
            callback_data=f"save_preset_{routine_id}"
        )],
        [InlineKeyboardButton(
            text="⬅️ Back to Levels",
            callback_data=f"level_{routine['level']}"
        )]
    ])
    
    await callback.message.answer(response, reply_markup=keyboard)
    await callback.answer()


@routine_router.callback_query(F.data.startswith("save_preset_"))
async def save_preset_routine(callback: CallbackQuery):
    """Save a preset routine to user's collection"""
    routine_id = callback.data.replace('save_preset_', '')
    user_id = callback.from_user.id
    routine = PRESET_ROUTINES.get(routine_id)
    
    if not routine:
        await callback.answer("❌ Routine not found", show_alert=True)
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
        
        await callback.answer(f"✅ Program '{routine['name']}' saved!")
        
        # Show saved routines
        await show_user_routines(callback.message, user_id)
        
    except Exception as e:
        await callback.answer(f"❌ Error saving: {str(e)}", show_alert=True)


# ============================================================================
# CUSTOM ROUTINE CREATION
# ============================================================================

@routine_router.callback_query(F.data == "create_routine")
async def create_routine(callback: CallbackQuery, state: FSMContext):
    """Start custom routine creation"""
    instructions = (
        "📝 Create Your Program:\n\n"
        "Send data in the following format:\n"
        "```\n"
        "Program Name\n"
        "Description\n" 
        "Schedule\n"
        "Exercise 1\n"
        "Exercise 2\n"
        "Exercise 3\n"
        "...\n"
        "```\n\n"
        "Example:\n"
        "```\n"
        "My Program\n"
        "Mass building program\n"
        "Mon, Wed, Fri\n"
        "Bench Press 4x8\n"
        "Squats 4x10\n"
        "Barbell Row 4x8\n"
        "```"
    )
    
    await state.set_state(RoutineCreationForm.waiting_for_routine_data)
    await callback.message.answer(instructions, parse_mode="Markdown")
    await callback.answer()


@routine_router.message(RoutineCreationForm.waiting_for_routine_data)
async def process_routine_creation(message: Message, state: FSMContext):
    """Process custom routine creation input"""
    user_id = message.from_user.id
    
    lines = [line.strip() for line in message.text.split('\n') if line.strip()]
    
    if len(lines) < 4:
        await message.answer(
            "❌ Not enough data!\n"
            "Need at minimum:\n"
            "1. Name\n"
            "2. Description\n"
            "3. Schedule\n"
            "4. At least one exercise"
        )
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
            f"✅ Program Created!\n\n"
            f"🏋️ {saved_routine.name}\n"
            f"📝 {saved_routine.description}\n"
            f"📅 {saved_routine.schedule}\n\n"
            f"💪 Exercises: {len(lines[3:])}\n\n"
            f"Use /custom_routines to view all programs"
        )
        
    except Exception as e:
        await message.answer(f"❌ Error creating: {str(e)}")


# ============================================================================
# MY ROUTINES
# ============================================================================

@routine_router.callback_query(F.data == "my_routines")
async def my_routines_callback(callback: CallbackQuery):
    """Show user's saved routines (callback version)"""
    await show_user_routines(callback.message, callback.from_user.id)
    await callback.answer()


async def show_user_routines(message: Message, user_id: int):
    """Helper function to show user's routines"""
    routines = get_user_routines(user_id)
    
    if not routines:
        await message.answer("🔭 You don't have any saved programs yet")
        return
    
    response = "📋 Your Saved Programs:\n\n"
    
    keyboard_buttons = []
    
    for i, routine in enumerate(routines, 1):
        icon = "⭐" if routine.is_preset else "📝"
        response += f"{i}. {icon} {routine.name}\n"
        response += f"   {routine.description or 'No description'}\n"
        response += f"   📊 Times Used: {routine.times_used}\n\n"
        
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
async def view_routine(callback: CallbackQuery):
    """View details of a saved routine"""
    routine_id = int(callback.data.replace('view_routine_', ''))
    user_id = callback.from_user.id
    
    routine = get_routine_by_id(routine_id, user_id)
    
    if not routine:
        await callback.answer("❌ Routine not found", show_alert=True)
        return
    
    # Build exercises text
    exercises = routine.exercises.get('exercises', [])
    exercises_text = "\n".join(exercises)
    
    icon = "⭐" if routine.is_preset else "📝"
    
    response = (
        f"{icon} {routine.name}\n\n"
        f"📝 Description: {routine.description or 'No description'}\n"
        f"📅 Schedule: {routine.schedule or 'Not specified'}\n"
        f"📊 Times Used: {routine.times_used}\n\n"
        f"Exercises:\n{exercises_text}"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="✅ Start Workout",
            callback_data=f"start_routine_{routine.routine_id}"
        )],
        [InlineKeyboardButton(
            text="🗑️ Delete",
            callback_data=f"delete_routine_{routine.routine_id}"
        )],
        [InlineKeyboardButton(
            text="⬅️ Back to My Routines",
            callback_data="my_routines"
        )]
    ])
    
    await callback.message.edit_text(response, reply_markup=keyboard)
    await callback.answer()


@routine_router.callback_query(F.data.startswith("start_routine_"))
async def start_routine(callback: CallbackQuery):
    """Mark routine as started (increment usage)"""
    routine_id = int(callback.data.replace('start_routine_', ''))
    
    try:
        update_routine_usage(routine_id)
        await callback.answer("🏋️ Great workout!", show_alert=True)
    except Exception as e:
        await callback.answer(f"❌ Error: {str(e)}", show_alert=True)


@routine_router.callback_query(F.data.startswith("delete_routine_"))
async def delete_routine_handler(callback: CallbackQuery):
    """Delete a routine"""
    routine_id = int(callback.data.replace('delete_routine_', ''))
    user_id = callback.from_user.id
    
    # Confirm deletion
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yes, Delete", callback_data=f"confirm_delete_{routine_id}"),
            InlineKeyboardButton(text="❌ Cancel", callback_data=f"view_routine_{routine_id}")
        ]
    ])
    
    await callback.message.edit_text(
        "⚠️ Confirm Deletion\n\n"
        "Are you sure you want to delete this program?",
        reply_markup=keyboard
    )
    await callback.answer()


@routine_router.callback_query(F.data.startswith("confirm_delete_"))
async def confirm_delete(callback: CallbackQuery):
    """Confirm routine deletion"""
    routine_id = int(callback.data.replace('confirm_delete_', ''))
    user_id = callback.from_user.id
    
    success = delete_routine(routine_id, user_id)
    
    if success:
        await callback.answer("✅ Program deleted", show_alert=True)
        await show_user_routines(callback.message, user_id)
    else:
        await callback.answer("❌ Error deleting", show_alert=True)


# ============================================================================
# ROUTINE STATISTICS
# ============================================================================

@routine_router.callback_query(F.data == "routine_stats")
async def show_routine_stats(callback: CallbackQuery):
    """Show routine statistics"""
    user_id = callback.from_user.id
    stats = get_routine_stats(user_id)
    
    if stats['total_routines'] == 0:
        await callback.message.answer("📊 You don't have any program statistics yet")
        await callback.answer()
        return
    
    response = (
        "📊 Your Program Statistics:\n\n"
        f"📚 Total Programs: {stats['total_routines']}\n"
        f"🔥 Most Popular: {stats['most_used']} ({stats['most_used_count']} times)\n"
        f"💪 Total Workouts from Programs: {stats['total_usage']}\n"
    )
    
    await callback.message.answer(response)
    await callback.answer()