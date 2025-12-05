"""
Nutrition tracking handlers for dev7 feature.
Updated to use unified database.
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from datetime import date

from localization.utils import t
from bot.features.dev1_workout_tracking.services import get_lang

from .services import nutrition_bot
from .states import NutritionStates
from .keyboards import (
    create_main_menu,
    create_meal_type_keyboard,
    create_food_results_keyboard,
    create_back_keyboard,
    create_goal_setting_method_keyboard,
    create_gender_keyboard,
    create_activity_level_keyboard,
    create_goal_type_keyboard
)

router = Router()

@router.message(Command("nutrition"))
async def nutrition_start(message: Message, state: FSMContext):
    """Handle /nutrition command"""
    lang = get_lang(message.from_user.id)
    await state.update_data(lang=lang)

    user_id = message.from_user.id
    username = message.from_user.username

    nutrition_bot.db.ensure_user_exists(user_id, username)

    keyboard = create_main_menu()
    await message.answer(t("nutrition_welcome", lang), parse_mode="HTML", reply_markup=keyboard)


@router.callback_query(F.data == "nutrition_main_menu")
async def main_menu_callback(callback: CallbackQuery, state: FSMContext):
    """Handle main menu callback"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    await state.clear()
    await state.update_data(lang=lang)

    keyboard = create_main_menu()
    await callback.message.edit_text(t("nutrition_main_menu_text", lang), parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "nutrition_add_food")
async def add_food_callback(callback: CallbackQuery, state: FSMContext):
    """Handle add food callback"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    keyboard = create_meal_type_keyboard()
    await callback.message.edit_text(t("nutrition_add_food_text", lang), parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("nutrition_meal:"))
async def meal_type_callback(callback: CallbackQuery, state: FSMContext):
    """Handle meal type selection"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    meal_type = callback.data.split(":")[1]
    await state.update_data(meal_type=meal_type)

    meal_emoji = {"breakfast": "🥞", "lunch": "🥗", "dinner": "🍽️", "snack": "🍎"}

    await callback.message.edit_text(
        t("nutrition_enter_food_name", lang, emoji=meal_emoji.get(meal_type, "🍽️"), meal=meal_type.title()),
        parse_mode="HTML",
        reply_markup=create_back_keyboard("nutrition_add_food")
    )
    await state.set_state(NutritionStates.waiting_for_search)
    await callback.answer()


@router.message(NutritionStates.waiting_for_search)
async def handle_food_search(message: Message, state: FSMContext):
    """Handle food search input"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    query = message.text.strip()

    if not query:
        await message.answer(t("nutrition_valid_food_name", lang))
        return

    searching_msg = await message.answer(t("nutrition_searching", lang))

    foods = await nutrition_bot.search_food(query)

    if not foods:
        await searching_msg.edit_text(
            t("nutrition_no_results", lang, query=query),
            reply_markup=create_back_keyboard("nutrition_add_food")
        )
        await state.clear()
        await state.update_data(lang=lang)
        return

    keyboard = create_food_results_keyboard(foods)
    await searching_msg.edit_text(
        t("nutrition_search_results", lang, query=query),
        parse_mode="HTML",
        reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("nutrition_select_food:"))
async def select_food_callback(callback: CallbackQuery, state: FSMContext):
    """Handle food selection"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    fdc_id = int(callback.data.split(":")[1])

    await callback.message.edit_text(t("nutrition_getting_info", lang))

    food_data = await nutrition_bot.get_food_details(fdc_id)

    if not food_data:
        await callback.message.edit_text(
            t("nutrition_info_error", lang),
            reply_markup=create_back_keyboard("nutrition_add_food")
        )
        await callback.answer()
        return

    await state.update_data(selected_food=food_data)

    await callback.message.edit_text(
        t("nutrition_food_details", lang,
          name=food_data['name'],
          calories=f"{food_data['calories']:.1f}",
          protein=f"{food_data['protein']:.1f}",
          carbs=f"{food_data['carbs']:.1f}",
          fat=f"{food_data['fat']:.1f}"),
        parse_mode="HTML",
        reply_markup=create_back_keyboard("nutrition_add_food")
    )
    await state.set_state(NutritionStates.waiting_for_portion)
    await callback.answer()


