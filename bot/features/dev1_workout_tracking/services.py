"""
Бизнес-логика для работы с тренировками и пользователями.
Все операции с БД вынесены сюда из handlers.
"""
from sqlalchemy import extract, func
from datetime import datetime, timezone, date, timedelta
from typing import Optional

from bot.core.models import User, Workout
from bot.core.database import get_session


# ==========================================
# РАБОТА С ПОЛЬЗОВАТЕЛЯМИ
# ==========================================

def get_or_create_user(
    telegram_id: int,
    username: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None
) -> User:
    """
    Получает пользователя из БД или создаёт нового.
    Обновляет данные если они изменились.
    """
    with get_session() as session:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        
        if user:
            # Обновляем данные если изменились
            updated = False
            if username and username != user.username:
                user.username = username
                updated = True
            if first_name and first_name != user.first_name:
                user.first_name = first_name
                updated = True
            if last_name and last_name != user.last_name:
                user.last_name = last_name
                updated = True
            
            if updated:
                user.updated_at = datetime.now(timezone.utc)
                session.commit()
        else:
            # Создаём нового пользователя
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            session.add(user)
            session.commit()
        
        session.refresh(user)
        return user


def get_user_profile(telegram_id: int) -> dict | None:
    """
    Получает полную информацию о пользователе + статистику.
    """
    with get_session() as session:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            return None
        
        # Статистика тренировок
        workout_stats = session.query(
            func.count(Workout.workout_id).label('total_workouts'),
            func.max(Workout.created_at).label('last_workout'),
            func.min(Workout.created_at).label('first_workout')
        ).filter(Workout.user_id == telegram_id).first()
        
        return {
            'user': user,
            'total_workouts': workout_stats.total_workouts or 0,
            'last_workout': workout_stats.last_workout,
            'first_workout': workout_stats.first_workout
        }


def increment_workout_count(telegram_id: int):
    """Увеличивает счётчик тренировок пользователя"""
    with get_session() as session:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if user:
            user.workout_count += 1
            session.commit()


# ==========================================
# РАБОТА С ТРЕНИРОВКАМИ
# ==========================================

def log_workout(
    telegram_id: int,
    exercise: str,
    sets: int,
    reps: int,
    weight: float
) -> tuple[Workout, float, float]:
    """
    Логирует тренировку и возвращает данные о новом и предыдущем 1RM.
    
    Returns:
        (workout, new_orm, prev_orm)
    """
    with get_session() as session:
        # Создаём запись тренировки
        workout = Workout(
            user_id=telegram_id,
            exercise=exercise,
            sets=sets,
            reps=reps,
            weight=weight,
            created_at=datetime.now(timezone.utc)
        )
        session.add(workout)
        session.commit()
        session.refresh(workout)
        
        # Вычисляем 1RM для нового сета
        new_orm = calculate_one_rep_max(weight, reps)
        
        # Получаем предыдущий лучший 1RM
        prev_workouts = (
            session.query(Workout)
            .filter(
                Workout.user_id == telegram_id,
                Workout.exercise.ilike(exercise),
                Workout.workout_id != Workout.workout_id
            )
            .all()
        )
        
        prev_orm = 0.0
        if prev_workouts:
            prev_orm = max(
                calculate_one_rep_max(w.weight, w.reps) 
                for w in prev_workouts
            )
        
        # Увеличиваем счётчик
        increment_workout_count(telegram_id)
        
        return workout, new_orm, prev_orm


def get_today_workouts(telegram_id: int) -> list[Workout]:
    """Возвращает все тренировки за сегодня"""
    with get_session() as session:
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        workouts = (
            session.query(Workout)
            .filter(
                Workout.user_id == telegram_id,
                Workout.created_at >= today,
                Workout.created_at < tomorrow
            )
            .order_by(Workout.created_at.asc())
            .all()
        )
        
        return workouts


def get_workouts_by_date(telegram_id: int, target_date: date) -> list[Workout]:
    """Возвращает тренировки за конкретную дату"""
    with get_session() as session:
        start_dt = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_dt = start_dt + timedelta(days=1)
        
        workouts = (
            session.query(Workout)
            .filter(
                Workout.user_id == telegram_id,
                Workout.created_at >= start_dt,
                Workout.created_at < end_dt
            )
            .order_by(Workout.created_at.asc())
            .all()
        )
        
        return workouts


def get_training_days_by_year(telegram_id: int, year: int) -> dict[int, list[int]]:
    """
    Возвращает словарь: месяц -> список дней с тренировками.
    """
    with get_session() as session:
        workouts = (
            session.query(Workout)
            .filter(
                Workout.user_id == telegram_id,
                extract('year', Workout.created_at) == year
            )
            .order_by(Workout.created_at.asc())
            .all()
        )
        
        if not workouts:
            return {}
        
        # Группируем по месяцам
        monthly_data = {}
        for workout in workouts:
            month = workout.created_at.month
            day = workout.created_at.day
            
            if month not in monthly_data:
                monthly_data[month] = set()
            monthly_data[month].add(day)
        
        # Преобразуем в отсортированные списки
        return {
            month: sorted(days) 
            for month, days in monthly_data.items()
        }


# ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================

def calculate_one_rep_max(weight: float, reps: int) -> float:
    """
    Вычисляет 1RM по формуле Brzycki.
    1RM = weight / (1.0278 - 0.0278 * reps)
    """
    if reps == 1:
        return weight
    if reps > 36:  # Защита от некорректных данных
        return weight
    return weight / (1.0278 - 0.0278 * reps)


def ensure_aware_datetime(dt: datetime) -> datetime:
    """Преобразует naive datetime в aware (UTC)"""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt