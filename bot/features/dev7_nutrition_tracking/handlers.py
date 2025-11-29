"""
Nutrition tracking handlers for dev7 feature.
Updated to use unified database.
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from datetime import date

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
    user_id = message.from_user.id
    username = message.from_user.username
    
    # Ensure user exists in unified database
    nutrition_bot.db.ensure_user_exists(user_id, username)
    
    welcome_text = """
🎯 **Welcome to Advanced Nutrition Tracker!** 🎯

Track your daily nutrition with comprehensive features:

🍔 **Add Food** - Search and log meals
📊 **Daily Summary** - See your progress
🎯 **Set Goals** - Define nutrition targets
📋 **View Meals** - Review logged foods

Choose an option below to get started!
    """
    
    keyboard = create_main_menu()
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=keyboard)
    await state.clear()


@router.callback_query(F.data == "nutrition_main_menu")
async def main_menu_callback(callback: CallbackQuery, state: FSMContext):
    """Handle main menu callback"""
    await state.clear()
    
    text = """
🎯 **Nutrition Tracker - Main Menu**

Choose what you'd like to do:
    """
    
    keyboard = create_main_menu()
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "nutrition_add_food")
async def add_food_callback(callback: CallbackQuery):
    """Handle add food callback"""
    text = """
🍽️ **Add Food to Meal**

First, select which meal you're logging:
    """
    
    keyboard = create_meal_type_keyboard()
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("nutrition_meal:"))
async def meal_type_callback(callback: CallbackQuery, state: FSMContext):
    """Handle meal type selection"""
    meal_type = callback.data.split(":")[1]
    
    await state.update_data(meal_type=meal_type)
    
    meal_emoji = {"breakfast": "🥞", "lunch": "🥗", "dinner": "🍽️", "snack": "🍎"}
    
    text = f"""
{meal_emoji.get(meal_type, "🍽️")} **Adding food to {meal_type.title()}**

Please enter the name of the food you want to search for:

*Example: Chicken breast, Banana, Rice, etc.*
    """
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=create_back_keyboard("nutrition_add_food"))
    await state.set_state(NutritionStates.waiting_for_search)
    await callback.answer()


@router.message(NutritionStates.waiting_for_search)
async def handle_food_search(message: Message, state: FSMContext):
    """Handle food search input"""
    query = message.text.strip()
    
    if not query:
        await message.answer("Please provide a valid food name to search for.")
        return
    
    searching_msg = await message.answer("🔍 Searching for foods...")
    
    foods = await nutrition_bot.search_food(query)
    
    if not foods:
        await searching_msg.edit_text(
            f"❌ No results found for '{query}'. Please try a different search term.",
            reply_markup=create_back_keyboard("nutrition_add_food")
        )
        await state.clear()
        return
    
    response = f"🔍 **Search results for '{query}':**\n\nSelect a food to add to your meal:"
    keyboard = create_food_results_keyboard(foods)
    
    await searching_msg.edit_text(response, parse_mode="Markdown", reply_markup=keyboard)


@router.callback_query(F.data.startswith("nutrition_select_food:"))
async def select_food_callback(callback: CallbackQuery, state: FSMContext):
    """Handle food selection"""
    fdc_id = int(callback.data.split(":")[1])
    
    await callback.message.edit_text("⏳ Getting food information...")
    
    food_data = await nutrition_bot.get_food_details(fdc_id)
    
    if not food_data:
        await callback.message.edit_text(
            "❌ Sorry, I couldn't get information for this food.",
            reply_markup=create_back_keyboard("nutrition_add_food")
        )
        await callback.answer()
        return
    
    # Store food data in state
    await state.update_data(selected_food=food_data)
    
    # Show nutrition info and ask for portion
    response = f"""
📊 **{food_data['name']}**

**Nutrition per 100g:**
🔥 Calories: {food_data['calories']:.1f} kcal
🥩 Protein: {food_data['protein']:.1f}g
🍞 Carbs: {food_data['carbs']:.1f}g
🥑 Fat: {food_data['fat']:.1f}g

