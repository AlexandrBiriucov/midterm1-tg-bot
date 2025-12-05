

text = {
    "invalid_format": {
        "en": "❌ Invalid format!\n"
            "Use: <code>/log Exercise 3x10x50</code>\n"
            "Example: <code>/log BenchPress 3x10x50</code>",
        "ru": "❌ Неверный формат!\n"
"Используйте: <code>/log Упражнение 3x10x50</code>\n"
"Пример: <code>/log Жим лёжа 3x10x50</code>"
    },

    "invalid_weight": {
        "en": "❌ Invalid weight format!\n"
            "Example: <code>/log BenchPress 3x10x50</code>",
        "ru":"❌ Неверный формат веса!\n"
             "Пример: <code>/log Жим лёжа 3x10x50</code>"
    },

"zero": {
    "en": "❌ Values must be greater than zero!",
    "ru": "❌ Значения должны быть больше нуля!"
},
"invalid_command" : {
    "en" :"❌ Invalid command format.\n"
            "Use: <code>/check_training DD.MM.YYYY</code>\n"
            "Example: <code>/check_training 03.09.2025</code>",
    "ru" : "❌ Неверный формат команды.\n"
"Используйте: <code>/check_training ДД.ММ.ГГГГ</code>\n"
"Пример: <code>/check_training 03.09.2025</code>"
},
"error_1": {
    "en": "❌ Error logging workout: {error}",
    "ru": "❌ Ошибка записи тренировки: {error}"
},
    "error_retrieving": {
        "en": "❌ Error retrieving data: {error}",  # 👈 изменил с {e} на {error}
        "ru": "❌ Ошибка получения данных: {error}"
    },
"no_records_today": {
    "en": "📝 No records for today ({date}).\nUse /log to record a workout!",
    "ru": "📝 Нет записей на сегодня ({date}).\nИспользуйте /log для записи тренировки!"
},

"workouts_for_date": {
    "en": "🏋️ <b>Workouts for {date}:</b>\n\n{workouts}",
    "ru": "🏋️ <b>Тренировки за {date}:</b>\n\n{workouts}"
},

"new_record": {
    "en": "🏆 <b>New record for {exercise}!</b>\n1RM: {new_orm} kg (previous: {prev_orm} kg)",
    "ru": "🏆 <b>Новый рекорд для {exercise}!</b>\n1ПМ: {new_orm} кг (предыдущий: {prev_orm} кг)"
},

"logged_success": {
    "en": "✅ Logged: <b>{exercise}</b> — {sets}x{reps}x{weight} kg",
    "ru": "✅ Записано: <b>{exercise}</b> — {sets}x{reps}x{weight} кг"
},

"invalid_check_training_format": {
    "en": "❌ Invalid command format.\nUse: <code>/check_training DD.MM.YYYY</code>\nExample: <code>/check_training 03.09.2025</code>",
    "ru": "❌ Неверный формат команды.\nИспользуйте: <code>/check_training ДД.ММ.ГГГГ</code>\nПример: <code>/check_training 03.09.2025</code>"
},


"invalid_date_format": {
    "en": "❌ Invalid date format.\nUse: <code>DD.MM.YYYY</code>\nExample: <code>03.09.2025</code>",
    "ru": "❌ Неверный формат даты.\nИспользуйте: <code>ДД.ММ.ГГГГ</code>\nПример: <code>03.09.2025</code>"
},


"no_workout_records": {
    "en": "📝 No workout records for {date}.",
    "ru": "📝 Нет записей тренировок за {date}."
},

"workouts_for_target_date": {
    "en": "🏋️ <b>Workouts for {date}:</b>\n\n{workouts}",
    "ru": "🏋️ <b>Тренировки за {date}:</b>\n\n{workouts}"
},

"error_retrieving_data": {
    "en": "❌ Error retrieving data: {error}",
    "ru": "❌ Ошибка получения данных: {error}"
},

"invalid_year_format": {
    "en": "❌ Invalid year format.\nUse: <code>/list_trainings [year]</code>\nExample: <code>/list_trainings 2024</code>",
    "ru": "❌ Неверный формат года.\nИспользуйте: <code>/list_trainings [год]</code>\nПример: <code>/list_trainings 2024</code>"
},
"invalid_list_trainings_format": {
    "en": "❌ Invalid command format.\nUse: <code>/list_trainings [year]</code>\nExample: <code>/list_trainings 2024</code>",
    "ru": "❌ Неверный формат команды.\nИспользуйте: <code>/list_trainings [год]</code>\nПример: <code>/list_trainings 2024</code>"
},

"no_workout_records_year": {
    "en": "📝 No workout records for {year}.",
    "ru": "📝 Нет записей тренировок за {year} год."
},

"month_january": {
    "en": "January",
    "ru": "Январь"
},
"month_february": {
    "en": "February",
    "ru": "Февраль"
},
"month_march": {
    "en": "March",
    "ru": "Март"
},
"month_april": {
    "en": "April",
    "ru": "Апрель"
},
"month_may": {
    "en": "May",
    "ru": "Май"
},
"month_june": {
    "en": "June",
    "ru": "Июнь"
},
"month_july": {
    "en": "July",
    "ru": "Июль"
},
"month_august": {
    "en": "August",
    "ru": "Август"
},
"month_september": {
    "en": "September",
    "ru": "Сентябрь"
},
"month_october": {
    "en": "October",
    "ru": "Октябрь"
},
"month_november": {
    "en": "November",
    "ru": "Ноябрь"
},
"month_december": {
    "en": "December",
    "ru": "Декабрь"
},

"training_days_year": {
    "en": "📅 <b>Training days in {year}:</b>\n\n{days}",
    "ru": "📅 <b>Дни тренировок в {year} году:</b>\n\n{days}"
},

"profile_not_found": {
    "en": "❌ Profile not found.\nUse /start to register.",
    "ru": "❌ Профиль не найден.\nИспользуйте /start для регистрации."
},

"user_profile": {
    "en": "👤 <b>User Profile</b>",
    "ru": "👤 <b>Профиль пользователя</b>"
},

"profile_id": {
    "en": "🆔 ID: <code>{telegram_id}</code>",
    "ru": "🆔 ID: <code>{telegram_id}</code>"
},

"profile_name": {
    "en": "👤 Name: {name}",
    "ru": "👤 Имя: {name}"
},

"not_specified": {
    "en": "Not specified",
    "ru": "Не указано"
},

"profile_last_name": {
    "en": "📛 Last name: {last_name}",
    "ru": "📛 Фамилия: {last_name}"
},

"profile_username": {
    "en": "🌐 Username: @{username}",
    "ru": "🌐 Имя пользователя: @{username}"
},

"profile_language": {
    "en": "🗣 Language: {language}",
    "ru": "🗣 Язык: {language}"
},

"profile_timezone": {
    "en": "🌍 Timezone: UTC+{timezone}",
    "ru": "🌍 Часовой пояс: UTC+{timezone}"
},

"workout_statistics": {
    "en": "🏋️‍♂️ <b>Workout Statistics</b>",
    "ru": "🏋️‍♂️ <b>Статистика тренировок</b>"
},

"total_workouts": {
    "en": "📊 Total workouts: {count}",
    "ru": "📊 Всего тренировок: {count}"
},

"records_in_bot": {
    "en": "🔢 Records in bot: {count}",
    "ru": "🔢 Записей в боте: {count}"
},

"first_workout": {
    "en": "📅 First workout: {date}",
    "ru": "📅 Первая тренировка: {date}"
},

"last_workout": {
    "en": "⏰ Last workout: {date}",
    "ru": "⏰ Последняя тренировка: {date}"
},

"registered": {
    "en": "📅 Registered: {date}",
    "ru": "📅 Зарегистрирован: {date}"
},

"updated": {
    "en": "🔄 Updated: {date}",
    "ru": "🔄 Обновлён: {date}"
},

"error_retrieving_profile": {
    "en": "❌ Error retrieving profile: {error}",
    "ru": "❌ Ошибка получения профиля: {error}"
},

"no_workout_records_yet": {
    "en": "📊 You don't have any workout records yet.\nUse /log to record your first workout!",
    "ru": "📊 У вас пока нет записей тренировок.\nИспользуйте /log для записи первой тренировки!"
},

"your_statistics": {
    "en": "📊 <b>Your Statistics</b>",
    "ru": "📊 <b>Ваша статистика</b>"
},

"total_workouts_stat": {
    "en": "🏋️‍♂️ Total workouts: {count}",
    "ru": "🏋️‍♂️ Всего тренировок: {count}"
},

"last_workout_stat": {
    "en": "⏰ Last workout: {date}",
    "ru": "⏰ Последняя тренировка: {date}"
},

"active_days": {
    "en": "📅 Active days: {days}",
    "ru": "📅 Активных дней: {days}"
},

"average_per_day": {
    "en": "📈 Average per day: {avg}",
    "ru": "📈 В среднем за день: {avg}"
},

"error_retrieving_statistics": {
    "en": "❌ Error retrieving statistics: {error}",
    "ru": "❌ Ошибка получения статистики: {error}"
},


"year_range_error": {
    "en": "❌ Year must be between 2000 and 2100",
    "ru": "❌ Год должен быть между 2000 и 2100"
},









}