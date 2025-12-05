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

from localization.utils import t
from bot.features.dev1_workout_tracking.services import get_lang

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
    lang = get_lang(message.from_user.id)
    await state.set_state(StatsForm.choice_type)
    await state.update_data(lang=lang)

    await message.answer(
        t("stats_main_menu", lang),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=t("stats_btn_overall", lang))],
                [KeyboardButton(text=t("stats_btn_progression", lang))],
                [KeyboardButton(text=t("stats_btn_recommendations", lang))],
            ],
            resize_keyboard=True,
        ),
    )


# ============================================================================
# Overall Stats - Time Period Selection
# ============================================================================

@stats_router.message(StatsForm.choice_type, F.text.in_(["Overall", "Общая"]))
async def process_overall_choice(message: Message, state: FSMContext):
    """Handle 'Overall' statistics choice"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    await state.update_data(choice_type="overall")
    await state.set_state(StatsForm.time_period)
    await message.answer(
        t("stats_choose_period", lang),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=t("stats_btn_today", lang))],
                [KeyboardButton(text=t("stats_btn_week", lang))],
                [KeyboardButton(text=t("stats_btn_alltime", lang))]
            ],
            resize_keyboard=True,
        ),
    )


@stats_router.message(StatsForm.time_period)
async def process_time_period(message: Message, state: FSMContext):
    """Process time period selection and show workouts"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    time_period = message.text.strip()
    user_id = message.from_user.id
    now = datetime.now(timezone.utc)

    with SessionLocal() as session:
        query = session.query(Workout).filter(Workout.user_id == user_id)

        # Check both English and Russian button text
        if time_period in [t("stats_btn_today", "en"), t("stats_btn_today", "ru")]:
            start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
            query = query.filter(Workout.created_at >= start, Workout.created_at <= now)
        elif time_period in [t("stats_btn_week", "en"), t("stats_btn_week", "ru")]:
            start = now - timedelta(days=7)
            query = query.filter(Workout.created_at >= start, Workout.created_at <= now)

        results = query.order_by(Workout.created_at.desc()).all()

        if not results:
            await message.answer(t("stats_no_workouts", lang))
        else:
            text = "\n".join(
                f"{w.created_at:%d-%m %H:%M} — {w.exercise} {w.sets}x{w.reps}x{w.weight} kg"
                for w in results
            )
            await message.answer(t("stats_your_workouts", lang, workouts=text))

    await state.set_state(StatsForm.choice_type)
    await message.answer(
        t("stats_main_menu", lang),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=t("stats_btn_overall", lang))],
                [KeyboardButton(text=t("stats_btn_progression", lang))],
                [KeyboardButton(text=t("stats_btn_recommendations", lang))],
            ],
            resize_keyboard=True,
        )
    )


# ============================================================================
# Progression Choice
# ============================================================================

@stats_router.message(StatsForm.choice_type, F.text.in_(["Progression", "Прогресс"]))
async def process_progression_choice(message: Message, state: FSMContext):
    """Handle 'Progression' statistics choice"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    await state.update_data(choice_type="progression")
    await state.set_state(StatsForm.progression_state)
    await message.answer(
        t("stats_choose_progression", lang),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=t("stats_btn_best_lift", lang))],
                [KeyboardButton(text=t("stats_btn_volume", lang))],
                [KeyboardButton(text=t("stats_btn_muscle_dist", lang))],
                [KeyboardButton(text=t("stats_btn_heatmap", lang))]
            ],
            resize_keyboard=True,
        ),
    )


# ============================================================================
# Best Lift Progression
# ============================================================================

@stats_router.message(StatsForm.progression_state, F.text.in_(["Best Lift", "Лучший подъём"]))
async def process_best_lift(message: Message, state: FSMContext):
    """Start best lift progression flow"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    await state.update_data(progression="best_lift")
    await state.set_state(StatsForm.best_lift)
    await message.answer(
        t("stats_enter_exercise", lang),
        reply_markup=ReplyKeyboardRemove(),
    )