**Enter portion size in grams:**
*Example: 150 (for 150 grams)*
    """
    
    await callback.message.edit_text(response, parse_mode="Markdown", reply_markup=create_back_keyboard("nutrition_add_food"))
    await state.set_state(NutritionStates.waiting_for_portion)
    await callback.answer()


@router.message(NutritionStates.waiting_for_portion)
async def handle_portion_input(message: Message, state: FSMContext):
    """Handle portion size input"""
    try:
        portion_grams = float(message.text.strip())
        
        if portion_grams <= 0:
            await message.answer("Please enter a positive number for the portion size.")
            return
        
        data = await state.get_data()
        food_data = data['selected_food']
        meal_type = data['meal_type']
        
        # Calculate nutrition for the specified portion
        multiplier = portion_grams / 100
        
        calories = food_data['calories'] * multiplier
        protein = food_data['protein'] * multiplier
        carbs = food_data['carbs'] * multiplier
        fat = food_data['fat'] * multiplier
        
        # Log the meal using unified database
        user_id = message.from_user.id
        nutrition_bot.db.log_meal(
            user_id, meal_type, food_data['fdc_id'], food_data['name'],
            portion_grams, calories, protein, carbs, fat
        )
        
        # Show confirmation
        meal_emoji = {"breakfast": "🥞", "lunch": "🥗", "dinner": "🍽️", "snack": "🍎"}
        
        response = f"""
✅ **Food logged successfully!**

{meal_emoji.get(meal_type, "🍽️")} **{meal_type.title()}**
🍽️ {food_data['name']} ({portion_grams}g)

**Nutrition added:**
🔥 Calories: {calories:.1f} kcal
🥩 Protein: {protein:.1f}g
🍞 Carbs: {carbs:.1f}g
🥑 Fat: {fat:.1f}g
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Add More Food", callback_data="nutrition_add_food")],
            [InlineKeyboardButton(text="📊 View Daily Summary", callback_data="nutrition_daily_summary")],
            [InlineKeyboardButton(text="🏠 Main Menu", callback_data="nutrition_main_menu")]
        ])
        
        await message.answer(response, parse_mode="Markdown", reply_markup=keyboard)
        await state.clear()
        
    except ValueError:
        await message.answer("Please enter a valid number for the portion size (e.g., 150).")


@router.callback_query(F.data == "nutrition_daily_summary")
async def daily_summary_callback(callback: CallbackQuery):
    """Handle daily summary callback"""
    user_id = callback.from_user.id
    
    # Get daily intake from unified database
    intake = nutrition_bot.db.get_daily_intake(user_id)
    
    # Get user goals from unified database
    goals = nutrition_bot.db.get_user_goals(user_id)
    
    response = f"""
📊 **Daily Summary - {date.today().strftime('%B %d, %Y')}**

**Today's Intake:**
🔥 Calories: {intake['calories']:.1f} kcal
🥩 Protein: {intake['protein']:.1f}g
🍞 Carbs: {intake['carbs']:.1f}g
🥑 Fat: {intake['fat']:.1f}g
    """
    
    if goals:
        cal_percent = (intake['calories'] / goals['calories'] * 100) if goals['calories'] > 0 else 0
        protein_percent = (intake['protein'] / goals['protein'] * 100) if goals['protein'] > 0 else 0
        carbs_percent = (intake['carbs'] / goals['carbs'] * 100) if goals['carbs'] > 0 else 0
        fat_percent = (intake['fat'] / goals['fat'] * 100) if goals['fat'] > 0 else 0
        
        response += f"""

**Progress vs Goals:**
🎯 Calories: {cal_percent:.1f}% ({intake['calories']:.1f}/{goals['calories']:.1f})
🎯 Protein: {protein_percent:.1f}% ({intake['protein']:.1f}/{goals['protein']:.1f}g)
🎯 Carbs: {carbs_percent:.1f}% ({intake['carbs']:.1f}/{goals['carbs']:.1f}g)
🎯 Fat: {fat_percent:.1f}% ({intake['fat']:.1f}/{goals['fat']:.1f}g)
        """
    else:
        response += "\n\n💡 *Set your daily goals to track progress!*"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Add Food", callback_data="nutrition_add_food")],
        [InlineKeyboardButton(text="📋 View Meals", callback_data="nutrition_view_meals")],
        [InlineKeyboardButton(text="🎯 Set Goals", callback_data="nutrition_set_goals")],
        [InlineKeyboardButton(text="🏠 Main Menu", callback_data="nutrition_main_menu")]
    ])
    
    await callback.message.edit_text(response, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "nutrition_set_goals")