@router.message(NutritionStates.waiting_for_portion)
async def handle_portion_input(message: Message, state: FSMContext):
    """Handle portion size input"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    try:
        portion_grams = float(message.text.strip())

        if portion_grams <= 0:
            await message.answer(t("nutrition_positive_portion", lang))
            return

        food_data = data['selected_food']
        meal_type = data['meal_type']

        multiplier = portion_grams / 100
        calories = food_data['calories'] * multiplier
        protein = food_data['protein'] * multiplier
        carbs = food_data['carbs'] * multiplier
        fat = food_data['fat'] * multiplier

        user_id = message.from_user.id
        nutrition_bot.db.log_meal(
            user_id, meal_type, food_data['fdc_id'], food_data['name'],
            portion_grams, calories, protein, carbs, fat
        )

        meal_emoji = {"breakfast": "🥞", "lunch": "🥗", "dinner": "🍽️", "snack": "🍎"}

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t("nutrition_btn_add_more", lang), callback_data="nutrition_add_food")],
            [InlineKeyboardButton(text=t("nutrition_btn_view_summary", lang), callback_data="nutrition_daily_summary")],
            [InlineKeyboardButton(text=t("nutrition_btn_main_menu", lang), callback_data="nutrition_main_menu")]
        ])

        await message.answer(
            t("nutrition_food_logged", lang,
              emoji=meal_emoji.get(meal_type, "🍽️"),
              meal=meal_type.title(),
              name=food_data['name'],
              portion=portion_grams,
              calories=f"{calories:.1f}",
              protein=f"{protein:.1f}",
              carbs=f"{carbs:.1f}",
              fat=f"{fat:.1f}"),
            parse_mode="HTML",
            reply_markup=keyboard
        )
        await state.clear()
        await state.update_data(lang=lang)

    except ValueError:
        await message.answer(t("nutrition_valid_portion", lang))


@router.callback_query(F.data == "nutrition_daily_summary")
async def daily_summary_callback(callback: CallbackQuery, state: FSMContext):
    """Handle daily summary callback"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    user_id = callback.from_user.id
    intake = nutrition_bot.db.get_daily_intake(user_id)
    goals = nutrition_bot.db.get_user_goals(user_id)

    response = t("nutrition_daily_summary_header", lang, date=date.today().strftime('%B %d, %Y'))
    response += "\n\n" + t("nutrition_todays_intake", lang,
                           calories=f"{intake['calories']:.1f}",
                           protein=f"{intake['protein']:.1f}",
                           carbs=f"{intake['carbs']:.1f}",
                           fat=f"{intake['fat']:.1f}")

    if goals:
        cal_percent = (intake['calories'] / goals['calories'] * 100) if goals['calories'] > 0 else 0
        protein_percent = (intake['protein'] / goals['protein'] * 100) if goals['protein'] > 0 else 0
        carbs_percent = (intake['carbs'] / goals['carbs'] * 100) if goals['carbs'] > 0 else 0
        fat_percent = (intake['fat'] / goals['fat'] * 100) if goals['fat'] > 0 else 0

        response += "\n\n" + t("nutrition_progress_vs_goals", lang,
                               cal_percent=f"{cal_percent:.1f}",
                               cal_current=f"{intake['calories']:.1f}",
                               cal_goal=f"{goals['calories']:.1f}",
                               protein_percent=f"{protein_percent:.1f}",
                               protein_current=f"{intake['protein']:.1f}",
                               protein_goal=f"{goals['protein']:.1f}",
                               carbs_percent=f"{carbs_percent:.1f}",
                               carbs_current=f"{intake['carbs']:.1f}",
                               carbs_goal=f"{goals['carbs']:.1f}",
                               fat_percent=f"{fat_percent:.1f}",
                               fat_current=f"{intake['fat']:.1f}",
                               fat_goal=f"{goals['fat']:.1f}")
    else:
        response += "\n\n" + t("nutrition_set_goals_hint", lang)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("nutrition_btn_add_food", lang), callback_data="nutrition_add_food")],
        [InlineKeyboardButton(text=t("nutrition_btn_view_meals", lang), callback_data="nutrition_view_meals")],
        [InlineKeyboardButton(text=t("nutrition_btn_set_goals", lang), callback_data="nutrition_set_goals")],
        [InlineKeyboardButton(text=t("nutrition_btn_main_menu", lang), callback_data="nutrition_main_menu")]
    ])

    await callback.message.edit_text(response, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "nutrition_set_goals")
