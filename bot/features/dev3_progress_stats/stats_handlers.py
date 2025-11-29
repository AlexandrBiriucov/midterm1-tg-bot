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


# ============================================================================
# Volume Progression
# ============================================================================

@stats_router.message(StatsForm.progression_state, F.text.casefold() == "volume progression")
async def process_volume(message: Message, state: FSMContext):
    """Process volume progression"""
    await state.set_state(StatsForm.volume_state)
    user_id = message.from_user.id

    with SessionLocal() as session:
        results = session.query(Workout).filter(Workout.user_id == user_id).all()
        
        weekly_volume = defaultdict(int)
        for w in results:
            week_start = (w.created_at - timedelta(days=w.created_at.weekday())).date()
            weekly_volume[week_start] += calculate_volume(w.sets, w.reps, w.weight)

        await state.update_data(
            weekly_volume={str(k): v for k, v in weekly_volume.items()}
        )

        lines = []
        for week_start, volume in weekly_volume.items():
            week_str = week_start.strftime("%Y-%m-%d")
            lines.append(f"The volume in the week starting at {week_str} was {volume}")

        text = "\n".join(lines)
        await message.answer(
            f"Here is your weekly progression:\n{text}",
            reply_markup=ReplyKeyboardRemove()
        )
        await message.answer("If you want to see the volume bar charts type 'chart'")
        await state.set_state(StatsForm.chart_state)


@stats_router.message(StatsForm.chart_state)
async def process_chart(message: Message, state: FSMContext):
    """Generate volume progression chart"""
    data = await state.get_data()
    data_for_chart = {datetime.fromisoformat(k): v for k, v in data.get("weekly_volume", {}).items()}
    weeks = list(data_for_chart.keys())
    volumes = list(data_for_chart.values())

    plt.figure(figsize=(10, 6))

    if len(weeks) <= 2:
        plt.plot(weeks, volumes, marker="o", linestyle="-")
        plt.xlim(weeks[0] - pd.Timedelta(days=1), weeks[-1] + pd.Timedelta(days=1))
    else:
        plt.bar(weeks, volumes, width=5)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.title("Volume Progression")
    plt.xlabel("Week")
    plt.ylabel("Volume")
    plt.tight_layout()
    
    # Save to graphs directory
    volume_path = GRAPHS_DIR / "volume_progress.png"
    plt.savefig(volume_path)
    plt.close()

    photo = FSInputFile(volume_path)
    await message.answer_photo(photo, caption="Your weekly volume progression")
    
    await state.set_state(StatsForm.choice_type)
    await message.answer(
        "What stats do you want to see?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Overall")],
                [KeyboardButton(text="Progression")]
            ],
            resize_keyboard=True,
        ),
    )


# ============================================================================
# Muscle Group Distribution
# ============================================================================

@stats_router.message(StatsForm.progression_state, F.text.casefold() == "muscle group distribution")
async def process_muscle_grp_distribution(message: Message, state: FSMContext):
    """Show muscle group distribution menu"""
    await state.set_state(StatsForm.muscle_grp_state)
    await message.answer("Muscle Distribution Menu", reply_markup=ReplyKeyboardRemove())
    user_id = message.from_user.id

    with SessionLocal() as session:
        results = (
            session.query(Workout)
            .filter(Workout.user_id == user_id)
            .order_by(Workout.created_at.desc())
            .all()
        )
        
        if not results:
            await message.answer("No workouts found.")
            return

        workouts_by_date = defaultdict(list)
        for w in results:
            workout_date = w.created_at.date()
            workouts_by_date[workout_date].append(w)

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"{date:%d-%m-%Y} — {len(workouts_by_date[date])} exercises",
                        callback_data=f"workout_{date}"
                    )
                ]
                for date in sorted(workouts_by_date.keys(), reverse=True)
            ]
        )

        await message.answer("Select a workout date to see muscle distribution:", reply_markup=keyboard)


@stats_router.callback_query(lambda c: c.data.startswith("workout_"))
async def workout_selected(callback_query: CallbackQuery, state: FSMContext):
    """Show muscle distribution pie chart for selected date"""
    date_str = callback_query.data.split("_")[1]
    workout_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    with SessionLocal() as session:
        workouts = (
            session.query(Workout)
            .filter(
                Workout.user_id == callback_query.from_user.id,
                Workout.created_at >= workout_date,
                Workout.created_at < workout_date + timedelta(days=1),
            )
            .all()
        )

        muscle_volume = defaultdict(int)
        for w in workouts:
            volume = w.sets * w.reps * w.weight
            muscle = exercise_to_muscle.get(w.exercise, "Other")
            muscle_volume[muscle] += volume

        labels = list(muscle_volume.keys())
        sizes = list(muscle_volume.values())
        explode = [0.1 if i == max(sizes) else 0 for i in sizes]
        
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.pie(sizes, explode=explode, labels=labels, autopct="%1.1f%%", shadow=True, startangle=90)
        ax.axis("equal")

        # Save to graphs directory
        muscle_path = GRAPHS_DIR / "muscle_distribution.png"
        plt.savefig(muscle_path)
        plt.close(fig)

        await callback_query.message.answer_photo(photo=FSInputFile(muscle_path))
        
        await state.set_state(StatsForm.choice_type)
        await callback_query.message.answer(
            "What stats do you want to see?",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Overall")],
                    [KeyboardButton(text="Progression")],
                ],
                resize_keyboard=True,
            )
        )


