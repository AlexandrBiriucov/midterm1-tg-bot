"""
Dev4 Custom Routines Module
Provides workout routine management functionality.
"""

from .handlers import routine_router, PRESET_ROUTINES
from .services import (
    save_custom_routine,
    get_user_routines,
    get_routine_by_id,
    delete_routine,
    update_routine_usage,
    get_routine_stats,
    search_routines
)
from .states import RoutineCreationForm

__all__ = [
    # Router
    'routine_router',
    
    # Constants
    'PRESET_ROUTINES',
    
    # Service functions
    'save_custom_routine',
    'get_user_routines',
    'get_routine_by_id',
    'delete_routine',
    'update_routine_usage',
    'get_routine_stats',
    'search_routines',
    
    # States
    'RoutineCreationForm',
]