async def set_goals_callback(callback: CallbackQuery, state: FSMContext):
    """Handle set goals callback"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    user_id = callback.from_user.id
    current_goals = nutrition_bot.db.get_user_goals(user_id)

    if current_goals:
        response = t("nutrition_current_goals", lang,
                     calories=f"{current_goals['calories']:.0f}",
                     protein=f"{current_goals['protein']:.0f}",
                     carbs=f"{current_goals['carbs']:.0f}",
                     fat=f"{current_goals['fat']:.0f}")
    else:
        response = t("nutrition_set_goals_prompt", lang)

    keyboard = create_goal_setting_method_keyboard()
    await callback.message.edit_text(response, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "nutrition_goal_manual")
async def goal_manual_callback(callback: CallbackQuery, state: FSMContext):
    """Start manual goal setting"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    await callback.message.edit_text(
        t("nutrition_enter_calories_goal", lang),
        parse_mode="HTML",
        reply_markup=create_back_keyboard("nutrition_set_goals")
    )
    await state.set_state(NutritionStates.waiting_for_goal_calories)
    await callback.answer()


@router.message(NutritionStates.waiting_for_goal_calories)
async def handle_goal_calories(message: Message, state: FSMContext):
    """Handle calorie goal input"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    try:
        calories = float(message.text.strip())

        if calories <= 0:
            await message.answer(t("nutrition_positive_calories", lang))
            return

        await state.update_data(goal_calories=calories)

        await message.answer(
            t("nutrition_calories_set_enter_protein", lang, calories=f"{calories:.0f}"),
            parse_mode="HTML"
        )
        await state.set_state(NutritionStates.waiting_for_goal_protein)

    except ValueError:
        await message.answer(t("nutrition_valid_calories", lang))


@router.message(NutritionStates.waiting_for_goal_protein)
async def handle_goal_protein(message: Message, state: FSMContext):
    """Handle protein goal input"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    try:
        protein = float(message.text.strip())

        if protein <= 0:
            await message.answer(t("nutrition_positive_protein", lang))
            return

        await state.update_data(goal_protein=protein)

        await message.answer(
            t("nutrition_protein_set_enter_carbs", lang, protein=f"{protein:.0f}"),
            parse_mode="HTML"
        )
        await state.set_state(NutritionStates.waiting_for_goal_carbs)

    except ValueError:
        await message.answer(t("nutrition_valid_protein", lang))


@router.message(NutritionStates.waiting_for_goal_carbs)
async def handle_goal_carbs(message: Message, state: FSMContext):
    """Handle carbs goal input"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    try:
        carbs = float(message.text.strip())

        if carbs <= 0:
            await message.answer(t("nutrition_positive_carbs", lang))
            return

        await state.update_data(goal_carbs=carbs)

        await message.answer(
            t("nutrition_carbs_set_enter_fat", lang, carbs=f"{carbs:.0f}"),
            parse_mode="HTML"
        )
        await state.set_state(NutritionStates.waiting_for_goal_fat)

    except ValueError:
        await message.answer(t("nutrition_valid_carbs", lang))


@router.message(NutritionStates.waiting_for_goal_fat)
async def handle_goal_fat(message: Message, state: FSMContext):
    """Handle fat goal input"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    try:
        fat = float(message.text.strip())

        if fat <= 0:
            await message.answer(t("nutrition_positive_fat", lang))
            return

        user_id = message.from_user.id

        nutrition_bot.db.set_user_goals(
            user_id,
            data['goal_calories'],
            data['goal_protein'],
            data['goal_carbs'],
            fat
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t("nutrition_btn_add_food", lang), callback_data="nutrition_add_food")],
            [InlineKeyboardButton(text=t("nutrition_btn_daily_summary", lang), callback_data="nutrition_daily_summary")],
            [InlineKeyboardButton(text=t("nutrition_btn_main_menu", lang), callback_data="nutrition_main_menu")]
        ])

        await message.answer(
            t("nutrition_goals_set_success", lang,
              calories=f"{data['goal_calories']:.0f}",
              protein=f"{data['goal_protein']:.0f}",
              carbs=f"{data['goal_carbs']:.0f}",
              fat=f"{fat:.0f}"),
            parse_mode="HTML",
            reply_markup=keyboard
        )
        await state.clear()
        await state.update_data(lang=lang)

    except ValueError:
        await message.answer(t("nutrition_valid_fat", lang))


