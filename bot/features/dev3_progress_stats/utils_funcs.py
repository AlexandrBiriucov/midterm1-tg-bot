"""
Utility functions for statistics calculations - Dev3 Feature
"""
from collections import defaultdict
from datetime import datetime, timedelta
from bot.core.models import Workout
from .muscle_groups import exercise_to_muscle


def one_rep_max(weight: float, reps: int) -> float:
    """
    Estimate 1RM using Brzycki formula
    
    Args:
        weight: Weight lifted
        reps: Number of repetitions
        
    Returns:
        Estimated one-rep max
        
    Raises:
        ValueError: If reps >= 37 or weight <= 0
    """
    if reps >= 37:
        raise ValueError("Reps must be less than 37 for this formula")
    if weight <= 0:
        raise ValueError("Weight should not be less than 0")
    
    return weight * (36 / (37 - reps))


def calculate_volume(sets: int, reps: int, weight: float) -> float:
    """
    Calculate total volume for a workout
    
    Args:
        sets: Number of sets
        reps: Number of reps per set
        weight: Weight used
        
    Returns:
        Total volume (sets * reps * weight)
    """
    return sets * reps * weight


async def compute_weekly_volume(user_id: int, session) -> dict:
    """
    Compute total weekly training volume for a user
    
    Args:
        user_id: Telegram user ID
        session: SQLAlchemy session
        
    Returns:
        Dictionary mapping week start dates (as strings) to total volume
    """
    weekly_volume = defaultdict(int)
    
    results = session.query(Workout).filter(Workout.user_id == user_id).all()
    
    for w in results:
        # Get Monday of the week
        week_start = (w.created_at - timedelta(days=w.created_at.weekday())).date()
        weekly_volume[week_start] += calculate_volume(w.sets, w.reps, w.weight)
    
    return {str(k): v for k, v in weekly_volume.items()}


async def compute_muscle_group_stats(user_id: int, session, current_time: datetime) -> dict:
    """
    Compute volume per muscle group per day
    
    Args:
        user_id: Telegram user ID
        session: SQLAlchemy session
        current_time: Current datetime for filtering
        
    Returns:
        Nested dictionary: {muscle_group: {date: volume}}
    """
    workouts = (
        session.query(Workout)
        .filter(
            Workout.user_id == user_id,
            Workout.created_at <= current_time
        )
        .all()
    )

    muscle_volume = defaultdict(lambda: defaultdict(int))
    
    for w in workouts:
        date = w.created_at.date()
        volume = w.sets * w.reps * w.weight
        muscle = exercise_to_muscle.get(w.exercise, "Other")
        muscle_volume[muscle][date] += volume

    return {m: dict(dates) for m, dates in muscle_volume.items()}


def group_muscle_volume_by_week(muscle_volumes: dict) -> dict:
    """
    Group daily muscle volumes into weekly totals
    
    Args:
        muscle_volumes: Dictionary from compute_muscle_group_stats
        
    Returns:
        Nested dictionary: {muscle_group: {week_start: total_volume}}
    """
    weekly_data = {}

    for muscle, daily_data in muscle_volumes.items():
        weekly_volume = defaultdict(int)
        
        for day, volume in daily_data.items():
            # Compute start of the week (Monday)
            week_start = day - timedelta(days=day.weekday())
            weekly_volume[week_start] += volume
        
        weekly_data[muscle] = dict(weekly_volume)

    return weekly_data