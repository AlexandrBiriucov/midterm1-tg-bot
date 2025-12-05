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
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command

from localization.utils import t

from bot.config import BOT_TOKEN
from bot.core.database import init_db
from bot.features.dev1_workout_tracking.handlers import router as workout_router
from bot.features.dev1_workout_tracking.services import get_or_create_user, get_lang, set_user_language
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
    """Welcome message with language selection"""
    # Create/get user on start
    user = get_or_create_user(
        telegram_id=m.from_user.id,
        username=m.from_user.username,
        first_name=m.from_user.first_name,
        last_name=m.from_user.last_name
    )

    # Check if user has language set
    lang = get_lang(m.from_user.id)

    # If language is not set (new user or default), show language selection
    if not user.language or user.language == "en":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang_en")],
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_ru")]
        ])

        await m.answer(
            "🌍 <b>Welcome! Please choose your language:</b>\n"
            "🌍 <b>Добро пожаловать! Пожалуйста, выберите язык:</b>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        # User already has language set, show welcome
        await show_welcome_message(m, lang)


@main_router.callback_query(F.data.startswith("set_lang_"))
async def set_language_callback(callback: CallbackQuery):
    """Handle language selection"""
    new_lang = callback.data.replace("set_lang_", "")
    user_id = callback.from_user.id

    # Save language to database
    set_user_language(user_id, new_lang)

    # Show welcome message in selected language
    await callback.message.delete()
    await show_welcome_message(callback.message, new_lang)
    await callback.answer()


async def show_welcome_message(m: Message, lang: str):
    """Show welcome message in user's language"""
    welcome_text = t("main_welcome", lang, name=m.from_user.first_name)
    await m.answer(welcome_text, parse_mode="HTML")


@main_router.message(Command("language"))
async def change_language(m: Message):
    """Change bot language"""
    lang = get_lang(m.from_user.id)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang_en")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_ru")]
    ])

    await m.answer(
        t("choose_language", lang),
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@main_router.message(Command("help"))
async def on_help(m: Message):
    """List of all commands"""
    lang = get_lang(m.from_user.id)
    help_text = t("main_help", lang)
    await m.answer(help_text, parse_mode="HTML")


@echo_router.message(F.text)
async def echo(m: Message):
    """Echo handler for unprocessed messages"""
    lang = get_lang(m.from_user.id)
    await m.answer(
        t("echo_message", lang, text=m.text)
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