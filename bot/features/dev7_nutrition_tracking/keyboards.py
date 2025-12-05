from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from localization.utils import t


def create_main_menu(lang: str = "en"):
    """Create the main menu keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("nutr_btn_add", lang), callback_data="nutrition_add_food")],
        [InlineKeyboardButton(text=t("nutr_btn_summary", lang), callback_data="nutrition_daily_summary")],
        [InlineKeyboardButton(text=t("nutr_btn_goals", lang), callback_data="nutrition_set_goals")],
        [InlineKeyboardButton(text=t("nutr_btn_meals", lang), callback_data="nutrition_view_meals")],
    ])
    return keyboard


def create_meal_type_keyboard(lang: str = "en"):
    """Create meal type selection keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("nutr_btn_breakfast", lang), callback_data="nutrition_meal:breakfast")],
        [InlineKeyboardButton(text=t("nutr_btn_lunch", lang), callback_data="nutrition_meal:lunch")],
        [InlineKeyboardButton(text=t("nutr_btn_dinner", lang), callback_data="nutrition_meal:dinner")],
        [InlineKeyboardButton(text=t("nutr_btn_snack", lang), callback_data="nutrition_meal:snack")],
        [InlineKeyboardButton(text=t("nutr_btn_back", lang), callback_data="nutrition_main_menu")]
    ])
    return keyboard


def create_food_results_keyboard(foods, lang: str = "en"):
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
    builder.row(InlineKeyboardButton(text=t("nutr_btn_back", lang), callback_data="nutrition_add_food"))

    return builder.as_markup()


def create_back_keyboard(callback_data="nutrition_main_menu", lang: str = "en"):
    """Create keyboard with back button"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("nutr_btn_back", lang), callback_data=callback_data)]
    ])
    return keyboard


def create_goal_setting_method_keyboard(lang: str = "en"):
    """Create keyboard for choosing goal setting method"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("nutr_btn_manual", lang), callback_data="nutrition_goal_manual")],
        [InlineKeyboardButton(text=t("nutr_btn_calculator", lang), callback_data="nutrition_goal_calculator")],
        [InlineKeyboardButton(text=t("nutr_btn_back", lang), callback_data="nutrition_main_menu")]
    ])
    return keyboard


def create_gender_keyboard(lang: str = "en"):
    """Create keyboard for gender selection"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("nutr_btn_male", lang), callback_data="nutrition_gender:male")],
        [InlineKeyboardButton(text=t("nutr_btn_female", lang), callback_data="nutrition_gender:female")],
        [InlineKeyboardButton(text=t("nutr_btn_back", lang), callback_data="nutrition_set_goals")]
    ])
    return keyboard


def create_activity_level_keyboard(lang: str = "en"):
    """Create keyboard for activity level selection"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("nutr_btn_minimal", lang), callback_data="nutrition_activity:1.2")],
        [InlineKeyboardButton(text=t("nutr_btn_light", lang), callback_data="nutrition_activity:1.375")],
        [InlineKeyboardButton(text=t("nutr_btn_moderate", lang), callback_data="nutrition_activity:1.55")],
        [InlineKeyboardButton(text=t("nutr_btn_active", lang), callback_data="nutrition_activity:1.725")],
        [InlineKeyboardButton(text=t("nutr_btn_very_active", lang), callback_data="nutrition_activity:1.9")],
        [InlineKeyboardButton(text=t("nutr_btn_back", lang), callback_data="nutrition_set_goals")]
    ])
    return keyboard


def create_goal_type_keyboard(lang: str = "en"):
    """Create keyboard for goal type selection"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("nutr_btn_loss", lang), callback_data="nutrition_goaltype:loss")],
        [InlineKeyboardButton(text=t("nutr_btn_maintain", lang), callback_data="nutrition_goaltype:maintain")],
        [InlineKeyboardButton(text=t("nutr_btn_gain", lang), callback_data="nutrition_goaltype:gain")],
        [InlineKeyboardButton(text=t("nutr_btn_back", lang), callback_data="nutrition_set_goals")]
    ])
    return keyboard