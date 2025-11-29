"""
Statistics and Progress Tracking Handlers - Dev3 Feature
Integrated with unified database structure
"""
import calendar
import os
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import seaborn as sns

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    Message, 
    ReplyKeyboardMarkup, 
    KeyboardButton,
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    ReplyKeyboardRemove,
    CallbackQuery,
    FSInputFile
)

from bot.core.database import SessionLocal
from bot.core.models import Workout
from .muscle_groups import exercise_to_muscle
from .utils_funcs import (
    one_rep_max,
    calculate_volume,
    compute_weekly_volume,
    compute_muscle_group_stats,
    group_muscle_volume_by_week
)

# Router for statistics feature
stats_router = Router()

# Define the graphs directory path
GRAPHS_DIR = Path(__file__).parent.parent.parent.parent / "data" / "graphs"

# Ensure the graphs directory exists
GRAPHS_DIR.mkdir(parents=True, exist_ok=True)