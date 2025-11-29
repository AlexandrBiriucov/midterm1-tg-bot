"""
Service layer for custom routines (Dev4 feature).
Handles all database operations for workout routines.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session
from bot.core.database import get_session
from bot.core.models import CustomRoutine, User


def save_custom_routine(
    user_id: int,
    name: str,
    exercises: list | dict,
    description: str = None,
    level: str = None,
    schedule: str = None,
    is_preset: bool = False
) -> CustomRoutine:
    """
    Save a new custom routine.
    
    Args:
        user_id: Telegram user ID
        name: Routine name
        exercises: List of exercises or dict with exercise data
        description: Optional description
        level: Optional level (beginner/intermediate/advanced)
        schedule: Optional schedule text
        is_preset: Whether this is a preset routine
        
    Returns:
        CustomRoutine: Created routine object
    """
    with get_session() as session:
        # Ensure exercises is proper format
        if isinstance(exercises, list):
            exercises_data = {"exercises": exercises}
        else:
            exercises_data = exercises
            
        routine = CustomRoutine(
            user_id=user_id,
            name=name,
            description=description,
            level=level,
            schedule=schedule,
            exercises=exercises_data,
            is_preset=is_preset
        )
        
        session.add(routine)
        session.commit()
        session.refresh(routine)
        
        return routine


def get_user_routines(user_id: int, level: str = None) -> list[CustomRoutine]:
    """
    Get all routines for a user, optionally filtered by level.
    
    Args:
        user_id: Telegram user ID
        level: Optional level filter
        
    Returns:
        list[CustomRoutine]: List of user's routines
    """
    with get_session() as session:
        query = select(CustomRoutine).where(CustomRoutine.user_id == user_id)
        
        if level:
            query = query.where(CustomRoutine.level == level)
            
        query = query.order_by(CustomRoutine.created_at.desc())
        
        routines = session.execute(query).scalars().all()
        
        # Detach from session
        return [session.merge(r, load=False) for r in routines]


def get_routine_by_id(routine_id: int, user_id: int = None) -> CustomRoutine | None:
    """
    Get a specific routine by ID.
    
    Args:
        routine_id: Routine ID
        user_id: Optional user ID to verify ownership
        
    Returns:
        CustomRoutine | None: Routine object or None if not found
    """
    with get_session() as session:
        query = select(CustomRoutine).where(CustomRoutine.routine_id == routine_id)
        
        if user_id:
            query = query.where(CustomRoutine.user_id == user_id)
            
        routine = session.execute(query).scalar_one_or_none()
        
        if routine:
            return session.merge(routine, load=False)
        return None


def delete_routine(routine_id: int, user_id: int) -> bool:
    """
    Delete a routine.
    
    Args:
        routine_id: Routine ID to delete
        user_id: User ID to verify ownership
        
    Returns:
        bool: True if deleted, False if not found
    """
    with get_session() as session:
        routine = session.execute(
            select(CustomRoutine)
            .where(CustomRoutine.routine_id == routine_id)
            .where(CustomRoutine.user_id == user_id)
        ).scalar_one_or_none()
        
        if routine:
            session.delete(routine)
            session.commit()
            return True
        return False


def update_routine_usage(routine_id: int):
    """
    Increment the usage counter for a routine.
    
    Args:
        routine_id: Routine ID
    """
    with get_session() as session:
        routine = session.execute(
            select(CustomRoutine).where(CustomRoutine.routine_id == routine_id)
        ).scalar_one_or_none()
        
        if routine:
            routine.times_used += 1
            session.commit()


def get_preset_routines(level: str = None) -> list[dict]:
    """
    Get preset routines. Since presets are defined in code,
    this returns the PRESET_ROUTINES dict filtered by level.
    
    Args:
        level: Optional level filter
        
    Returns:
        list[dict]: List of preset routine data
    """
    from bot.features.dev4_custom_routines.handlers import PRESET_ROUTINES
    
    if level:
        return {
            k: v for k, v in PRESET_ROUTINES.items() 
            if v.get('level') == level
        }
    return PRESET_ROUTINES


def search_routines(user_id: int, search_term: str) -> list[CustomRoutine]:
    """
    Search user's routines by name or description.
    
    Args:
        user_id: Telegram user ID
        search_term: Search term
        
    Returns:
        list[CustomRoutine]: Matching routines
    """
    with get_session() as session:
        query = (
            select(CustomRoutine)
            .where(CustomRoutine.user_id == user_id)
            .where(
                (CustomRoutine.name.like(f"%{search_term}%")) |
                (CustomRoutine.description.like(f"%{search_term}%"))
            )
        )
        
        routines = session.execute(query).scalars().all()
        return [session.merge(r, load=False) for r in routines]


def get_routine_stats(user_id: int) -> dict:
    """
    Get statistics about user's routines.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        dict: Statistics (total_routines, most_used, etc.)
    """
    with get_session() as session:
        routines = session.execute(
            select(CustomRoutine)
            .where(CustomRoutine.user_id == user_id)
        ).scalars().all()
        
        if not routines:
            return {
                "total_routines": 0,
                "most_used": None,
                "total_usage": 0
            }
        
        most_used = max(routines, key=lambda r: r.times_used)
        total_usage = sum(r.times_used for r in routines)
        
        return {
            "total_routines": len(routines),
            "most_used": most_used.name,
            "most_used_count": most_used.times_used,
            "total_usage": total_usage
        }