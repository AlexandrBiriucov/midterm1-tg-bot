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


# ============================================================================
# Best Lift Progression
# ============================================================================

@stats_router.message(StatsForm.progression_state, F.text.casefold() == "best lift progression")
async def process_best_lift(message: Message, state: FSMContext):
    """Start best lift progression flow"""
    await state.update_data(progression="best_lift")
    await state.set_state(StatsForm.best_lift)
    await message.answer(
        "Which exercise do you want to choose?\nPlease write the exercise name (BenchPress, Squat, Deadlift...)",
        reply_markup=ReplyKeyboardRemove(),
    )


@stats_router.message(StatsForm.best_lift)
async def process_best_lift_exercise_choice(message: Message, state: FSMContext):
    """Process exercise choice and show weekly progression"""
    exercise = message.text.strip()
    await state.update_data(exercise=exercise)
    user_id = message.from_user.id

    with SessionLocal() as session:
        results = (
            session.query(Workout)
            .filter(Workout.user_id == user_id, Workout.exercise.ilike(exercise))
            .order_by(Workout.created_at.asc())
            .all()
        )

        if not results:
            await message.answer(f"No data found for {exercise}")
            await state.clear()
            return

        weekly_max = defaultdict(int)
        for w in results:
            week_start = (w.created_at - timedelta(days=w.created_at.weekday())).date()
            weekly_max[week_start] = max(weekly_max[week_start], w.weight)

        lines = []
        for week_start, max_weight in weekly_max.items():
            week_str = week_start.strftime("%Y-%m-%d")
            lines.append(f"Week starting {week_str}: best result was {max_weight} kg")

        text = "\n".join(lines)
        await message.answer(f"Here is your weekly progression:\n{text}")
        
        await state.update_data(weekly_max={str(k): v for k, v in weekly_max.items()})
        await state.set_state(StatsForm.best_lift_action)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Graph", callback_data="graph")],
            [InlineKeyboardButton(text="One Repetition Max", callback_data="orm")],
            [InlineKeyboardButton(text="Previous", callback_data="Back")],
        ])
        await message.answer("Choose an option", reply_markup=keyboard)


@stats_router.callback_query(F.data.in_(["graph", "orm", "Back"]))
async def graph_or_ORM(callback: CallbackQuery, state: FSMContext):
    """Handle graph/ORM/back callback buttons"""
    choice = callback.data
    await callback.answer()

    if choice == "graph":
        data = await state.get_data()
        weekly_max = {datetime.fromisoformat(k): v for k, v in data.get("weekly_max", {}).items()}
        weeks = list(weekly_max.keys())
        weights = list(weekly_max.values())

        if not weeks:
            await callback.message.answer("No weekly data available to display.")
            return

        plt.figure(figsize=(10, 6))
        plt.plot(weeks, weights, marker="o", linestyle="-", color="blue")
        plt.xticks(rotation=45, ha="right", fontsize=10)
        plt.title("Best Lift Progression")
        plt.xlabel("Week")
        plt.ylabel("Max Weight (kg)")
        plt.tight_layout()
        
        # Save to graphs directory
        progress_path = GRAPHS_DIR / "progress.png"
        plt.savefig(progress_path)
        plt.close()

        photo = FSInputFile(progress_path)
        await callback.message.answer_photo(photo, caption="Your weekly progression graph")
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Graph", callback_data="graph")],
            [InlineKeyboardButton(text="One Repetition Max", callback_data="orm")],
            [InlineKeyboardButton(text="Previous", callback_data="Back")],
        ])
        await callback.message.answer("Choose an option", reply_markup=keyboard)

    elif choice == "orm":
        data = await state.get_data()
        user_id = callback.from_user.id
        exercise_choice = data.get("exercise")

        with SessionLocal() as session:
            results = (
                session.query(Workout)
                .filter(Workout.user_id == user_id, Workout.exercise.ilike(exercise_choice))
                .order_by(Workout.weight.desc())
                .all()
            )

            if results:
                best_set = [one_rep_max(r.weight, r.reps) for r in results]
                best_lift = max(best_set)
                await callback.message.answer(
                    f"Theoretically your current max weight on {exercise_choice} is {best_lift:.1f} kg"
                )
            else:
                await callback.message.answer(f"No data registered for {exercise_choice}")
        
        await state.clear()

    elif choice == "Back":
        await state.set_state(StatsForm.choice_type)
        await callback.message.answer(
            "What stats do you want to see?",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Overall")],
                    [KeyboardButton(text="Progression")]
                    [KeyboardButton(text="Recomendations")]
                ],
                resize_keyboard=True,
            ),
        )


