"""
All translations for the bot
"""

translations = {
    # MAIN BOT MESSAGES
    "main_welcome": {
        "en": """👋 <b>Hey, {name}!</b>

I'm your personal fitness assistant! I'll help you with:

🏋️ <b>Workout Tracking</b>
   • Log exercises and sets
   • Create custom workout routines
   • View training history

📚 <b>Exercise Library</b>
   • 270+ exercises with detailed instructions
   • Filter by muscle group, equipment, difficulty
   • Professional technique tips
   • Use /exercise to browse

📊 <b>Progress Monitoring</b>
   • Analyze statistics
   • Track personal records
   • Visualize results
   • Use /statistics to explore

🎯 <b>Custom Routines</b>
   • Browse preset workout programs
   • Create your own training plans
   • Track routine usage
   • Use /routines and /custom_routines

⏱️ <b>Rest Timers</b>
   • Set custom timers for rest periods
   • Save timer presets for quick access
   • Use /timer to get started

🍎 <b>Nutrition Tracking</b>
   • Track calories and macronutrients
   • Search 350,000+ foods via USDA database
   • Set personalized nutrition goals
   • View daily nutrition summary
   • Use /nutrition to start

📅 <b>Training Notifications</b>
   • Schedule workout reminders
   • Custom notification times
   • Weekly training schedule
   • Use /notification to set up

Use /help to see all available commands!""",
        "ru": """👋 <b>Привет, {name}!</b>

Я твой личный фитнес-помощник! Я помогу тебе с:

🏋️ <b>Отслеживанием тренировок</b>
   • Записывать упражнения и подходы
   • Создавать собственные программы тренировок
   • Просматривать историю тренировок

📚 <b>Библиотекой упражнений</b>
   • 270+ упражнений с подробными инструкциями
   • Фильтр по группам мышц, оборудованию, сложности
   • Профессиональные советы по технике
   • Используй /exercise для просмотра

📊 <b>Мониторингом прогресса</b>
   • Анализировать статистику
   • Отслеживать личные рекорды
   • Визуализировать результаты
   • Используй /statistics для исследования

🎯 <b>Собственными программами</b>
   • Просматривать готовые программы тренировок
   • Создавать свои планы тренировок
   • Отслеживать использование программ
   • Используй /routines и /custom_routines

⏱️ <b>Таймерами отдыха</b>
   • Устанавливать таймеры для периодов отдыха
   • Сохранять пресеты таймеров для быстрого доступа
   • Используй /timer для начала

🍎 <b>Отслеживанием питания</b>
   • Отслеживать калории и макронутриенты
   • Искать среди 350,000+ продуктов в базе USDA
   • Устанавливать персональные цели по питанию
   • Просматривать дневную сводку питания
   • Используй /nutrition для начала

📅 <b>Уведомлениями о тренировках</b>
   • Планировать напоминания о тренировках
   • Настраиваемое время уведомлений
   • Недельный график тренировок
   • Используй /notification для настройки

Используй /help для просмотра всех доступных команд!"""
    },

    "choose_language": {
        "en": "🌍 <b>Choose your language:</b>",
        "ru": "🌍 <b>Выберите ваш язык:</b>"
    },

    "main_help": {
        "en": """📋 <b>Available Commands:</b>

<b>🏋️ Workouts:</b>
/log (e.g., BenchPress 3x10x50) - Log an exercise 
/today - Show today's workouts
/check_training (e.g., 03.09.2025) - Check workouts by date
/list_trainings - List training days by year
/profile - View your profile

<b>🎯 Workout Routines:</b>
/routines - Browse preset workout programs by level
/custom_routines - Create and manage your own routines

<b>📊 Statistics & Progress:</b>
/statistics - View comprehensive statistics

<b>📚 Exercise Library:</b>
/exercise - Browse exercise database 
/exercise_stats - View library statistics

<b>⏱️ Rest Timers:</b>
/timer - Set and manage rest timers

<b>🍎 Nutrition Tracking:</b>
/nutrition - Track meals and macros

<b>📅 Training Notifications:</b>
/notification - Manage training reminders

<b>🌍 Language:</b>
/language - Change bot language""",
        "ru": """📋 <b>Доступные команды:</b>

<b>🏋️ Тренировки:</b>
/log (например, BenchPress 3x10x50) - Записать упражнение
/today - Показать сегодняшние тренировки
/check_training (например, 03.09.2025) - Проверить тренировки по дате
/list_trainings - Список дней тренировок по году
/profile - Просмотр вашего профиля

<b>🎯 Программы тренировок:</b>
/routines - Просмотр готовых программ по уровню
/custom_routines - Создание и управление своими программами

<b>📊 Статистика и прогресс:</b>
/statistics - Просмотр подробной статистики

<b>📚 Библиотека упражнений:</b>
/exercise - Просмотр базы упражнений
/exercise_stats - Просмотр статистики библиотеки

<b>⏱️ Таймеры отдыха:</b>
/timer - Установка и управление таймерами

<b>🍎 Отслеживание питания:</b>
/nutrition - Отслеживание приёмов пищи и макросов

<b>📅 Уведомления о тренировках:</b>
/notification - Управление напоминаниями

<b>🌍 Язык:</b>
/language - Изменить язык бота"""
    },

    "echo_message": {
        "en": "💬 You wrote: <i>{text}</i>\n\nUse /help to see available commands.",
        "ru": "💬 Вы написали: <i>{text}</i>\n\nИспользуйте /help для просмотра доступных команд."
    },

# Добавь эти переводы в localization/translations.py

# ========================================
# EXERCISE LIBRARY (dev2)
# ========================================

# Buttons
# Добавь эти переводы в localization/translations.py
# ИСПРАВЛЕННАЯ ВЕРСИЯ С HTML ВМЕСТО MARKDOWN!

# ========================================
# EXERCISE LIBRARY (dev2)
# ========================================

# Buttons
"exercise_back_button": {
    "en": "⬅️ Back",
    "ru": "⬅️ Назад"
},
"exercise_main_menu_button": {
    "en": "🏠 Main Menu",
    "ru": "🏠 Главное меню"
},

# Database stats
"exercise_db_stats": {
    "en": "📊 <b>Exercise Database Statistics</b>\n\n📚 Total exercises: {total}\n💪 Muscle groups: {groups}\n🏋️ Equipment types: {equipment}\n📈 Difficulty levels: {levels}",
    "ru": "📊 <b>Статистика базы упражнений</b>\n\n📚 Всего упражнений: {total}\n💪 Групп мышц: {groups}\n🏋️ Типов оборудования: {equipment}\n📈 Уровней сложности: {levels}"
},

"exercise_db_empty": {
    "en": "❌ Exercise database is empty. Please contact administrator.",
    "ru": "❌ База упражнений пуста. Обратитесь к администратору."
},

# Selection steps
"exercise_step1": {
    "en": "📚 <b>Exercise Library</b>\n\n<b>Step 1/4:</b> Select muscle group",
    "ru": "📚 <b>Библиотека упражнений</b>\n\n<b>Шаг 1/4:</b> Выберите группу мышц"
},

"exercise_step2": {
    "en": "📚 <b>Exercise Library</b>\n\n<b>Step 2/4:</b> Select specific muscle\n\n🎯 Selected: <b>{muscle_group}</b>",
    "ru": "📚 <b>Библиотека упражнений</b>\n\n<b>Шаг 2/4:</b> Выберите конкретную мышцу\n\n🎯 Выбрано: <b>{muscle_group}</b>"
},

"exercise_step3": {
    "en": "📚 <b>Exercise Library</b>\n\n<b>Step 3/4:</b> Select equipment type\n\n🎯 Muscle group: <b>{muscle_group}</b>\n💪 Muscle: <b>{muscle}</b>",
    "ru": "📚 <b>Библиотека упражнений</b>\n\n<b>Шаг 3/4:</b> Выберите тип оборудования\n\n🎯 Группа мышц: <b>{muscle_group}</b>\n💪 Мышца: <b>{muscle}</b>"
},

"exercise_step4": {
    "en": "📚 <b>Exercise Library</b>\n\n<b>Step 4/4:</b> Select difficulty level\n\n🎯 Muscle group: <b>{muscle_group}</b>\n💪 Muscle: <b>{muscle}</b>\n🏋️ Equipment: <b>{equipment}</b>",
    "ru": "📚 <b>Библиотека упражнений</b>\n\n<b>Шаг 4/4:</b> Выберите уровень сложности\n\n🎯 Группа мышц: <b>{muscle_group}</b>\n💪 Мышца: <b>{muscle}</b>\n🏋️ Оборудование: <b>{equipment}</b>"
},

# Results
"exercise_no_results": {
    "en": "❌ <b>No exercises found</b>\n\nTry different filters.",
    "ru": "❌ <b>Упражнения не найдены</b>\n\nПопробуйте другие фильтры."
},

"exercise_select_final": {
    "en": "✅ <b>Found {count} exercise(s)</b>\n\n🎯 Muscle group: <b>{muscle_group}</b>\n💪 Muscle: <b>{muscle}</b>\n🏋️ Equipment: <b>{equipment}</b>\n📈 Difficulty: <b>{difficulty}</b>\n\nSelect an exercise to view details:",
    "ru": "✅ <b>Найдено упражнений: {count}</b>\n\n🎯 Группа мышц: <b>{muscle_group}</b>\n💪 Мышца: <b>{muscle}</b>\n🏋️ Оборудование: <b>{equipment}</b>\n📈 Сложность: <b>{difficulty}</b>\n\nВыберите упражнение для просмотра:"
},

"exercise_not_found": {
    "en": "❌ Exercise not found",
    "ru": "❌ Упражнение не найдено"
},

# Exercise details
"exercise_selected": {
    "en": "📖 <b>Exercise Details</b>",
    "ru": "📖 <b>Детали упражнения</b>"
},

"exercise_description": {
    "en": "📝 <b>Description:</b>",
    "ru": "📝 <b>Описание:</b>"
},

"exercise_technique": {
    "en": "🎯 <b>Technique:</b>",
    "ru": "🎯 <b>Техника:</b>"
},

"exercise_tips": {
    "en": "💡 <b>Tips:</b>",
    "ru": "💡 <b>Советы:</b>"
},

"exercise_default_tips": {
    "en": "💡 <b>Tips:</b> Maintain proper form and control throughout the movement.",
    "ru": "💡 <b>Советы:</b> Соблюдайте правильную технику и контроль на протяжении всего движения."
},

# Navigation
"exercise_return_main": {
    "en": "✅ Returned to main menu.\n\nUse /exercise to browse exercises again.",
    "ru": "✅ Возврат в главное меню.\n\nИспользуйте /exercise для просмотра упражнений снова."
},

# ========================================
# NUTRITION TRACKING (dev7) - ПОЛНЫЕ ПЕРЕВОДЫ
# ========================================
# Скопируй ВСЁ это в localization/translations.py
# ВНУТРИ словаря translations = { ... }

# === WELCOME & MAIN MENU ===
"nutrition_welcome": {
    "en": "🎯 <b>Welcome to Advanced Nutrition Tracker!</b>\n\nTrack your daily nutrition with comprehensive features:\n\n🍔 <b>Add Food</b> - Search and log meals\n📊 <b>Daily Summary</b> - See your progress\n🎯 <b>Set Goals</b> - Define nutrition targets\n📋 <b>View Meals</b> - Review logged foods\n\nChoose an option below to get started!",
    "ru": "🎯 <b>Добро пожаловать в продвинутый трекер питания!</b>\n\nОтслеживайте своё питание с полным функционалом:\n\n🍔 <b>Добавить еду</b> - Найти и записать приёмы пищи\n📊 <b>Дневная сводка</b> - Посмотреть прогресс\n🎯 <b>Установить цели</b> - Определить цели по питанию\n📋 <b>Просмотр приёмов пищи</b> - Просмотреть записанную еду\n\nВыберите опцию ниже, чтобы начать!"
},

"nutrition_main_menu_text": {
    "en": "🎯 <b>Nutrition Tracker - Main Menu</b>\n\nChoose what you'd like to do:",
    "ru": "🎯 <b>Трекер питания - Главное меню</b>\n\nВыберите, что хотите сделать:"
},

# === ADD FOOD FLOW ===
"nutrition_add_food_text": {
    "en": "🍽️ <b>Add Food to Meal</b>\n\nFirst, select which meal you're logging:",
    "ru": "🍽️ <b>Добавить еду к приёму пищи</b>\n\nСначала выберите, какой приём пищи записываете:"
},

"nutrition_enter_food_name": {
    "en": "{emoji} <b>Adding food to {meal}</b>\n\nPlease enter the name of the food you want to search for:\n\n<i>Example: Chicken breast, Banana, Rice, etc.</i>",
    "ru": "{emoji} <b>Добавление еды к {meal}</b>\n\nВведите название еды для поиска:\n\n<i>Например: Куриная грудка, Банан, Рис и т.д.</i>"
},

"nutrition_valid_food_name": {
    "en": "Please provide a valid food name to search for.",
    "ru": "Пожалуйста, укажите корректное название еды для поиска."
},

"nutrition_searching": {
    "en": "🔍 Searching for foods...",
    "ru": "🔍 Поиск еды..."
},

"nutrition_no_results": {
    "en": "❌ No results found for '{query}'. Please try a different search term.",
    "ru": "❌ Результаты для '{query}' не найдены. Попробуйте другой запрос."
},

"nutrition_search_results": {
    "en": "🔍 <b>Search results for '{query}':</b>\n\nSelect a food to add to your meal:",
    "ru": "🔍 <b>Результаты поиска для '{query}':</b>\n\nВыберите еду для добавления к приёму пищи:"
},

"nutrition_getting_info": {
    "en": "⏳ Getting food information...",
    "ru": "⏳ Получение информации о еде..."
},

"nutrition_info_error": {
    "en": "❌ Sorry, I couldn't get information for this food.",
    "ru": "❌ Извините, не удалось получить информацию об этой еде."
},

"nutrition_food_details": {
    "en": "📊 <b>{name}</b>\n\n<b>Nutrition per 100g:</b>\n🔥 Calories: {calories} kcal\n🥩 Protein: {protein}g\n🍞 Carbs: {carbs}g\n🥑 Fat: {fat}g\n\n<b>Enter portion size in grams:</b>\n<i>Example: 150 (for 150 grams)</i>",
    "ru": "📊 <b>{name}</b>\n\n<b>Пищевая ценность на 100г:</b>\n🔥 Калории: {calories} ккал\n🥩 Белки: {protein}г\n🍞 Углеводы: {carbs}г\n🥑 Жиры: {fat}г\n\n<b>Введите размер порции в граммах:</b>\n<i>Например: 150 (для 150 грамм)</i>"
},

"nutrition_positive_portion": {
    "en": "Please enter a positive number for the portion size.",
    "ru": "Пожалуйста, введите положительное число для размера порции."
},

"nutrition_valid_portion": {
    "en": "Please enter a valid number for the portion size (e.g., 150).",
    "ru": "Пожалуйста, введите корректное число для размера порции (например, 150)."
},

"nutrition_food_logged": {
    "en": "✅ <b>Food logged successfully!</b>\n\n{emoji} <b>{meal}</b>\n🍽️ {name} ({portion}g)\n\n<b>Nutrition added:</b>\n🔥 Calories: {calories} kcal\n🥩 Protein: {protein}g\n🍞 Carbs: {carbs}g\n🥑 Fat: {fat}g",
    "ru": "✅ <b>Еда успешно записана!</b>\n\n{emoji} <b>{meal}</b>\n🍽️ {name} ({portion}г)\n\n<b>Добавлена пищевая ценность:</b>\n🔥 Калории: {calories} ккал\n🥩 Белки: {protein}г\n🍞 Углеводы: {carbs}г\n🥑 Жиры: {fat}г"
},

# === DAILY SUMMARY ===
"nutrition_daily_summary_header": {
    "en": "📊 <b>Daily Summary - {date}</b>",
    "ru": "📊 <b>Дневная сводка - {date}</b>"
},

"nutrition_todays_intake": {
    "en": "<b>Today's Intake:</b>\n🔥 Calories: {calories} kcal\n🥩 Protein: {protein}g\n🍞 Carbs: {carbs}g\n🥑 Fat: {fat}g",
    "ru": "<b>Приём за сегодня:</b>\n🔥 Калории: {calories} ккал\n🥩 Белки: {protein}г\n🍞 Углеводы: {carbs}г\n🥑 Жиры: {fat}г"
},

"nutrition_progress_vs_goals": {
    "en": "<b>Progress vs Goals:</b>\n🎯 Calories: {cal_percent}% ({cal_current}/{cal_goal})\n🎯 Protein: {protein_percent}% ({protein_current}/{protein_goal}g)\n🎯 Carbs: {carbs_percent}% ({carbs_current}/{carbs_goal}g)\n🎯 Fat: {fat_percent}% ({fat_current}/{fat_goal}g)",
    "ru": "<b>Прогресс относительно целей:</b>\n🎯 Калории: {cal_percent}% ({cal_current}/{cal_goal})\n🎯 Белки: {protein_percent}% ({protein_current}/{protein_goal}г)\n🎯 Углеводы: {carbs_percent}% ({carbs_current}/{carbs_goal}г)\n🎯 Жиры: {fat_percent}% ({fat_current}/{fat_goal}г)"
},

"nutrition_set_goals_hint": {
    "en": "💡 <i>Set your daily goals to track progress!</i>",
    "ru": "💡 <i>Установите дневные цели для отслеживания прогресса!</i>"
},

# === SET GOALS ===
"nutrition_current_goals": {
    "en": "🎯 <b>Current Daily Goals:</b>\n\n🔥 Calories: {calories} kcal\n🥩 Protein: {protein}g\n🍞 Carbs: {carbs}g\n🥑 Fat: {fat}g\n\n<b>Choose how you'd like to update your goals:</b>",
    "ru": "🎯 <b>Текущие дневные цели:</b>\n\n🔥 Калории: {calories} ккал\n🥩 Белки: {protein}г\n🍞 Углеводы: {carbs}г\n🥑 Жиры: {fat}г\n\n<b>Выберите, как хотите обновить цели:</b>"
},

"nutrition_set_goals_prompt": {
    "en": "🎯 <b>Set Your Daily Nutrition Goals</b>\n\nChoose your preferred method to set your goals:\n\n✏️ <b>Enter Manually</b> - Input your own targets\n🧮 <b>Calculator</b> - Calculate based on your body metrics and goals",
    "ru": "🎯 <b>Установите дневные цели по питанию</b>\n\nВыберите предпочтительный способ установки целей:\n\n✏️ <b>Ввести вручную</b> - Укажите свои цели\n🧮 <b>Калькулятор</b> - Рассчитать на основе ваших параметров и целей"
},

# === MANUAL GOAL SETTING ===
"nutrition_enter_calories_goal": {
    "en": "✏️ <b>Manual Goal Setting</b>\n\n<b>Enter your daily calorie goal:</b>\n<i>Example: 2000</i>",
    "ru": "✏️ <b>Ручная установка целей</b>\n\n<b>Введите вашу дневную цель по калориям:</b>\n<i>Например: 2000</i>"
},

"nutrition_positive_calories": {
    "en": "Please enter a positive number for calories.",
    "ru": "Пожалуйста, введите положительное число для калорий."
},

"nutrition_valid_calories": {
    "en": "Please enter a valid number for calories.",
    "ru": "Пожалуйста, введите корректное число для калорий."
},

"nutrition_calories_set_enter_protein": {
    "en": "✅ Calorie goal set to {calories} kcal\n\n<b>Now enter your daily protein goal (in grams):</b>\n<i>Example: 150</i>",
    "ru": "✅ Цель по калориям установлена: {calories} ккал\n\n<b>Теперь введите дневную цель по белкам (в граммах):</b>\n<i>Например: 150</i>"
},

"nutrition_positive_protein": {
    "en": "Please enter a positive number for protein.",
    "ru": "Пожалуйста, введите положительное число для белков."
},

"nutrition_valid_protein": {
    "en": "Please enter a valid number for protein.",
    "ru": "Пожалуйста, введите корректное число для белков."
},

"nutrition_protein_set_enter_carbs": {
    "en": "✅ Protein goal set to {protein}g\n\n<b>Now enter your daily carbohydrate goal (in grams):</b>\n<i>Example: 250</i>",
    "ru": "✅ Цель по белкам установлена: {protein}г\n\n<b>Теперь введите дневную цель по углеводам (в граммах):</b>\n<i>Например: 250</i>"
},

"nutrition_positive_carbs": {
    "en": "Please enter a positive number for carbohydrates.",
    "ru": "Пожалуйста, введите положительное число для углеводов."
},

"nutrition_valid_carbs": {
    "en": "Please enter a valid number for carbohydrates.",
    "ru": "Пожалуйста, введите корректное число для углеводов."
},

"nutrition_carbs_set_enter_fat": {
    "en": "✅ Carbohydrate goal set to {carbs}g\n\n<b>Finally, enter your daily fat goal (in grams):</b>\n<i>Example: 70</i>",
    "ru": "✅ Цель по углеводам установлена: {carbs}г\n\n<b>Наконец, введите дневную цель по жирам (в граммах):</b>\n<i>Например: 70</i>"
},

"nutrition_positive_fat": {
    "en": "Please enter a positive number for fat.",
    "ru": "Пожалуйста, введите положительное число для жиров."
},

"nutrition_valid_fat": {
    "en": "Please enter a valid number for fat.",
    "ru": "Пожалуйста, введите корректное число для жиров."
},

"nutrition_goals_set_success": {
    "en": "🎯 <b>Goals Set Successfully!</b>\n\nYour daily nutrition targets:\n🔥 Calories: {calories} kcal\n🥩 Protein: {protein}g\n🍞 Carbs: {carbs}g\n🥑 Fat: {fat}g\n\nYou can now track your progress against these goals!",
    "ru": "🎯 <b>Цели успешно установлены!</b>\n\nВаши дневные цели по питанию:\n🔥 Калории: {calories} ккал\n🥩 Белки: {protein}г\n🍞 Углеводы: {carbs}г\n🥑 Жиры: {fat}г\n\nТеперь вы можете отслеживать прогресс относительно этих целей!"
},

# === CALCULATOR ===
"nutrition_calculator_start": {
    "en": "🧮 <b>Nutrition Goals Calculator</b>\n\nLet's calculate your personalized nutrition goals based on your body metrics and activity level!\n\n<b>First, enter your age:</b>\n<i>Example: 25</i>",
    "ru": "🧮 <b>Калькулятор целей по питанию</b>\n\nДавайте рассчитаем ваши персонализированные цели по питанию на основе ваших параметров и уровня активности!\n\n<b>Сначала введите ваш возраст:</b>\n<i>Например: 25</i>"
},

"nutrition_valid_age": {
    "en": "Please enter a valid age between 15 and 100.",
    "ru": "Пожалуйста, введите корректный возраст от 15 до 100."
},

"nutrition_valid_age_number": {
    "en": "Please enter a valid number for age.",
    "ru": "Пожалуйста, введите корректное число для возраста."
},

"nutrition_age_recorded": {
    "en": "✅ Age recorded!\n\n<b>Now select your gender:</b>",
    "ru": "✅ Возраст записан!\n\n<b>Теперь выберите ваш пол:</b>"
},

"nutrition_gender_selected": {
    "en": "✅ Gender: {emoji} {gender}\n\n<b>Enter your weight in kilograms:</b>\n<i>Example: 75</i>",
    "ru": "✅ Пол: {emoji} {gender}\n\n<b>Введите ваш вес в килограммах:</b>\n<i>Например: 75</i>"
},

"nutrition_valid_weight": {
    "en": "Please enter a valid weight between 30 and 300 kg.",
    "ru": "Пожалуйста, введите корректный вес от 30 до 300 кг."
},

"nutrition_valid_weight_number": {
    "en": "Please enter a valid number for weight.",
    "ru": "Пожалуйста, введите корректное число для веса."
},

"nutrition_weight_recorded": {
    "en": "✅ Weight: {weight}kg\n\n<b>Enter your height in centimeters:</b>\n<i>Example: 175</i>",
    "ru": "✅ Вес: {weight}кг\n\n<b>Введите ваш рост в сантиметрах:</b>\n<i>Например: 175</i>"
},

"nutrition_valid_height": {
    "en": "Please enter a valid height between 120 and 250 cm.",
    "ru": "Пожалуйста, введите корректный рост от 120 до 250 см."
},

"nutrition_valid_height_number": {
    "en": "Please enter a valid number for height.",
    "ru": "Пожалуйста, введите корректное число для роста."
},

"nutrition_height_recorded": {
    "en": "✅ Height: {height}cm\n\n<b>Select your activity level:</b>",
    "ru": "✅ Рост: {height}см\n\n<b>Выберите ваш уровень активности:</b>"
},

"nutrition_activity_recorded": {
    "en": "✅ Activity Level: {activity}\n\n<b>Finally, select your goal:</b>",
    "ru": "✅ Уровень активности: {activity}\n\n<b>Наконец, выберите вашу цель:</b>"
},

"nutrition_calculator_result": {
    "en": "🎯 <b>Goals Calculated Successfully!</b>\n\n<b>Your Profile:</b>\n👤 Age: {age} | Gender: {gender}\n⚖️ Weight: {weight}kg | Height: {height}cm\n🎯 Goal: {goal}\n\n<b>Your Daily Nutrition Goals:</b>\n🔥 Calories: {calories} kcal\n🥩 Protein: {protein}g\n🍞 Carbs: {carbs}g\n🥑 Fat: {fat}g\n\nStart tracking your meals to reach your goals!",
    "ru": "🎯 <b>Цели успешно рассчитаны!</b>\n\n<b>Ваш профиль:</b>\n👤 Возраст: {age} | Пол: {gender}\n⚖️ Вес: {weight}кг | Рост: {height}см\n🎯 Цель: {goal}\n\n<b>Ваши дневные цели по питанию:</b>\n🔥 Калории: {calories} ккал\n🥩 Белки: {protein}г\n🍞 Углеводы: {carbs}г\n🥑 Жиры: {fat}г\n\nНачните отслеживать приёмы пищи для достижения целей!"
},

# === VIEW MEALS ===
"nutrition_no_meals_today": {
    "en": "📋 <b>Today's Meals</b>\n\nNo meals logged today yet!\n\nStart by adding some food to track your nutrition.",
    "ru": "📋 <b>Приёмы пищи за сегодня</b>\n\nСегодня пока нет записей!\n\nНачните с добавления еды для отслеживания питания."
},

"nutrition_todays_meals_header": {
    "en": "📋 <b>Today's Meals - {date}</b>",
    "ru": "📋 <b>Приёмы пищи за сегодня - {date}</b>"
},






}