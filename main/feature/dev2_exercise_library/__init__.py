"""
Dev2 Exercise Library Module
Provides exercise database and filtering functionality
"""

from .exercise_db import ExerciseDatabase
from .exercise_handlers import exercise_router

__all__ = ['ExerciseDatabase', 'exercise_router']
