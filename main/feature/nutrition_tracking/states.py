from aiogram.fsm.state import State, StatesGroup

class NutritionStates(StatesGroup):
    waiting_for_search = State()
    waiting_for_portion = State()
    setting_goals = State()
    waiting_for_goal_calories = State()
    waiting_for_goal_protein = State()
    waiting_for_goal_carbs = State()
    waiting_for_goal_fat = State()
