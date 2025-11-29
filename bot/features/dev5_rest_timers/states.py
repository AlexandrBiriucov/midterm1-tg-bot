"""
FSM States for timer preset creation and management.
"""
from aiogram.fsm.state import State, StatesGroup


class TimerPresetForm(StatesGroup):
    """States for creating/editing timer presets"""
    waiting_for_name = State()
    waiting_for_time = State()