# workout_tracking.py
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from .db import SessionLocal
from .models import Workout
import re
from datetime import datetime, timezone, date, timedelta
from sqlalchemy import select, extract
from .userProfiling import get_or_create_user, get_user_by_telegram_id,increment_workout_count,get_user_profile,ensure_aware_datetime

# Создаем свой собственный роутер для этого модуля
router = Router()

# Регистрируем хэндлеры на этом роутере

@router.message(Command("log"))
async def log_workout(m: Message):
    user = get_user_by_telegram_id(m.from_user.id)
    if not user:
        # Если пользователя нет, создаем его
        user = get_or_create_user(
            telegram_id=m.from_user.id,
            username=m.from_user.username,
            first_name=m.from_user.first_name,
            last_name=m.from_user.last_name
        )
    # ... (весь код функции остается без изменений)
    parts = m.text.strip().split(maxsplit=2)
    if len(parts) < 3:
        return await m.answer("Формат: /log Exercise 3x10x50")

    exercise = parts[1]
    m2 = re.match(r"^(\d+)x(\d+)x(\d+)$", parts[2])
    if not m2:
        return await m.answer("Пример: /log BenchPress 3x10x50")

    sets, reps, weight = map(int, m2.groups())

    session = SessionLocal()
    try:
        w = Workout(
            user_id=m.from_user.id,
            exercise=exercise,
            sets=sets,
            reps=reps,
            weight=weight,
            created_at=datetime.now(timezone.utc),
        )
        session.add(w)
        session.commit()
        # Увеличиваем счетчик тренировок
        increment_workout_count(m.from_user.id)

        await m.answer(f"Записал: {exercise} — {sets}x{reps}x{weight} кг ✅")
    finally:
        session.close()


@router.message(Command("today"))
async def today(m: Message):
    session = SessionLocal()
    try:
        # Получаем сегодняшнюю дату (без времени)
        today_date = date.today()

        # Выбираем только записи за сегодня
        q = (select(Workout)
             .where(Workout.user_id == m.from_user.id)
             .where(Workout.created_at >= today_date)
             .order_by(Workout.created_at.asc()))  # Сортировка по времени от старых к новым

        rows = session.execute(q).scalars().all()

        if not rows:
            return await m.answer(f"За сегодня ({today_date:%d.%m.%Y}) записей нет.")

        # Форматируем вывод с сетами, повторениями и весом
        lines = [f"{r.created_at:%H:%M} - {r.exercise} {r.sets}x{r.reps}x{r.weight}кг" for r in rows]

        await m.answer(
            f"❕ Формат: Время - Упражнение Сеты х Повторения х Вес \n" +
            f"Упражнения записанные сегодня ({today_date:%d.%m.%Y}):\n \n" +
            "\n".join(lines)
        )
    finally:
        session.close()


from datetime import datetime


@router.message(Command("check_training"))
async def check_training(m: Message):
    # Проверяем правильность формата команды
    parts = m.text.split()
    if len(parts) != 2:
        return await m.answer(
            "❌ Неправильный формат команды.\nИспользуйте: /check_training ДД.ММ.ГГГГ\nПример: /check_training 03.09.2025")

    date_str = parts[1]

    # Пытаемся распарсить дату
    try:
        target_date = datetime.strptime(date_str, "%d.%m.%Y").date()
    except ValueError:
        return await m.answer("❌ Неправильный формат даты.\nИспользуйте: ДД.ММ.ГГГГ\nПример: 03.09.2025")

    session = SessionLocal()
    try:
        # Выбираем записи за указанную дату
        q = (select(Workout)
             .where(Workout.user_id == m.from_user.id)
             .where(Workout.created_at >= target_date)
             .where(Workout.created_at < target_date + timedelta(days=1))
             .order_by(Workout.created_at.asc()))

        rows = session.execute(q).scalars().all()

        if not rows:
            return await m.answer(f"📝 За {target_date:%d.%m.%Y} записей тренировок нет.")

        # Форматируем вывод
        lines = [f"{r.created_at:%H:%M} - {r.exercise} {r.sets}x{r.reps}x{r.weight}кг" for r in rows]

        await m.answer(
            f"❕ Формат: Время - Упражнение Сеты х Повторения х Вес \n" +
            f"Упражнения записанные за {target_date:%d.%m.%Y}:\n \n" +
            "\n".join(lines)
        )
    finally:
        session.close()

