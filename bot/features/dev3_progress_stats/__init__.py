"""
Dev3: Progress Statistics & Analysis Module

This module provides comprehensive workout statistics including:
- Overall workout summaries (today/week/all-time)
- Best lift progression tracking with graphs
- Volume progression analysis
- Muscle group distribution visualization
- Training frequency heatmaps
- Personalized training recommendations

All data is stored in the unified database (bot/core/models.py).
"""

from .stats_handlers import stats_router
from .utils_funcs import (
    one_rep_max,
    calculate_volume,
    compute_weekly_volume,
    compute_muscle_group_stats,
    group_muscle_volume_by_week
)

__all__ = [
    'stats_router',
    'one_rep_max',
    'calculate_volume',
    'compute_weekly_volume',
    'compute_muscle_group_stats',
    'group_muscle_volume_by_week'
]