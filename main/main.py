import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
# Импорт внешних пакетов из requirements.txt

# Добавляем папку feature в путь поиска модулей
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'feature'))

# (Даниил) Импорт моих скриптов
from feature.dev1_workout_tracking.db import init_db
from feature.dev1_workout_tracking.workout_tracking import router as workout_router
from feature.dev1_workout_tracking.userProfiling import get_or_create_user

# (Даниил) Импорт скриптов Макса
from feature.dev5_rest_timers.handlers import router as dev5_router
from feature.nutrition_tracking.handlers import router as nutrition_router

# Импорт модуля уведомлений о тренировках
from feature.training_notification.handlers import router as notification_router

# Импорт модуля библиотеки упражнений (dev2)
from feature.dev2_exercise_library.exercise_handlers import exercise_router

# from dev2_module import router as dev2_router
from feature.dev3_progress_stats.stats_main import stats_router as dev3_router
# ... и так далее для dev4, dev5, dev6

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(TOKEN)
Dispatcher = Dispatcher()

# Роутер для основных команд из скрипта main.py
main_router = Router()
echo_router = Router()

# Включаем (include) все роутеры в диспетчере
# Включение main роутера
Dispatcher.include_router(main_router)

# Включение роутеров разработчиков
Dispatcher.include_router(workout_router)
Dispatcher.include_router(exercise_router)  # Роутер библиотеки упражнений
Dispatcher.include_router(dev5_router)
Dispatcher.include_router(dev3_router)
Dispatcher.include_router(nutrition_router)
Dispatcher.include_router(notification_router)

# Включение эхо роутера
Dispatcher.include_router(echo_router)
# dp.include_router(dev3_router)
# ... и так далее

async def main():
    # Инициализируем базу данных
    init_db()

    # Инициализируем сессию для nutrition_bot
    from feature.nutrition_tracking.services import nutrition_bot
    await nutrition_bot.ensure_session()
    
    # Инициализируем базу данных для уведомлений
    from feature.training_notification.database import init_db as init_notification_db
    init_notification_db()

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

    await m.answer(f"Hello, {m.from_user.first_name}! I will help you log workouts. To see all functions: /help")

@main_router.message(Command("help"))
async def on_help(m: Message):
    help_text = """
Available commands:

📝 Workouts:
/log BenchPress 3x10x50 — log an exercise
/today — show today's entries

🍽️ Nutrition:
/nutrition — open the nutrition tracker menu

🔔 Notifications:
/notification — set up workout reminders

⏱️ Rest Timers:
/timer — manage rest timers

📊 Statistics:
/statistics — view progress statistics
    """
    await m.answer(help_text)

# Эхо-хэндлер тоже можно оставить здесь или вынести в основной main.py
@echo_router.message(F.text)
async def echo(m: Message):
    await m.answer(f"You wrote: {m.text}\nUse /help for a list of commands.")

if __name__ == "__main__":
    asyncio.run(main())