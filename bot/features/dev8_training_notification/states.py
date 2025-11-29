from aiogram.fsm.state import State, StatesGroup


class NotificationStates(StatesGroup):
    """FSM States for training notifications"""
    waiting_for_time = State()
    waiting_for_custom_reminder = State()