@router.callback_query(F.data == "nutrition_goal_calculator")
async def goal_calculator_start(callback: CallbackQuery, state: FSMContext):
    """Start calculator-based goal setting"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    await callback.message.edit_text(
        t("nutrition_calculator_start", lang),
        parse_mode="HTML",
        reply_markup=create_back_keyboard("nutrition_set_goals")
    )
    await state.set_state(NutritionStates.waiting_for_age)
    await callback.answer()


@router.message(NutritionStates.waiting_for_age)
async def handle_calculator_age(message: Message, state: FSMContext):
    """Handle age input for calculator"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    try:
        age = int(message.text.strip())

        if age < 15 or age > 100:
            await message.answer(t("nutrition_valid_age", lang))
            return

        await state.update_data(calc_age=age)

        keyboard = create_gender_keyboard()
        await message.answer(t("nutrition_age_recorded", lang), parse_mode="HTML", reply_markup=keyboard)

    except ValueError:
        await message.answer(t("nutrition_valid_age_number", lang))


@router.callback_query(F.data.startswith("nutrition_gender:"))
async def handle_calculator_gender(callback: CallbackQuery, state: FSMContext):
    """Handle gender selection for calculator"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    gender = callback.data.split(":")[1]
    await state.update_data(calc_gender=gender)

    gender_emoji = {"male": "👨", "female": "👩"}

    await callback.message.edit_text(
        t("nutrition_gender_selected", lang, emoji=gender_emoji.get(gender), gender=gender.title()),
        parse_mode="HTML",
        reply_markup=create_back_keyboard("nutrition_set_goals")
    )
    await state.set_state(NutritionStates.waiting_for_weight)
    await callback.answer()


@router.message(NutritionStates.waiting_for_weight)
async def handle_calculator_weight(message: Message, state: FSMContext):
    """Handle weight input for calculator"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    try:
        weight = float(message.text.strip())

        if weight < 30 or weight > 300:
            await message.answer(t("nutrition_valid_weight", lang))
            return

        await state.update_data(calc_weight=weight)

        await message.answer(
            t("nutrition_weight_recorded", lang, weight=weight),
            parse_mode="HTML"
        )
        await state.set_state(NutritionStates.waiting_for_height)

    except ValueError:
        await message.answer(t("nutrition_valid_weight_number", lang))


