"""
Main entry point for the GymBot.
Initialization and launch of all components.
"""
import sys
from pathlib import Path

# Add project root to PYTHONPATH
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from bot.config import BOT_TOKEN
from bot.core.database import init_db
from bot.features.dev1_workout_tracking.handlers import router as workout_router
from bot.features.dev1_workout_tracking.services import get_or_create_user
from bot.features.dev2_exercise_library.exercise_handlers import exercise_router
from bot.features.dev2_exercise_library.exercise_db import ExerciseDatabase
from bot.features.dev3_progress_stats.stats_handlers import stats_router
from bot.features.dev4_custom_routines.handlers import routine_router
from bot.features.dev5_rest_timers.handlers import router as timer_router
from bot.features.dev7_nutrition_tracking.handlers import router as nutrition_router
from bot.features.dev8_training_notification.handlers import router as notification_router


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create bot and dispatcher
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# Main router for start/help commands
main_router = Router()

# Echo router (last in chain)
echo_router = Router()


@main_router.message(CommandStart())
async def on_start(m: Message):
    """Welcome message"""
    # Create/get user on start
    get_or_create_user(
        telegram_id=m.from_user.id,
        username=m.from_user.username,
        first_name=m.from_user.first_name,
        last_name=m.from_user.last_name
    )

    welcome_text = f"""
👋 <b>Hey, {m.from_user.first_name}!</b>

I'm your personal fitness assistant! I'll help you with:

🏋️ <b>Workout Tracking</b>
   • Log exercises and sets
   • Create custom workout routines
   • View training history

📚 <b>Exercise Library</b>
   • 270+ exercises with detailed instructions
   • Filter by muscle group, equipment, difficulty
   • Professional technique tips
   • Use /exercise to browse

📊 <b>Progress Monitoring</b>
   • Analyze statistics
   • Track personal records
   • Visualize results
   • Use /statistics to explore

🎯 <b>Custom Routines</b>
   • Browse preset workout programs
   • Create your own training plans
   • Track routine usage
   • Use /routines and /custom_routines

⏱️ <b>Rest Timers</b>
   • Set custom timers for rest periods
   • Save timer presets for quick access
   • Use /timer to get started

🍎 <b>Nutrition Tracking</b>
   • Track calories and macronutrients
   • Search 350,000+ foods via USDA database
   • Set personalized nutrition goals
   • View daily nutrition summary
   • Use /nutrition to start

📅 <b>Training Notifications</b>
   • Schedule workout reminders
   • Custom notification times
   • Weekly training schedule
   • Use /notification to set up

Use /help to see all available commands!
"""
    
    await m.answer(welcome_text, parse_mode="HTML")


@main_router.message(Command("help"))
async def on_help(m: Message):
    """List of all commands"""
    help_text = """
📋 <b>Available Commands:</b>

<b>🏋️ Workouts:</b>
/log (e.g., BenchPress 3x10x50) - Log an exercise 
/today - Show today's workouts
/check_training (e.g., 03.09.2025) - Check workouts by date
/list_trainings - List training days by year
/profile - View your profile

<b>🎯 Workout Routines:</b>
/routines - Browse preset workout programs by level
/custom_routines - Create and manage your own routines

<b>📊 Statistics & Progress:</b>
/statistics - View comprehensive statistics

<b>📚 Exercise Library:</b>
/exercise - Browse exercise database 
/exercise_stats - View library statistics

<b>⏱️ Rest Timers:</b>
/timer - Set and manage rest timers

<b>🍎 Nutrition Tracking:</b>
/nutrition - Track meals and macros

<b>📅 Training Notifications:</b>
/notification - Manage training reminders

"""
    
    await m.answer(help_text, parse_mode="HTML")


@echo_router.message(F.text)
async def echo(m: Message):
    """Echo handler for unprocessed messages"""
    await m.answer(
        f"You wrote: {m.text}\n\n"
        "Use /help to view available commands."
    )


async def main():
    """Main startup function"""
    try:
        # Initialize unified database
        logger.info("🗄️ Initializing database...")
        init_db()
        
        # Auto-initialize exercises if database is empty
        logger.info("📚 Checking exercise database...")
        exercise_db = ExerciseDatabase()
        exercise_db.auto_initialize_if_empty()
        
        # Include routers in dispatcher (order matters!)
        dp.include_router(main_router)
        dp.include_router(workout_router)         # Dev1: Workout tracking
        dp.include_router(exercise_router)        # Dev2: Exercise library
        dp.include_router(stats_router)           # Dev3: Statistics & progress
        dp.include_router(routine_router)         # Dev4: Custom routines
        dp.include_router(timer_router)           # Dev5: Rest timers
        dp.include_router(nutrition_router)       # Dev7: Nutrition tracking
        dp.include_router(notification_router)    # Dev8: Training notifications
        dp.include_router(echo_router)            # Echo always last!
        
        logger.info("🤖 Bot started!")
        logger.info("📚 Exercise library ready")
        logger.info("📊 Statistics module ready")
        logger.info("🎯 Custom routines ready")
        logger.info("⏱️ Timer module ready")
        logger.info("🍎 Nutrition tracking ready")
        logger.info("📅 Training notifications ready")
        
        # Start polling
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Bot startup error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())