# ============================================================================
# Heat Map
# ============================================================================

@stats_router.message(StatsForm.progression_state, F.text.casefold() == "heat map")
async def process_heat_map(message: Message, state: FSMContext):
    """Generate workout frequency heatmap"""
    await state.set_state(StatsForm.heat_map_state)
    user_id = message.from_user.id

    with SessionLocal() as session:
        workouts = session.query(Workout).filter(Workout.user_id == user_id).all()
        
        heatmap_data = defaultdict(lambda: [0, 0, 0, 0])
        for w in workouts:
            month = w.created_at.month
            week_of_month = min((w.created_at.day - 1) // 7, 3)
            heatmap_data[month][week_of_month] += 1

        df = pd.DataFrame.from_dict(
            heatmap_data,
            orient="index",
            columns=["Week 1", "Week 2", "Week 3", "Week 4"]
        )

        df = df.sort_index()
        df.index = df.index.map(lambda m: calendar.month_abbr[m])

        plt.figure(figsize=(10, 8))
        sns.heatmap(df, annot=True, cmap="YlOrRd", cbar=True, fmt="d")
        plt.title("Workout Frequency per Month/Week")
        plt.xlabel("Week of Month")
        plt.ylabel("Month")
        
        # Save to graphs directory
        heatmap_path = GRAPHS_DIR / "heatmap.png"
        plt.savefig(heatmap_path)
        plt.close()

        photo = FSInputFile(heatmap_path)
        await message.answer_photo(photo, caption="Your week by week heatmap")

    await state.clear()


# ============================================================================
# Recommendations
# ============================================================================

@stats_router.message(StatsForm.choice_type, F.text.casefold() == "get recommendations")
async def process_recommendations(message: Message, state: FSMContext):
    """Generate training recommendations based on weak points"""
    await state.set_state(StatsForm.recommendations_state)
    user_id = message.from_user.id

    with SessionLocal() as session:
        overall_weekly_data = await compute_weekly_volume(user_id=user_id, session=session)
        overall_muscle_group_data = await compute_muscle_group_stats(
            user_id=user_id,
            session=session,
            current_time=datetime.now(timezone.utc)
        )

    await state.update_data(weekly_volume=overall_weekly_data)
    await state.update_data(muscle_group_stats=overall_muscle_group_data)

    weekly_volumes = group_muscle_volume_by_week(overall_muscle_group_data)

    # Calculate relative volumes
    relative_volumes = {}
    for muscle, weeks in weekly_volumes.items():
        rel = {}
        for week_start, muscle_vol in weeks.items():
            week_str = str(week_start)
            total = overall_weekly_data.get(week_str, 0)
            if total and total > 0:
                rel[week_str] = (muscle_vol / total) * 100
            else:
                rel[week_str] = 0.0
        relative_volumes[muscle] = rel

    # Find weak points
    weak_points = []
    num_muscles = len(relative_volumes) if relative_volumes else 0
    expected_percentage = (100 / num_muscles) if num_muscles else 0
    
    for muscle, week_data in relative_volumes.items():
        for week_str, relative_volume in week_data.items():
            if expected_percentage and relative_volume < expected_percentage * 0.7:
                weak_points.append({
                    "muscle_group": muscle,
                    "week": week_str,
                    "relative_volume": relative_volume,
                    "deficit": expected_percentage - relative_volume
                })

    if weak_points:
        lines = []
        for wp in weak_points:
            mg = wp.get("muscle_group")
            week = wp.get("week")
            rel = wp.get("relative_volume", 0.0)
            deficit = wp.get("deficit", 0.0)
            lines.append(f"{mg} — week {week}: {rel:.1f}% of weekly volume (deficit {deficit:.1f}%)")
        message_text = "Weak points detected:\n" + "\n".join(lines)
    else:
        message_text = "No weak points detected. Great job!"

    await message.answer(message_text)
    await state.set_state(StatsForm.choice_type)