@router.message(NutritionStates.waiting_for_height)
async def handle_calculator_height(message: Message, state: FSMContext):
    """Handle height input for calculator"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    try:
        height = float(message.text.strip())

        if height < 120 or height > 250:
            await message.answer(t("nutrition_valid_height", lang))
            return

        await state.update_data(calc_height=height)

        keyboard = create_activity_level_keyboard()
        await message.answer(
            t("nutrition_height_recorded", lang, height=height),
            parse_mode="HTML",
            reply_markup=keyboard
        )

    except ValueError:
        await message.answer(t("nutrition_valid_height_number", lang))


@router.callback_query(F.data.startswith("nutrition_activity:"))
async def handle_calculator_activity(callback: CallbackQuery, state: FSMContext):
    """Handle activity level selection for calculator"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    activity_multiplier = float(callback.data.split(":")[1])
    await state.update_data(calc_activity=activity_multiplier)

    activity_labels = {
        1.2: "Sedentary",
        1.375: "Lightly Active",
        1.55: "Moderately Active",
        1.725: "Very Active",
        1.9: "Extremely Active"
    }

    keyboard = create_goal_type_keyboard()
    await callback.message.edit_text(
        t("nutrition_activity_recorded", lang, activity=activity_labels.get(activity_multiplier)),
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data.startswith("nutrition_goaltype:"))
async def handle_calculator_goal_type(callback: CallbackQuery, state: FSMContext):
    """Handle goal type selection and calculate nutrition goals"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    goal_type = callback.data.split(":")[1]

    goals = nutrition_bot.calculator.calculate_goals(
        gender=data['calc_gender'],
        age=data['calc_age'],
        weight_kg=data['calc_weight'],
        height_cm=data['calc_height'],
        activity_multiplier=data['calc_activity'],
        goal_type=goal_type
    )

    user_id = callback.from_user.id
    nutrition_bot.db.set_user_goals(
        user_id,
        goals['calories'],
        goals['protein'],
        goals['carbs'],
        goals['fat'],
        bmr=goals['bmr'],
        tdee=goals['tdee'],
        goal_type=goal_type
    )

    goal_labels = {
        "loss": t("nutrition_goal_loss", lang),
        "maintain": t("nutrition_goal_maintain", lang),
        "gain": t("nutrition_goal_gain", lang)
    }

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("nutrition_btn_add_food", lang), callback_data="nutrition_add_food")],
        [InlineKeyboardButton(text=t("nutrition_btn_daily_summary", lang), callback_data="nutrition_daily_summary")],
        [InlineKeyboardButton(text=t("nutrition_btn_main_menu", lang), callback_data="nutrition_main_menu")]
    ])

    await callback.message.edit_text(
        t("nutrition_calculator_result", lang,
          age=data['calc_age'],
          gender=data['calc_gender'].title(),
          weight=data['calc_weight'],
          height=data['calc_height'],
          goal=goal_labels.get(goal_type, goal_type),
          calories=f"{goals['calories']:.0f}",
          protein=f"{goals['protein']:.0f}",
          carbs=f"{goals['carbs']:.0f}",
          fat=f"{goals['fat']:.0f}"),
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await state.clear()
    await state.update_data(lang=lang)
    await callback.answer()


@router.callback_query(F.data == "nutrition_view_meals")
async def view_meals_callback(callback: CallbackQuery, state: FSMContext):
    """Handle view meals callback"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    user_id = callback.from_user.id
    meals = nutrition_bot.db.get_daily_meals(user_id)

    if not meals:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t("nutrition_btn_add_food", lang), callback_data="nutrition_add_food")],
            [InlineKeyboardButton(text=t("nutrition_btn_main_menu", lang), callback_data="nutrition_main_menu")]
        ])

        await callback.message.edit_text(
            t("nutrition_no_meals_today", lang),
            parse_mode="HTML",
            reply_markup=keyboard
        )
    else:
        response = t("nutrition_todays_meals_header", lang, date=date.today().strftime('%B %d, %Y')) + "\n\n"

        meal_groups = {"breakfast": [], "lunch": [], "dinner": [], "snack": []}

        for meal in meals:
            meal_type = meal['meal_type']
            if meal_type in meal_groups:
                meal_groups[meal_type].append(meal)

        meal_emojis = {"breakfast": "🥞", "lunch": "🥗", "dinner": "🍽️", "snack": "🍎"}

        for meal_type, meal_list in meal_groups.items():
            if meal_list:
                response += f"\n{meal_emojis[meal_type]} **{meal_type.title()}:**\n"

                for meal in meal_list:
                    response += f"• {meal['food_name']} ({meal['portion_grams']:.0f}g)\n"
                    response += f"  {meal['calories']:.0f} kcal | P: {meal['protein']:.1f}g | C: {meal['carbs']:.1f}g | F: {meal['fat']:.1f}g\n"

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t("nutrition_btn_add_food", lang), callback_data="nutrition_add_food")],
            [InlineKeyboardButton(text=t("nutrition_btn_daily_summary", lang), callback_data="nutrition_daily_summary")],
            [InlineKeyboardButton(text=t("nutrition_btn_main_menu", lang), callback_data="nutrition_main_menu")]
        ])

        await callback.message.edit_text(response, parse_mode="HTML", reply_markup=keyboard)

    await callback.answer()