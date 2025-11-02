

import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
from ..dev1_workout_tracking.models import Workout 
from .muscle_groups import exercise_to_muscle

def one_rep_max(weight: float, reps: int) -> float:
    """Estimate 1RM using Brzycki formula"""
    if reps >= 37:
        raise ValueError("Reps must be less than 37 for this formula")
    elif weight <=0:
        raise ValueError("weight should not be less than 0")

    return weight * (36 / (37 - reps))
    
    


def calculate_volume(sets:int,reps:int,weight:float)->float:
    volume=sets*reps*weight
    return volume





async def compute_weekly_volume(user_id: int, session):
    weekly_volume = defaultdict(int)
    try:
        results = session.query(Workout).filter(Workout.user_id == user_id).all()
        print("Queried user_id:", user_id)
        print("Results found:", len(results))
        for w in results:
            print("Workout:", w.exercise, w.sets, w.reps, w.weight, w.created_at)
            week_start = (w.created_at - timedelta(days=w.created_at.weekday())).date()
            weekly_volume[week_start] += calculate_volume(w.sets, w.reps, w.weight)
    finally:
        session.close()
    print("Weekly volume dict:", weekly_volume)
    return {str(k): v for k, v in weekly_volume.items()}






async def compute_muscle_group_stats(user_id: int, session,current_time:datetime):
        try:
        # Fetch all exercises from that date
            workouts = (
                session.query(Workout)
                .filter(
                    Workout.user_id == user_id,
                    Workout.created_at <= current_time
                )
                .all()
            )

            muscle_volume = defaultdict(int)
            for w in workouts:
                volume = w.sets * w.reps * w.weight
                muscle = exercise_to_muscle.get(w.exercise, "Other")
                muscle_volume[muscle] += volume

            return dict(muscle_volume)
        finally:
            session.close()