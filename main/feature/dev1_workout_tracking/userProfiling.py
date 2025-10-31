from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .db import SessionLocal
from .models import User
from sqlalchemy import func
from datetime import datetime, timezone


def get_or_create_user(telegram_id: int, username: str = None,
                       first_name: str = None, last_name: str = None) -> User:
    """
    Получает пользователя из базы или создает нового.

    Args:
        telegram_id (int): ID пользователя в Telegram
        username (str, optional): username пользователя
        first_name (str, optional): Имя пользователя
        last_name (str, optional): Фамилия пользователя

    Returns:
        User: Объект пользователя
    """
    session = SessionLocal()
    try:
        # Пытаемся найти пользователя
        user = session.query(User).filter_by(telegram_id=telegram_id).first()

        if user:
            # Обновляем данные если пользователь найден
            if username and username != user.username:
                user.username = username
            if first_name and first_name != user.first_name:
                user.first_name = first_name
            if last_name and last_name != user.last_name:
                user.last_name = last_name
        else:
            # Создаем нового пользователя
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

    except IntegrityError:
        session.rollback()
        # Если произошла ошибка уникальности, пытаемся снова найти пользователя
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        return user
    finally:
        session.close()


def get_user_by_telegram_id(telegram_id: int) -> User:
    """
    Находит пользователя по Telegram ID.

    Args:
        telegram_id (int): ID пользователя в Telegram

    Returns:
        User: Объект пользователя или None если не найден
    """
    session = SessionLocal()
    try:
        return session.query(User).filter_by(telegram_id=telegram_id).first()
    finally:
        session.close()


def update_user_timezone(telegram_id: int, timezone_offset: int) -> bool:
    """
    Обновляет часовой пояс пользователя.

    Args:
        telegram_id (int): ID пользователя в Telegram
        timezone_offset (int): Смещение часового пояса (например, 3 для UTC+3)

    Returns:
        bool: True если обновление прошло успешно
    """
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if user:
            # Здесь можно добавить поле timezone_offset в модель User
            # user.timezone_offset = timezone_offset
            session.commit()
            return True
        return False
    finally:
        session.close()


def get_all_users() -> list[User]:
    """
    Получает всех пользователей бота.

    Returns:
        list[User]: Список всех пользователей
    """
    session = SessionLocal()
    try:
        return session.query(User).all()
    finally:
        session.close()


def get_user_profile(telegram_id: int) -> dict:
    """
    Получает полную информацию о пользователе включая статистику.

    Args:
        telegram_id (int): ID пользователя в Telegram

    Returns:
        dict: Словарь с информацией о пользователе
    """
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            return None

        # Получаем статистику тренировок
        from .models import Workout
        workout_stats = session.query(
            func.count(Workout.id).label('total_workouts'),
            func.max(Workout.created_at).label('last_workout'),
            func.min(Workout.created_at).label('first_workout')
        ).filter(Workout.user_id == telegram_id).first()

        return {
            'user': user,
            'total_workouts': workout_stats.total_workouts if workout_stats else 0,
            'last_workout': workout_stats.last_workout if workout_stats else None,
            'first_workout': workout_stats.first_workout if workout_stats else None
        }
    finally:
        session.close()


def increment_workout_count(telegram_id: int):
    """
    Увеличивает счетчик тренировок пользователя.

    Args:
        telegram_id (int): ID пользователя в Telegram
    """
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if user:
            user.workout_count += 1
            session.commit()
    finally:
        session.close()


def ensure_aware_datetime(dt: datetime) -> datetime:
    """
    Преобразует naive datetime в aware (UTC).

    Args:
        dt (datetime): Время для преобразования

    Returns:
        datetime: aware datetime в UTC
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt