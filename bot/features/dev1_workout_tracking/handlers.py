"""
Handlers for workout tracking.
All business logic is extracted to services.py
"""
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from datetime import datetime, date
import re

from .services import (
    get_or_create_user,
    log_workout,
    get_today_workouts,
    get_workouts_by_date,
    get_training_days_by_year,
    get_user_profile,
    ensure_aware_datetime
)

router = Router(name="workout_tracking")


@router.message(Command("log"))
async def log_workout_handler(message: Message):
    """
    Logs a workout.
    Format: /log Exercise 3x10x50
    """
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
            "❌ Invalid format!\n"
            "Use: <code>/log Exercise 3x10x50</code>\n"
            "Example: <code>/log BenchPress 3x10x50</code>",
            parse_mode="HTML"
        )
    
    exercise = parts[1]
    
    # Parse sets x reps x weight
    pattern = re.match(r"^(\d+)x(\d+)x(\d+(?:\.\d+)?)$", parts[2])
    if not pattern:
        return await message.answer(
            "❌ Invalid weight format!\n"
            "Example: <code>/log BenchPress 3x10x50</code>",
            parse_mode="HTML"
        )
    
    sets, reps, weight = pattern.groups()
    sets, reps, weight = int(sets), int(reps), float(weight)
    
    # Validation
    if sets <= 0 or reps <= 0 or weight <= 0:
        return await message.answer("❌ Values must be greater than zero!")
    
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
                f"🏆 <b>New record for {exercise}!</b>\n"
                f"1RM: {new_orm:.1f} kg (previous: {prev_orm:.1f} kg)",
                parse_mode="HTML"
            )
        
        await message.answer(
            f"✅ Logged: <b>{exercise}</b> — {sets}x{reps}x{weight} kg",
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(f"❌ Error logging workout: {e}")


@router.message(Command("today"))
async def today(message: Message):
    """Shows today's workouts"""
    try:
        workouts = get_today_workouts(message.from_user.id)
        
        if not workouts:
            today_date = date.today()
            return await message.answer(
                f"📝 No records for today ({today_date:%d.%m.%Y}).\n"
                "Use /log to record a workout!"
            )
        
        # Format output
        today_date = date.today()
        lines = [
            f"<code>{w.created_at:%H:%M}</code> - <b>{w.exercise}</b> {w.sets}x{w.reps}x{w.weight}kg"
            for w in workouts
        ]
        
        await message.answer(
            f"🏋️ <b>Workouts for {today_date:%d.%m.%Y}:</b>\n\n"
            + "\n".join(lines),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(f"❌ Error retrieving data: {e}")


@router.message(Command("check_training"))
async def check_training(message: Message):
    """
    Shows workouts for a specific date.
    Format: /check_training DD.MM.YYYY
    """
    parts = message.text.split()
    if len(parts) != 2:
        return await message.answer(
            "❌ Invalid command format.\n"
            "Use: <code>/check_training DD.MM.YYYY</code>\n"
            "Example: <code>/check_training 03.09.2025</code>",
            parse_mode="HTML"
        )
    
    date_str = parts[1]
    
    # Parse date
    try:
        target_date = datetime.strptime(date_str, "%d.%m.%Y").date()
    except ValueError:
        return await message.answer(
            "❌ Invalid date format.\n"
            "Use: <code>DD.MM.YYYY</code>\n"
            "Example: <code>03.09.2025</code>",
            parse_mode="HTML"
        )
    
    try:
        # Get workouts
        workouts = get_workouts_by_date(message.from_user.id, target_date)
        
        if not workouts:
            return await message.answer(
                f"📝 No workout records for {target_date:%d.%m.%Y}."
            )
        
        # Format output
        lines = [
            f"<code>{w.created_at:%H:%M}</code> - <b>{w.exercise}</b> {w.sets}x{w.reps}x{w.weight}kg"
            for w in workouts
        ]
        
        await message.answer(
            f"🏋️ <b>Workouts for {target_date:%d.%m.%Y}:</b>\n\n"
            + "\n".join(lines),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(f"❌ Error retrieving data: {e}")


@router.message(Command("list_trainings"))
async def list_trainings(message: Message):
    """
    Shows workout calendar for the year.
    Format: /list_trainings [year]
    """
    parts = message.text.split()
    
    if len(parts) == 1:
        year = datetime.now().year
    elif len(parts) == 2:
        try:
            year = int(parts[1])
            if year < 2000 or year > 2100:
                return await message.answer("❌ Year must be between 2000 and 2100")
        except ValueError:
            return await message.answer(
                "❌ Invalid year format.\n"
                "Use: <code>/list_trainings [year]</code>\n"
                "Example: <code>/list_trainings 2024</code>",
                parse_mode="HTML"
            )
    else:
        return await message.answer(
            "❌ Invalid command format.\n"
            "Use: <code>/list_trainings [year]</code>\n"
            "Example: <code>/list_trainings 2024</code>",
            parse_mode="HTML"
        )
    
    try:
        # Get data
        monthly_data = get_training_days_by_year(message.from_user.id, year)
        
        if not monthly_data:
            return await message.answer(f"📝 No workout records for {year}.")
        
        # Month names
        month_names = {
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August",
            9: "September", 10: "October", 11: "November", 12: "December"
        }
        
        # Format output
        lines = []
        for month_num in sorted(monthly_data.keys()):
            month_name = month_names.get(month_num, f"Month {month_num}")
            days = ", ".join(map(str, monthly_data[month_num]))
            lines.append(f"<b>{month_name}:</b> {days}")
        
        await message.answer(
            f"📅 <b>Training days in {year}:</b>\n\n"
            + "\n".join(lines),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(f"❌ Error retrieving data: {e}")


@router.message(Command("profile"))
async def show_profile(message: Message):
    """Shows user profile with complete statistics"""
    try:
        profile_data = get_user_profile(message.from_user.id)
        
        if not profile_data or not profile_data['user']:
            return await message.answer(
                "❌ Profile not found.\n"
                "Use /start to register."
            )
        
        user = profile_data['user']
        created_at = ensure_aware_datetime(user.created_at)
        updated_at = ensure_aware_datetime(user.updated_at)
        
        # Build profile
        profile_text = f"👤 <b>User Profile</b>\n\n"
        profile_text += f"🆔 ID: <code>{user.telegram_id}</code>\n"
        profile_text += f"👤 Name: {user.first_name or 'Not specified'}\n"
        
        if user.last_name:
            profile_text += f"📛 Last name: {user.last_name}\n"
        if user.username:
            profile_text += f"🌐 Username: @{user.username}\n"
        
        profile_text += f"🗣 Language: {user.language}\n"
        profile_text += f"🌍 Timezone: UTC+{user.timezone_offset}\n\n"
        
        # Statistics
        profile_text += f"🏋️‍♂️ <b>Workout Statistics</b>\n\n"
        profile_text += f"📊 Total workouts: {profile_data['total_workouts']}\n"
        profile_text += f"🔢 Records in bot: {user.workout_count}\n"
        
        if profile_data['first_workout']:
            first_date = ensure_aware_datetime(profile_data['first_workout'])
            profile_text += f"📅 First workout: {first_date:%d.%m.%Y}\n"
        
        if profile_data['last_workout']:
            last_date = ensure_aware_datetime(profile_data['last_workout'])
            profile_text += f"⏰ Last workout: {last_date:%d.%m.%Y}\n"
        
        profile_text += f"\n📅 Registered: {created_at:%d.%m.%Y %H:%M}\n"
        profile_text += f"🔄 Updated: {updated_at:%d.%m.%Y %H:%M}"
        
        await message.answer(profile_text, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Error retrieving profile: {e}")


@router.message(Command("stats"))
async def show_stats(message: Message):
    """Shows brief workout statistics"""
    try:
        profile_data = get_user_profile(message.from_user.id)
        
        if not profile_data or profile_data['total_workouts'] == 0:
            return await message.answer(
                "📊 You don't have any workout records yet.\n"
                "Use /log to record your first workout!"
            )
        
        # Calculate active days
        from datetime import timezone
        now_utc = datetime.now(timezone.utc)
        created_at = ensure_aware_datetime(profile_data['user'].created_at)
        days_active = max((now_utc - created_at).days, 1)
        
        stats_text = f"📊 <b>Your Statistics</b>\n\n"
        stats_text += f"🏋️‍♂️ Total workouts: {profile_data['total_workouts']}\n"
        
        if profile_data['last_workout']:
            last_workout = ensure_aware_datetime(profile_data['last_workout'])
            stats_text += f"⏰ Last workout: {last_workout:%d.%m.%Y}\n"
        
        stats_text += f"📅 Active days: {days_active}\n"
        
        avg_workouts = profile_data['total_workouts'] / days_active
        stats_text += f"📈 Average per day: {avg_workouts:.2f}"
        
        await message.answer(stats_text, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Error retrieving statistics: {e}")