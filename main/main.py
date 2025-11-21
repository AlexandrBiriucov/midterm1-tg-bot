import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
#Импорт внешних пакетов из requirements.txt

# Добавляем папку feature в путь поиска модулей
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'feature'))
# (Даниил) Импорт моих скриптов.
from feature.dev1_workout_tracking.db import init_db
from feature.dev1_workout_tracking.workout_tracking import router as workout_router
from feature.dev1_workout_tracking.userProfiling import get_or_create_user

# (Даниил) Импорт скриптов Макса.
from feature.dev5_rest_timers.handlers import router as dev5_router
from feature.nutrition_tracking.handlers import router as nutrition_router

# Импорт модуля уведомлений о тренировках
from feature.training_notification.handlers import router as notification_router

from feature.dev2_exercise_library.exercise_handlers import exercise_router
from feature.dev3_progress_stats.stats_main import stats_router as dev3_router
from feature.dev4_custom_routines.handlers.routine_handlers import routine_router

# 🆕 ИМПОРТ БАЗЫ ДАННЫХ ДЛЯ ТАЙМЕРОВ (добавьте эту строку)
from feature.dev5_rest_timers.database import init_db as init_timer_db

# ... и так далее для dev4, dev5, dev6

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(TOKEN)
Dispatcher = Dispatcher()

# Роутер для основных команд из скрипта main.py
main_router = Router()
echo_router = Router()

# Включаем (include) все роутер в диспетчере
# Включение main роутера.
Dispatcher.include_router(main_router)

# Включение роутеров разработчиков.
Dispatcher.include_router(workout_router)
Dispatcher.include_router(exercise_router)
Dispatcher.include_router(dev5_router)
Dispatcher.include_router(dev3_router)
Dispatcher.include_router(nutrition_router)
Dispatcher.include_router(notification_router)
# 🆕 ДОБАВЛЯЕМ ЭТУ СТРОКУ:
Dispatcher.include_router(routine_router)
# Включение эхо роутера.
Dispatcher.include_router(echo_router)
# dp.include_router(dev3_router)
# ... и так далее

async def main():
    # Инициализируем базу данных
    init_db()
    from feature.dev2_exercise_library.exercise_db import ExerciseDatabase
    exercise_db = ExerciseDatabase()
    stats = exercise_db.get_database_stats()
    print(f"✅ Exercise database loaded: {stats['total_exercises']} exercises")
    
    if stats['total_exercises'] == 0:
        print("⚠️  WARNING: Exercise database is empty!")
        print("📝 Run 'python feature/dev2_exercise_library/initialize_exercises.py' to populate it")

    from feature.nutrition_tracking.services import nutrition_bot
    await nutrition_bot.ensure_session()
    
    # Инициализируем базу данных для уведомлений
    from feature.training_notification.database import init_db as init_notification_db
    init_notification_db()

    
    # 🆕 ДОБАВЛЯЕМ ЭТИ 2 СТРОКИ:
    from feature.dev4_custom_routines.db.routine_db import routine_db
    print("✅ Routine system initialized")
    
    # 🆕 ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ ТАЙМЕРОВ (добавьте эти строки)
    await init_timer_db()
    print("✅ Timer database initialized")
    
    # Запускаем поллинг
    await Dispatcher.start_polling(bot)
    

@main_router.message(CommandStart())
async def on_start(m: Message):
    # Создаем/получаем пользователя при старте
    user = get_or_create_user(
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

📊 <b>Progress Monitoring</b>
   • Analyze statistics
   • Track personal records
   • Visualize results

🍎 <b>Nutrition Control</b>
   • Count calories and macros
   • Keep food diary

⏱️ <b>Time Management</b>
   • Rest timers between sets
   • Workout reminders

📚 <b>Exercise Library</b>
   • Database of 90 exercises
   • Detailed technique instructions

Use /help to see all available commands!
"""
    
    await m.answer(welcome_text, parse_mode="HTML")

@main_router.message(Command("help"))
async def on_help(m: Message):
    help_text = """
📋 <b>Available Commands:</b>

<b>🏋️ Workouts:</b>
/log - Log an exercise (e.g., /log BenchPress 3x10x50)
/today - Show today's workouts
/statistics - Overall training statistics
/profile - View your profile

<b>📚 Exercises:</b>
/exercise - Search exercises in library
/exercise_stats - Exercise statistics

<b>🎯 Workout Programs:</b>
/routines - Manage training routines
/custom_routines - Add custom routines

<b>🍎 Nutrition:</b>
/nutrition - Track calories and macros

<b>⏱️ Timers:</b>
/timer - Rest timer between sets

<b>🔔 Notifications:</b>
/notification - Set up workout reminders

<b>📊 Progress:</b>
/stats - Detailed progress statistics

<i>Tip: Start with /log command to record your first workout!</i>
"""
    
    await m.answer(help_text, parse_mode="HTML")

# Эхо-хэндлер тоже можно оставить здесь или вынести в основной main.py
@echo_router.message(F.text)
async def echo(m: Message):
    await m.answer(f"Ты написал: {m.text}")

if __name__ == "__main__":
    asyncio.run(main())