async def set_goals_callback(callback: CallbackQuery, state: FSMContext):
    """Handle set goals callback - show method selection"""
    user_id = callback.from_user.id
    current_goals = nutrition_bot.db.get_user_goals(user_id)
    
    if current_goals:
        response = f"""
🎯 **Current Daily Goals:**

🔥 Calories: {current_goals['calories']:.0f} kcal
🥩 Protein: {current_goals['protein']:.0f}g
🍞 Carbs: {current_goals['carbs']:.0f}g
🥑 Fat: {current_goals['fat']:.0f}g

**Choose how you'd like to update your goals:**
        """
    else:
        response = """
🎯 **Set Your Daily Nutrition Goals**

Choose your preferred method to set your goals:

✏️ **Enter Manually** - Input your own targets
🧮 **Calculator** - Calculate based on your body metrics and goals
        """
    
    keyboard = create_goal_setting_method_keyboard()
    await callback.message.edit_text(response, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()


# MANUAL GOAL SETTING FLOW
@router.callback_query(F.data == "nutrition_goal_manual")
async def goal_manual_callback(callback: CallbackQuery, state: FSMContext):
    """Start manual goal setting"""
    response = """
✏️ **Manual Goal Setting**

**Enter your daily calorie goal:**
*Example: 2000*
    """
    
    await callback.message.edit_text(response, parse_mode="Markdown", reply_markup=create_back_keyboard("nutrition_set_goals"))
    await state.set_state(NutritionStates.waiting_for_goal_calories)
    await callback.answer()


@router.message(NutritionStates.waiting_for_goal_calories)
async def handle_goal_calories(message: Message, state: FSMContext):
    """Handle calorie goal input"""
    try:
        calories = float(message.text.strip())
        
        if calories <= 0:
            await message.answer("Please enter a positive number for calories.")
            return
        
        await state.update_data(goal_calories=calories)
        
        await message.answer(
            f"✅ Calorie goal set to {calories:.0f} kcal\n\n"
            "**Now enter your daily protein goal (in grams):**\n"
            "*Example: 150*",
            parse_mode="Markdown"
        )
        await state.set_state(NutritionStates.waiting_for_goal_protein)
        
    except ValueError:
        await message.answer("Please enter a valid number for calories.")


@router.message(NutritionStates.waiting_for_goal_protein)
async def handle_goal_protein(message: Message, state: FSMContext):
    """Handle protein goal input"""
    try:
        protein = float(message.text.strip())
        
        if protein <= 0:
            await message.answer("Please enter a positive number for protein.")
            return
        
        await state.update_data(goal_protein=protein)
        
        await message.answer(
            f"✅ Protein goal set to {protein:.0f}g\n\n"
            "**Now enter your daily carbohydrate goal (in grams):**\n"
            "*Example: 250*",
            parse_mode="Markdown"
        )
        await state.set_state(NutritionStates.waiting_for_goal_carbs)
        
    except ValueError:
        await message.answer("Please enter a valid number for protein.")


@router.message(NutritionStates.waiting_for_goal_carbs)
async def handle_goal_carbs(message: Message, state: FSMContext):
    """Handle carbs goal input"""
    try:
        carbs = float(message.text.strip())
        
        if carbs <= 0:
            await message.answer("Please enter a positive number for carbohydrates.")
            return
        
        await state.update_data(goal_carbs=carbs)
        
        await message.answer(
            f"✅ Carbohydrate goal set to {carbs:.0f}g\n\n"
            "**Finally, enter your daily fat goal (in grams):**\n"
            "*Example: 70*",
            parse_mode="Markdown"
        )
        await state.set_state(NutritionStates.waiting_for_goal_fat)
        
    except ValueError:
        await message.answer("Please enter a valid number for carbohydrates.")


@router.message(NutritionStates.waiting_for_goal_fat)
async def handle_goal_fat(message: Message, state: FSMContext):
    """Handle fat goal input"""
    try:
        fat = float(message.text.strip())
        
        if fat <= 0:
            await message.answer("Please enter a positive number for fat.")
            return
        
        data = await state.get_data()
        user_id = message.from_user.id
        
        # Save all goals to unified database
        nutrition_bot.db.set_user_goals(
            user_id, 
            data['goal_calories'], 
            data['goal_protein'], 
            data['goal_carbs'], 
            fat
        )
        
        response = f"""
🎯 **Goals Set Successfully!**

Your daily nutrition targets:
🔥 Calories: {data['goal_calories']:.0f} kcal
🥩 Protein: {data['goal_protein']:.0f}g
🍞 Carbs: {data['goal_carbs']:.0f}g
🥑 Fat: {fat:.0f}g

You can now track your progress against these goals!
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Add Food", callback_data="nutrition_add_food")],
            [InlineKeyboardButton(text="📊 Daily Summary", callback_data="nutrition_daily_summary")],
            [InlineKeyboardButton(text="🏠 Main Menu", callback_data="nutrition_main_menu")]
        ])
        
        await message.answer(response, parse_mode="Markdown", reply_markup=keyboard)
        await state.clear()
        
    except ValueError:
        await message.answer("Please enter a valid number for fat.")


# CALCULATOR GOAL SETTING FLOW
@router.callback_query(F.data == "nutrition_goal_calculator")
async def goal_calculator_start(callback: CallbackQuery, state: FSMContext):
    """Start calculator-based goal setting"""
    response = """
🧮 **Nutrition Goals Calculator**

Let's calculate your personalized nutrition goals based on your body metrics and activity level!

**First, enter your age:**
*Example: 25*
    """
    
    await callback.message.edit_text(response, parse_mode="Markdown", reply_markup=create_back_keyboard("nutrition_set_goals"))
    await state.set_state(NutritionStates.waiting_for_age)
    await callback.answer()


@router.message(NutritionStates.waiting_for_age)
async def handle_calculator_age(message: Message, state: FSMContext):
    """Handle age input for calculator"""
    try:
        age = int(message.text.strip())
        
        if age < 15 or age > 100:
            await message.answer("Please enter a valid age between 15 and 100.")
            return
        
        await state.update_data(calc_age=age)
        
        response = """
✅ Age recorded!

**Now select your gender:**
        """
        
        keyboard = create_gender_keyboard()
        await message.answer(response, parse_mode="Markdown", reply_markup=keyboard)
        
    except ValueError:
        await message.answer("Please enter a valid number for age.")


@router.callback_query(F.data.startswith("nutrition_gender:"))
async def handle_calculator_gender(callback: CallbackQuery, state: FSMContext):
    """Handle gender selection for calculator"""
    gender = callback.data.split(":")[1]
    await state.update_data(calc_gender=gender)
    
    gender_emoji = {"male": "👨", "female": "👩"}
    
    response = f"""
✅ Gender: {gender_emoji.get(gender)} {gender.title()}

**Enter your weight in kilograms:**
*Example: 75*
    """
    
    await callback.message.edit_text(response, parse_mode="Markdown", reply_markup=create_back_keyboard("nutrition_set_goals"))
    await state.set_state(NutritionStates.waiting_for_weight)
    await callback.answer()


@router.message(NutritionStates.waiting_for_weight)
async def handle_calculator_weight(message: Message, state: FSMContext):
    """Handle weight input for calculator"""
    try:
        weight = float(message.text.strip())
        
        if weight < 30 or weight > 300:
            await message.answer("Please enter a valid weight between 30 and 300 kg.")
            return
        
        await state.update_data(calc_weight=weight)
        
        await message.answer(
            f"✅ Weight: {weight}kg\n\n"
            "**Enter your height in centimeters:**\n"
            "*Example: 175*",
            parse_mode="Markdown"
        )
        await state.set_state(NutritionStates.waiting_for_height)
        
    except ValueError:
        await message.answer("Please enter a valid number for weight.")


@router.message(NutritionStates.waiting_for_height)
async def handle_calculator_height(message: Message, state: FSMContext):
    """Handle height input for calculator"""
    try:
        height = float(message.text.strip())
        
        if height < 120 or height > 250:
            await message.answer("Please enter a valid height between 120 and 250 cm.")
            return
        
        await state.update_data(calc_height=height)
        
        response = f"""
✅ Height: {height}cm

**Select your activity level:**
        """
        
        keyboard = create_activity_level_keyboard()
        await message.answer(response, parse_mode="Markdown", reply_markup=keyboard)
        
    except ValueError:
        await message.answer("Please enter a valid number for height.")


@router.callback_query(F.data.startswith("nutrition_activity:"))
async def handle_calculator_activity(callback: CallbackQuery, state: FSMContext):
    """Handle activity level selection for calculator"""
    activity_multiplier = float(callback.data.split(":")[1])
    await state.update_data(calc_activity=activity_multiplier)
    
    activity_labels = {
        1.2: "Sedentary",
        1.375: "Lightly Active",
        1.55: "Moderately Active",
        1.725: "Very Active",
        1.9: "Extremely Active"
    }
    
    response = f"""
✅ Activity Level: {activity_labels.get(activity_multiplier)}

**Finally, select your goal:**
        """
    
    keyboard = create_goal_type_keyboard()
    await callback.message.edit_text(response, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("nutrition_goaltype:"))
async def handle_calculator_goal_type(callback: CallbackQuery, state: FSMContext):
    """Handle goal type selection and calculate nutrition goals"""
    goal_type = callback.data.split(":")[1]
    
    data = await state.get_data()
    
    # Calculate nutrition goals
    goals = nutrition_bot.calculator.calculate_goals(
        gender=data['calc_gender'],
        age=data['calc_age'],
        weight_kg=data['calc_weight'],
        height_cm=data['calc_height'],
        activity_multiplier=data['calc_activity'],
        goal_type=goal_type
    )
    
    # Save to unified database
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
        "loss": "Weight Loss 📉",
        "maintain": "Maintain Weight ⚖️",
        "gain": "Weight Gain 📈"
    }
    
    response = f"""
🎯 **Goals Calculated Successfully!**

**Your Profile:**
👤 Age: {data['calc_age']} | Gender: {data['calc_gender'].title()}
⚖️ Weight: {data['calc_weight']}kg | Height: {data['calc_height']}cm
🎯 Goal: {goal_labels.get(goal_type)}

**Your Daily Nutrition Goals:**
🔥 Calories: {goals['calories']:.0f} kcal
🥩 Protein: {goals['protein']:.0f}g
🍞 Carbs: {goals['carbs']:.0f}g
🥑 Fat: {goals['fat']:.0f}g

Start tracking your meals to reach your goals!
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Add Food", callback_data="nutrition_add_food")],
        [InlineKeyboardButton(text="📊 Daily Summary", callback_data="nutrition_daily_summary")],
        [InlineKeyboardButton(text="🏠 Main Menu", callback_data="nutrition_main_menu")]
    ])
    
    await callback.message.edit_text(response, parse_mode="Markdown", reply_markup=keyboard)
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "nutrition_view_meals")
async def view_meals_callback(callback: CallbackQuery):
    """Handle view meals callback"""
    user_id = callback.from_user.id
    meals = nutrition_bot.db.get_daily_meals(user_id)
    
    if not meals:
        response = """
📋 **Today's Meals**

No meals logged today yet!

Start by adding some food to track your nutrition.
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Add Food", callback_data="nutrition_add_food")],
            [InlineKeyboardButton(text="🏠 Main Menu", callback_data="nutrition_main_menu")]
        ])
    else:
        response = f"📋 **Today's Meals - {date.today().strftime('%B %d, %Y')}**\n\n"
        
        # Group meals by type
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
            [InlineKeyboardButton(text="➕ Add Food", callback_data="nutrition_add_food")],
            [InlineKeyboardButton(text="📊 Daily Summary", callback_data="nutrition_daily_summary")],
            [InlineKeyboardButton(text="🏠 Main Menu", callback_data="nutrition_main_menu")]
        ])
    
    await callback.message.edit_text(response, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()