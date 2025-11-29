"""
FSM States for custom routine creation and management.
"""
from aiogram.fsm.state import State, StatesGroup


class RoutineCreationForm(StatesGroup):
    """States for creating custom workout routines"""
    waiting_for_routine_data = State()