@stats_router.message(StatsForm.best_lift)
async def process_best_lift_exercise_choice(message: Message, state: FSMContext):
    """Process exercise choice and show weekly progression"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

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
            await message.answer(t("stats_no_data_exercise", lang, exercise=exercise))
            await state.clear()
            return

        weekly_max = defaultdict(int)
        for w in results:
            week_start = (w.created_at - timedelta(days=w.created_at.weekday())).date()
            weekly_max[week_start] = max(weekly_max[week_start], w.weight)

        lines = []
        for week_start, max_weight in weekly_max.items():
            week_str = week_start.strftime("%Y-%m-%d")
            lines.append(t("stats_week_result", lang, week=week_str, weight=max_weight))

        text = "\n".join(lines)
        await message.answer(t("stats_weekly_progression", lang, progression=text))

        await state.update_data(weekly_max={str(k): v for k, v in weekly_max.items()})
        await state.set_state(StatsForm.best_lift_action)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t("stats_btn_graph", lang), callback_data="graph")],
            [InlineKeyboardButton(text=t("stats_btn_orm", lang), callback_data="orm")],
            [InlineKeyboardButton(text=t("stats_btn_back", lang), callback_data="Back")],
        ])
        await message.answer(t("stats_choose_option", lang), reply_markup=keyboard)


@stats_router.callback_query(F.data.in_(["graph", "orm", "Back"]))
async def graph_or_ORM(callback: CallbackQuery, state: FSMContext):
    """Handle graph/ORM/back callback buttons"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    choice = callback.data
    await callback.answer()

    if choice == "graph":
        weekly_max = {datetime.fromisoformat(k): v for k, v in data.get("weekly_max", {}).items()}
        weeks = list(weekly_max.keys())
        weights = list(weekly_max.values())

        if not weeks:
            await callback.message.answer(t("stats_no_weekly_data", lang))
            return

        plt.figure(figsize=(10, 6))
        plt.plot(weeks, weights, marker="o", linestyle="-", color="blue")
        plt.xticks(rotation=45, ha="right", fontsize=10)
        plt.title("Best Lift Progression")
        plt.xlabel("Week")
        plt.ylabel("Max Weight (kg)")
        plt.tight_layout()

        progress_path = GRAPHS_DIR / "progress.png"
        plt.savefig(progress_path)
        plt.close()

        photo = FSInputFile(progress_path)
        await callback.message.answer_photo(photo, caption=t("stats_graph_caption", lang))

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t("stats_btn_graph", lang), callback_data="graph")],
            [InlineKeyboardButton(text=t("stats_btn_orm", lang), callback_data="orm")],
            [InlineKeyboardButton(text=t("stats_btn_back", lang), callback_data="Back")],
        ])
        await callback.message.answer(t("stats_choose_option", lang), reply_markup=keyboard)

    elif choice == "orm":
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
                    t("stats_orm_result", lang, exercise=exercise_choice, weight=f"{best_lift:.1f}")
                )
            else:
                await callback.message.answer(t("stats_no_data_exercise", lang, exercise=exercise_choice))

        await state.clear()

    elif choice == "Back":
        await state.set_state(StatsForm.choice_type)
        await callback.message.answer(
            t("stats_main_menu", lang),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text=t("stats_btn_overall", lang))],
                    [KeyboardButton(text=t("stats_btn_progression", lang))]
                ],
                resize_keyboard=True,
            ),
        )


# ============================================================================
# Volume Progression
# ============================================================================

