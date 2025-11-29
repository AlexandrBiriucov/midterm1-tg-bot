"""
Statistics and Progress Tracking Handlers - Dev3 Feature
Integrated with unified database structure
"""
import calendar
import os
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import seaborn as sns

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    Message, 
    ReplyKeyboardMarkup, 
    KeyboardButton,
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    ReplyKeyboardRemove,
    CallbackQuery,
    FSInputFile
)

from bot.core.database import SessionLocal
from bot.core.models import Workout
from .muscle_groups import exercise_to_muscle
from .utils_funcs import (
    one_rep_max,
    calculate_volume,
    compute_weekly_volume,
    compute_muscle_group_stats,
    group_muscle_volume_by_week
)

# Router for statistics feature
stats_router = Router()

# Define the graphs directory path
GRAPHS_DIR = Path(__file__).parent.parent.parent.parent / "data" / "graphs"

# Ensure the graphs directory exists
GRAPHS_DIR.mkdir(parents=True, exist_ok=True)




# ============================================================================
# FSM States
# ============================================================================

class StatsForm(StatesGroup):
    choice_type = State()
    time_period = State()
    progression_state = State()
    best_lift = State()
    best_lift_action = State()
    volume_state = State()
    consistency = State()
    leaderboard_state = State()
    chart_state = State()
    muscle_grp_period = State()
    muscle_grp_process_period = State()
    muscle_grp_state = State()
    heat_map_state = State()
    recommendations_state = State()


# ============================================================================
# Main Statistics Command
# ============================================================================

@stats_router.message(Command("statistics"))
async def stats_command(message: Message, state: FSMContext):
    """Main entry point for statistics"""
    await state.set_state(StatsForm.choice_type)
    await message.answer(
        "What stats do you want to see?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Overall")],
                [KeyboardButton(text="Progression")],
                [KeyboardButton(text="Get Recommendations")],
            ],
            resize_keyboard=True,
        ),
    )


# ============================================================================
# Overall Stats - Time Period Selection
# ============================================================================

@stats_router.message(StatsForm.choice_type, F.text.casefold() == "overall")
async def process_overall_choice(message: Message, state: FSMContext):
    """Handle 'Overall' statistics choice"""
    await state.update_data(choice_type="overall")
    await state.set_state(StatsForm.time_period)
    await message.answer(
        "Choose the time period of the stats",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Today")],
                [KeyboardButton(text="This Week")],
                [KeyboardButton(text="All Time")]
            ],
            resize_keyboard=True,
        ),
    )


@stats_router.message(StatsForm.time_period)
async def process_time_period(message: Message, state: FSMContext):
    """Process time period selection and show workouts"""
    time_period = message.text.strip()
    user_id = message.from_user.id
    now = datetime.now(timezone.utc)
    
    with SessionLocal() as session:
        query = session.query(Workout).filter(Workout.user_id == user_id)

        if time_period == "Today":
            start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
            query = query.filter(Workout.created_at >= start, Workout.created_at <= now)
        elif time_period == "This Week":
            start = now - timedelta(days=7)
            query = query.filter(Workout.created_at >= start, Workout.created_at <= now)
        
        results = query.order_by(Workout.created_at.desc()).all()

        if not results:
            await message.answer("No workouts found for this period.")
        else:
            text = "\n".join(
                f"{w.created_at:%d-%m %H:%M} — {w.exercise} {w.sets}x{w.reps}x{w.weight} kg"
                for w in results
            )
            await message.answer(f"Here are your workouts:\n{text}")

    await state.set_state(StatsForm.choice_type)
    await message.answer(
        "What stats do you want to see next?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Overall")],
                [KeyboardButton(text="Progression")],
                [KeyboardButton(text="Recomendation")],
            ],
            resize_keyboard=True,
        )
    )