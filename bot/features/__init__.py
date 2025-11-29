"""
Dev2 Exercise Library Module
Provides exercise database and filtering functionality using unified database
"""

from .exercise_db import ExerciseDatabase
from .exercise_handlers import exercise_router

__all__ = ['ExerciseDatabase', 'exercise_router']

__version__ = '2.0.0'
__description__ = 'Exercise library integrated with unified SQLAlchemy database'
