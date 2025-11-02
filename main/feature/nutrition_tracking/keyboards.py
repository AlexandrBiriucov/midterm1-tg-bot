from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_main_menu():
    """Create the main menu keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍔 Add Food", callback_data="nutrition_add_food")],
        [InlineKeyboardButton(text="📊 Daily Summary", callback_data="nutrition_daily_summary")],
        [InlineKeyboardButton(text="🎯 Set Goals", callback_data="nutrition_set_goals")],
        [InlineKeyboardButton(text="📋 View Meals", callback_data="nutrition_view_meals")],
    ])
    return keyboard


def create_meal_type_keyboard():
    """Create meal type selection keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🥞 Breakfast", callback_data="nutrition_meal:breakfast")],
        [InlineKeyboardButton(text="🥗 Lunch", callback_data="nutrition_meal:lunch")],
        [InlineKeyboardButton(text="🍽️ Dinner", callback_data="nutrition_meal:dinner")],
        [InlineKeyboardButton(text="🍎 Snack", callback_data="nutrition_meal:snack")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="nutrition_main_menu")]
    ])
    return keyboard


def create_food_results_keyboard(foods):
    """Create keyboard with food search results"""
    builder = InlineKeyboardBuilder()
    
    for i, food in enumerate(foods[:5]):
        name = food.get('description', 'Unknown food')
        fdc_id = food.get('fdcId')
        
        display_name = name[:35] + "..." if len(name) > 35 else name
        
        builder.add(InlineKeyboardButton(
            text=f"{display_name}",
            callback_data=f"nutrition_select_food:{fdc_id}"
        ))
    
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data="nutrition_add_food"))
    
    return builder.as_markup()


def create_back_keyboard(callback_data="nutrition_main_menu"):
    """Create keyboard with back button"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Back", callback_data=callback_data)]
    ])
    return keyboard


def create_goal_setting_method_keyboard():
    """Create keyboard for choosing goal setting method"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ Enter Manually", callback_data="nutrition_goal_manual")],
        [InlineKeyboardButton(text="🧮 Food Calculator", callback_data="nutrition_goal_calculator")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="nutrition_main_menu")]
    ])
    return keyboard


def create_gender_keyboard():
    """Create keyboard for gender selection"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨 Male", callback_data="nutrition_gender:male")],
        [InlineKeyboardButton(text="👩 Female", callback_data="nutrition_gender:female")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="nutrition_set_goals")]
    ])
    return keyboard


def create_activity_level_keyboard():
    """Create keyboard for activity level selection"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛋️ Sedentary (little/no exercise)", callback_data="nutrition_activity:1.2")],
        [InlineKeyboardButton(text="🚶 Light (1-3 days/week)", callback_data="nutrition_activity:1.375")],
        [InlineKeyboardButton(text="🏃 Moderate (3-5 days/week)", callback_data="nutrition_activity:1.55")],
        [InlineKeyboardButton(text="💪 Active (6-7 days/week)", callback_data="nutrition_activity:1.725")],
        [InlineKeyboardButton(text="🏋️ Very Active (2x per day)", callback_data="nutrition_activity:1.9")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="nutrition_set_goals")]
    ])
    return keyboard


def create_goal_type_keyboard():
    """Create keyboard for goal type selection"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📉 Weight Loss", callback_data="nutrition_goaltype:loss")],
        [InlineKeyboardButton(text="⚖️ Maintain Weight", callback_data="nutrition_goaltype:maintain")],
        [InlineKeyboardButton(text="📈 Weight Gain", callback_data="nutrition_goaltype:gain")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="nutrition_set_goals")]
    ])
    return keyboard