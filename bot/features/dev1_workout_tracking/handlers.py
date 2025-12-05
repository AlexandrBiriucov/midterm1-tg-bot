"""
Handlers for workout tracking.
All business logic is extracted to services.py
"""
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from datetime import datetime, date
import re

from localization.utils import t

from .services import (
    get_or_create_user,
    log_workout,
    get_today_workouts,
    get_workouts_by_date,
    get_training_days_by_year,
    get_user_profile,
    ensure_aware_datetime,
    get_lang
)

router = Router(name="workout_tracking")


@router.message(Command("log"))
async def log_workout_handler(message: Message):
    """
    Logs a workout.
    Format: /log Exercise 3x10x50
    """
    lang = get_lang(message.from_user.id)

    # Create/update user
    get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )

    # Parse command
    parts = message.text.strip().split(maxsplit=2)
    if len(parts) < 3:
        return await message.answer(
            t("invalid_format", lang),
            parse_mode="HTML"
        )

    exercise = parts[1]

    # Parse sets x reps x weight
    pattern = re.match(r"^(\d+)x(\d+)x(\d+(?:\.\d+)?)$", parts[2])
    if not pattern:
        return await message.answer(
            t("invalid_weight", lang),
            parse_mode="HTML"
        )

    sets, reps, weight = pattern.groups()
    sets, reps, weight = int(sets), int(reps), float(weight)

    # Validation
    if sets <= 0 or reps <= 0 or weight <= 0:
        return await message.answer(
            t("zero", lang)
        )

    try:
        # Log workout
        workout, new_orm, prev_orm = log_workout(
            telegram_id=message.from_user.id,
            exercise=exercise,
            sets=sets,
            reps=reps,
            weight=weight
        )

        # Check for new record
        if new_orm > prev_orm and prev_orm > 0:
            await message.answer(
                t("new_record", lang,
                  exercise=exercise,
                  new_orm=f"{new_orm:.1f}",
                  prev_orm=f"{prev_orm:.1f}"),
                parse_mode="HTML"
            )

        await message.answer(
            t("logged_success", lang,
              exercise=exercise,
              sets=sets,
              reps=reps,
              weight=weight),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(t("error_1", lang, error=e))


@router.message(Command("today"))
async def today(message: Message):
    """Shows today's workouts"""
    lang = get_lang(message.from_user.id)

    try:
        workouts = get_today_workouts(message.from_user.id)

        if not workouts:
            today_date = date.today()
            return await message.answer(
                t("no_records_today", lang, date=today_date.strftime("%d.%m.%Y"))
            )

        # Format output
        today_date = date.today()
        lines = [
            f"<code>{w.created_at:%H:%M}</code> - <b>{w.exercise}</b> {w.sets}x{w.reps}x{w.weight}kg"
            for w in workouts
        ]

        await message.answer(
            t("workouts_for_date", lang,
              date=today_date.strftime("%d.%m.%Y"),
              workouts="\n".join(lines)),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(t("error_retrieving", lang, error=e))


@router.message(Command("check_training"))
async def check_training(message: Message):
    """
    Shows workouts for a specific date.
    Format: /check_training DD.MM.YYYY
    """
    lang = get_lang(message.from_user.id)

    parts = message.text.split()
    if len(parts) != 2:
        return await message.answer(
            t("invalid_check_training_format", lang),
            parse_mode="HTML"
        )

    date_str = parts[1]

    # Parse date
    try:
        target_date = datetime.strptime(date_str, "%d.%m.%Y").date()
    except ValueError:
        return await message.answer(
            t("invalid_date_format", lang),
            parse_mode="HTML"
        )

    try:
        # Get workouts
        workouts = get_workouts_by_date(message.from_user.id, target_date)

        if not workouts:
            return await message.answer(
                t("no_workout_records", lang, date=target_date.strftime("%d.%m.%Y"))
            )

        # Format output
        lines = [
            f"<code>{w.created_at:%H:%M}</code> - <b>{w.exercise}</b> {w.sets}x{w.reps}x{w.weight}kg"
            for w in workouts
        ]

        await message.answer(
            t("workouts_for_target_date", lang,
              date=target_date.strftime("%d.%m.%Y"),
              workouts="\n".join(lines)),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(t("error_retrieving_data", lang, error=e))


@router.message(Command("list_trainings"))
async def list_trainings(message: Message):
    """
    Shows workout calendar for the year.
    Format: /list_trainings [year]
    """
    lang = get_lang(message.from_user.id)

    parts = message.text.split()

    if len(parts) == 1:
        year = datetime.now().year
    elif len(parts) == 2:
        try:
            year = int(parts[1])
            if year < 2000 or year > 2100:
                return await message.answer(t("year_range_error", lang))
        except ValueError:
            return await message.answer(
                t("invalid_year_format", lang),
                parse_mode="HTML"
            )
    else:
        return await message.answer(
            t("invalid_list_trainings_format", lang),
            parse_mode="HTML"
        )

    try:
        # Get data
        monthly_data = get_training_days_by_year(message.from_user.id, year)

        if not monthly_data:
            return await message.answer(t("no_workout_records_year", lang, year=year))

        # Month names
        month_names = {
            1: t("month_january", lang),
            2: t("month_february", lang),
            3: t("month_march", lang),
            4: t("month_april", lang),
            5: t("month_may", lang),
            6: t("month_june", lang),
            7: t("month_july", lang),
            8: t("month_august", lang),
            9: t("month_september", lang),
            10: t("month_october", lang),
            11: t("month_november", lang),
            12: t("month_december", lang)
        }

        # Format output
        lines = []
        for month_num in sorted(monthly_data.keys()):
            month_name = month_names.get(month_num, f"Month {month_num}")
            days = ", ".join(map(str, monthly_data[month_num]))
            lines.append(f"<b>{month_name}:</b> {days}")

        await message.answer(
            t("training_days_year", lang, year=year, days="\n".join(lines)),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(t("error_retrieving_data", lang, error=e))


@router.message(Command("profile"))
async def show_profile(message: Message):
    """Shows user profile with complete statistics"""
    lang = get_lang(message.from_user.id)

    try:
        profile_data = get_user_profile(message.from_user.id)

        if not profile_data or not profile_data['user']:
            return await message.answer(
                t("profile_not_found", lang)
            )

        user = profile_data['user']
        created_at = ensure_aware_datetime(user.created_at)
        updated_at = ensure_aware_datetime(user.updated_at)

        # Build profile
        profile_text = t("user_profile", lang) + "\n\n"
        profile_text += t("profile_id", lang, telegram_id=user.telegram_id) + "\n"
        profile_text += t("profile_name", lang, name=user.first_name or t("not_specified", lang)) + "\n"

        if user.last_name:
            profile_text += t("profile_last_name", lang, last_name=user.last_name) + "\n"
        if user.username:
            profile_text += t("profile_username", lang, username=user.username) + "\n"

        profile_text += t("profile_language", lang, language=user.language) + "\n"
        profile_text += t("profile_timezone", lang, timezone=user.timezone_offset) + "\n\n"

        # Statistics
        profile_text += t("workout_statistics", lang) + "\n\n"
        profile_text += t("total_workouts", lang, count=profile_data['total_workouts']) + "\n"
        profile_text += t("records_in_bot", lang, count=user.workout_count) + "\n"

        if profile_data['first_workout']:
            first_date = ensure_aware_datetime(profile_data['first_workout'])
            profile_text += t("first_workout", lang, date=first_date.strftime("%d.%m.%Y")) + "\n"

        if profile_data['last_workout']:
            last_date = ensure_aware_datetime(profile_data['last_workout'])
            profile_text += t("last_workout", lang, date=last_date.strftime("%d.%m.%Y")) + "\n"

        profile_text += "\n" + t("registered", lang, date=created_at.strftime("%d.%m.%Y %H:%M")) + "\n"
        profile_text += t("updated", lang, date=updated_at.strftime("%d.%m.%Y %H:%M"))

        await message.answer(profile_text, parse_mode="HTML")
    except Exception as e:
        await message.answer(t("error_retrieving_profile", lang, error=e))


@router.message(Command("stats"))
async def show_stats(message: Message):
    """Shows brief workout statistics"""
    lang = get_lang(message.from_user.id)

    try:
        profile_data = get_user_profile(message.from_user.id)

        if not profile_data or profile_data['total_workouts'] == 0:
            return await message.answer(
                t("no_workout_records_yet", lang)
            )

        # Calculate active days
        from datetime import timezone
        now_utc = datetime.now(timezone.utc)
        created_at = ensure_aware_datetime(profile_data['user'].created_at)
        days_active = max((now_utc - created_at).days, 1)

        stats_text = t("your_statistics", lang) + "\n\n"
        stats_text += t("total_workouts_stat", lang, count=profile_data['total_workouts']) + "\n"

        if profile_data['last_workout']:
            last_workout = ensure_aware_datetime(profile_data['last_workout'])
            stats_text += t("last_workout_stat", lang, date=last_workout.strftime("%d.%m.%Y")) + "\n"

        stats_text += t("active_days", lang, days=days_active) + "\n"

        avg_workouts = profile_data['total_workouts'] / days_active
        stats_text += t("average_per_day", lang, avg=f"{avg_workouts:.2f}")

        await message.answer(stats_text, parse_mode="HTML")
    except Exception as e:
        await message.answer(t("error_retrieving_statistics", lang, error=e))