@router.message(Command("list_trainings"))
async def list_trainings(m: Message):
    session = SessionLocal()
    try:
        # Парсим аргументы команды
        parts = m.text.split()
        year = None

        if len(parts) == 1:
            # /list_trainings - текущий год
            year = datetime.now().year
        elif len(parts) == 2:
            # /list_trainings год
            try:
                year = int(parts[1])
                if year < 2000 or year > 2100:
                    return await m.answer("❌ Год должен быть между 2000 и 2100")
            except ValueError:
                return await m.answer(
                    "❌ Неправильный формат года.\nИспользуйте: /list_trainings [год]\nПример: /list_trainings 2024")
        else:
            return await m.answer(
                "❌ Неправильный формат команды.\nИспользуйте: /list_trainings [год]\nПример: /list_trainings 2024")

        # Получаем все тренировки за указанный год
        q = (select(Workout)
             .where(Workout.user_id == m.from_user.id)
             .where(extract('year', Workout.created_at) == year)
             .order_by(Workout.created_at.asc()))

        rows = session.execute(q).scalars().all()

        if not rows:
            return await m.answer(f"📝 За {year} год записей тренировок нет.")

        # Группируем по месяцам
        monthly_data = {}
        for r in rows:
            month = r.created_at.month
            day = r.created_at.day
            if month not in monthly_data:
                monthly_data[month] = []
            monthly_data[month].append(day)

        # Сортируем дни и убираем дубликаты (если несколько тренировок в день)
        for month in monthly_data:
            monthly_data[month] = sorted(set(monthly_data[month]))

        # Русские названия месяцев
        month_names = {
            1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
            5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
            9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
        }

        # Форматируем вывод
        lines = []
        for month_num in sorted(monthly_data.keys()):
            month_name = month_names.get(month_num, f"Месяц {month_num}")
            days = ", ".join(map(str, monthly_data[month_num]))
            lines.append(f"{month_name}: {days}")

        await m.answer(
            f"❕ Формат: Месяц: Числа \n \n" +
            f"Записанные тренировки в {year} году:\n\n" +
            "\n".join(lines)
        )

    finally:
        session.close()


@router.message(Command("profile"))
async def show_profile(m: Message):
    """
    Показывает профиль пользователя с полной информацией и статистикой.
    """
    profile_data = get_user_profile(m.from_user.id)

    if not profile_data or not profile_data['user']:
        return await m.answer("❌ Профиль не найден. Используйте /start для регистрации.")

    user = profile_data['user']

    created_at = ensure_aware_datetime(user.created_at)
    updated_at = ensure_aware_datetime(user.updated_at)

    # Форматируем информацию о пользователе
    profile_text = f"👤 <b>Профиль пользователя</b>\n\n"
    profile_text += f"🆔 ID: <code>{user.telegram_id}</code>\n"
    profile_text += f"👤 Имя: {user.first_name or 'Не указано'}\n"
    profile_text += f"📛 Фамилия: {user.last_name or 'Не указано'}\n"
    profile_text += f"🌐 Username: @{user.username or 'Не указан'}\n"
    profile_text += f"🗣 Язык: {user.language}\n"
    profile_text += f"🌍 Часовой пояс: UTC+{user.timezone_offset}\n\n"

    # Статистика тренировок
    profile_text += f"🏋️‍♂️ <b>Статистика тренировок</b>\n\n"
    profile_text += f"📊 Всего тренировок: {profile_data['total_workouts']}\n"
    profile_text += f"🔢 Записей в боте: {user.workout_count}\n"

    if profile_data['first_workout']:
        first_date = profile_data['first_workout'].strftime("%d.%m.%Y")
        profile_text += f"📅 Первая тренировка: {first_date}\n"

    if profile_data['last_workout']:
        last_date = profile_data['last_workout'].strftime("%d.%m.%Y")
        profile_text += f"⏰ Последняя тренировка: {last_date}\n"

    profile_text += f"📅 Дата регистрации: {created_at.strftime('%d.%m.%Y %H:%M')}\n"
    profile_text += f"🔄 Последнее обновление: {updated_at.strftime('%d.%m.%Y %H:%M')}\n\n"
    profile_text += "💡 <i>Используйте /settings для изменения настроек</i>"

    await m.answer(profile_text, parse_mode="HTML")


@router.message(Command("stats"))
async def show_stats(m: Message):
    """
    Показывает краткую статистику тренировок.
    """
    profile_data = get_user_profile(m.from_user.id)

    if not profile_data:
        return await m.answer("📊 У вас еще нет записей тренировок.")

    # Используем функцию для обеспечения aware datetime
    now_utc = ensure_aware_datetime(datetime.now(timezone.utc))
    created_at = ensure_aware_datetime(profile_data['user'].created_at)

    days_active = (now_utc - created_at).days

    stats_text = f"📊 <b>Ваша статистика</b>\n\n"
    stats_text += f"🏋️‍♂️ Всего тренировок: {profile_data['total_workouts']}\n"

    if profile_data['last_workout']:
        last_workout = ensure_aware_datetime(profile_data['last_workout'])
        last_date = last_workout.strftime("%d.%m.%Y")
        stats_text += f"⏰ Последняя тренировка: {last_date}\n"

    stats_text += f"📅 Активен дней: {days_active}\n"

    if days_active > 0:
        avg_workouts = profile_data['total_workouts'] / days_active
        stats_text += f"📈 Среднее в день: {avg_workouts:.1f} тренировок"
    else:
        stats_text += "📈 Среднее в день: 0 тренировок"

    await m.answer(stats_text, parse_mode="HTML")

# Функция для получения роутера из этого модуля (опционально, но удобно)
def get_router():
    return router