@stats_router.message(StatsForm.progression_state, F.text.in_(["Volume", "Объём"]))
async def process_volume(message: Message, state: FSMContext):
    """Process volume progression"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

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
            lines.append(t("stats_volume_week", lang, week=week_str, volume=volume))

        text = "\n".join(lines)
        await message.answer(
            t("stats_weekly_progression", lang, progression=text),
            reply_markup=ReplyKeyboardRemove()
        )
        await message.answer(t("stats_type_chart", lang))
        await state.set_state(StatsForm.chart_state)


@stats_router.message(StatsForm.chart_state)
async def process_chart(message: Message, state: FSMContext):
    """Generate volume progression chart"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

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

    volume_path = GRAPHS_DIR / "volume_progress.png"
    plt.savefig(volume_path)
    plt.close()

    photo = FSInputFile(volume_path)
    await message.answer_photo(photo, caption=t("stats_volume_caption", lang))

    await state.set_state(StatsForm.choice_type)
    await message.answer(
        t("stats_main_menu", lang),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=t("stats_btn_overall", lang))],
                [KeyboardButton(text=t("stats_btn_progression", lang))]
            ],
            resize_keyboard=True,
        ),
    )


# ============================================================================
# Muscle Group Distribution
# ============================================================================

@stats_router.message(StatsForm.progression_state, F.text.in_(["Muscle Groups", "Группы мышц"]))
async def process_muscle_grp_distribution(message: Message, state: FSMContext):
    """Show muscle group distribution menu"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    await state.set_state(StatsForm.muscle_grp_state)
    await message.answer(t("stats_muscle_menu", lang), reply_markup=ReplyKeyboardRemove())
    user_id = message.from_user.id

    with SessionLocal() as session:
        results = (
            session.query(Workout)
            .filter(Workout.user_id == user_id)
            .order_by(Workout.created_at.desc())
            .all()
        )

        if not results:
            await message.answer(t("stats_no_workouts", lang))
            return

        workouts_by_date = defaultdict(list)
        for w in results:
            workout_date = w.created_at.date()
            workouts_by_date[workout_date].append(w)

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"{date:%d-%m-%Y} — {len(workouts_by_date[date])} {t('stats_exercises', lang)}",
                        callback_data=f"workout_{date}"
                    )
                ]
                for date in sorted(workouts_by_date.keys(), reverse=True)
            ]
        )

        await message.answer(t("stats_select_workout_date", lang), reply_markup=keyboard)


@stats_router.callback_query(lambda c: c.data.startswith("workout_"))
async def workout_selected(callback_query: CallbackQuery, state: FSMContext):
    """Show muscle distribution pie chart for selected date"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

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

        muscle_path = GRAPHS_DIR / "muscle_distribution.png"
        plt.savefig(muscle_path)
        plt.close(fig)

        await callback_query.message.answer_photo(photo=FSInputFile(muscle_path))

        await state.set_state(StatsForm.choice_type)
        await callback_query.message.answer(
            t("stats_main_menu", lang),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text=t("stats_btn_overall", lang))],
                    [KeyboardButton(text=t("stats_btn_progression", lang))],
                ],
                resize_keyboard=True,
            )
        )


# ============================================================================
# Heat Map
# ============================================================================

@stats_router.message(StatsForm.progression_state, F.text.in_(["Heat Map", "Тепловая карта"]))
async def process_heat_map(message: Message, state: FSMContext):
    """Generate workout frequency heatmap"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

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

        heatmap_path = GRAPHS_DIR / "heatmap.png"
        plt.savefig(heatmap_path)
        plt.close()

        photo = FSInputFile(heatmap_path)
        await message.answer_photo(photo, caption=t("stats_heatmap_caption", lang))

    await state.clear()


# ============================================================================
# Recommendations
# ============================================================================

@stats_router.message(StatsForm.choice_type, F.text.in_(["Recommendations", "Рекомендации"]))
async def process_recommendations(message: Message, state: FSMContext):
    """Generate training recommendations based on weak points"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

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
            lines.append(t("stats_weak_point", lang, muscle=mg, week=week, volume=f"{rel:.1f}", deficit=f"{deficit:.1f}"))
        message_text = t("stats_weak_points_detected", lang, points="\n".join(lines))
    else:
        message_text = t("stats_no_weak_points", lang)

    await message.answer(message_text)
    await state.set_state(StatsForm.choice_type)