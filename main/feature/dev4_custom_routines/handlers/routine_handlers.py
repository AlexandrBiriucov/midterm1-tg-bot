import json
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command

# Импорт из папки db (на том же уровне)
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from db.routine_db import routine_db

# Создаем роутер
routine_router = Router()

# Для хранения состояний пользователей
user_states = {}

# Предустановленные программы тренировок по уровням
PRESET_ROUTINES = {
    "beginner_fullbody": {
        "name": "🟢 Full Body (Начинающий)",
        "level": "beginner",
        "description": "Базовая программа для новичков, 3 раза в неделю",
        "schedule": "Пн, Ср, Пт",
        "exercises": [
            "🏋️ Приседания со штангой - 3х10",
            "💪 Жим штанги лёжа - 3х10", 
            "📏 Тяга штанги в наклоне - 3х10",
            "🦵 Выпады - 3х12",
            "📊 Планка - 3х30 сек"
        ]
    },
    
    "beginner_ppl": {
        "name": "🟢 PPL (Начинающий)", 
        "level": "beginner",
        "description": "Толкай-Тяни-Ноги для новичков",
        "schedule": "Пн: Толкай, Вт: Тяни, Ср: Ноги, Чт: отдых, Пт: повтор",
        "exercises": [
            "День 1 (Толкай):",
            "- Жим штанги 3х10",
            "- Жим гантелей 3х12", 
            "- Отжимания 3хMAX",
            "",
            "День 2 (Тяни):",
            "- Тяга штанги 3х10",
            "- Подтягивания/Тяга верхнего блока 3х10",
            "- Гиперэкстензия 3х15",
            "",
            "День 3 (Ноги):", 
            "- Приседания 3х10",
            "- Мёртвая тяга 3х10",
            "- Разгибания ног 3х12"
        ]
    },

    "intermediate_upper_lower": {
        "name": "🟡 Upper/Lower (Средний)",
        "level": "intermediate", 
        "description": "Сплит верх/низ для продолжающих",
        "schedule": "Пн: Верх, Вт: Низ, Ср: отдых, Чт: Верх, Пт: Низ",
        "exercises": [
            "День 1 (Верхняя часть):",
            "- Жим штанги 4х8",
            "- Тяга штанги 4х8", 
            "- Жим гантелей 3х10",
            "- Подтягивания 3хMAX",
            "",
            "День 2 (Нижняя часть):",
            "- Приседания 4х8", 
            "- Мёртвая тяга 3х8",
            "- Жим ногами 3х10",
            "- Икры 4х15"
        ]
    }
}

# Команда /routines
@routine_router.message(Command("routines"))
async def show_routines(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Начинающий", callback_data="level_beginner")],
        [InlineKeyboardButton(text="🟡 Средний", callback_data="level_intermediate")],
        [InlineKeyboardButton(text="🔴 Продвинутый", callback_data="level_advanced")]
    ])
    
    await message.answer(
        "🏋️ **Выбери свой уровень:**\n\n"
        "🟢 **Начинающий** - до 3 месяцев тренировок\n"  
        "🟡 **Средний** - 3-12 месяцев опыта\n"
        "🔴 **Продвинутый** - 1-2 года тренировок",
        reply_markup=keyboard
    )

# Команда /custom_routines
@routine_router.message(Command("custom_routines"))
async def custom_routines(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Создать рутину", callback_data="create_routine")],
        [InlineKeyboardButton(text="📋 Мои рутины", callback_data="my_routines")]
    ])
    
    await message.answer(
        "🎯 **Управление кастомными тренировками:**",
        reply_markup=keyboard
    )

# Обработчик выбора уровня
@routine_router.callback_query(F.data.startswith("level_"))
async def show_level_routines(callback: CallbackQuery):
    level = callback.data.replace('level_', '')
    
    level_routines = {k: v for k, v in PRESET_ROUTINES.items() if v['level'] == level}
    
    if not level_routines:
        await callback.message.answer("❌ Программы для этого уровня пока не добавлены")
        return
    
    keyboard_buttons = []
    for routine_id, routine in level_routines.items():
        keyboard_buttons.append([InlineKeyboardButton(
            text=routine['name'], 
            callback_data=f"show_routine_{routine_id}"
        )])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    level_names = {
        'beginner': '🟢 Начинающий',
        'intermediate': '🟡 Средний', 
        'advanced': '🔴 Продвинутый'
    }
    
    await callback.message.edit_text(
        f"**{level_names[level]} - Выбери программу:**",
        reply_markup=keyboard
    )

# Показать детали routine
@routine_router.callback_query(F.data.startswith("show_routine_"))
async def show_routine_details(callback: CallbackQuery):
    routine_id = callback.data.replace('show_routine_', '')
    routine = PRESET_ROUTINES[routine_id]
    
    exercises_text = "\n".join(routine['exercises'])
    
    response = (
        f"🏋️ **{routine['name']}**\n\n"
        f"📝 **Описание:** {routine['description']}\n"
        f"📅 **Расписание:** {routine['schedule']}\n\n"
        f"**Упражнения:**\n{exercises_text}"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="💾 Сохранить программу", callback_data=f"save_routine_{routine_id}")
    ]])
    
    await callback.message.answer(response, reply_markup=keyboard)

# Сохранение routine
@routine_router.callback_query(F.data.startswith("save_routine_"))
async def save_routine(callback: CallbackQuery):
    routine_id = callback.data.replace('save_routine_', '')
    user_id = callback.from_user.id
    routine = PRESET_ROUTINES[routine_id]
    
    routine_db.save_custom_routine(user_id, routine['name'], routine)
    await callback.answer(f"✅ Программа '{routine['name']}' сохранена!")

# Создание своей routine
@routine_router.callback_query(F.data == "create_routine")
async def create_routine(callback: CallbackQuery):
    instructions = (
        "📝 **Создание своей программы:**\n\n"
        "Отправь данные в формате:\n"
        "Название программы\n"
        "Описание\n" 
        "Расписание\n"
        "Упражнение 1\n"
        "Упражнение 2\n"
        "Упражнение 3\n"
    )
    
    user_states[callback.from_user.id] = 'creating_routine'
    await callback.message.answer(instructions)

# Обработка ввода custom routine
@routine_router.message(F.text)
async def process_routine_creation(message: Message):
    user_id = message.from_user.id
    
    if user_states.get(user_id) != 'creating_routine':
        return
    
    lines = message.text.split('\n')
    
    if len(lines) < 4:
        await message.answer("❌ Недостаточно данных. Нужно минимум 4 строки!")
        return
    
    routine_data = {
        'name': lines[0],
        'description': lines[1],
        'schedule': lines[2], 
        'exercises': lines[3:]
    }
    
    routine_db.save_custom_routine(user_id, routine_data['name'], routine_data)
    user_states[user_id] = None
    
    await message.answer(
        f"✅ **Программа создана!**\n\n"
        f"🏋️ **{routine_data['name']}**\n"
        f"📝 {routine_data['description']}\n"
        f"📅 {routine_data['schedule']}\n\n"
        f"Используй /custom_routines для просмотра"
    )

# Показать мои routines
@routine_router.callback_query(F.data == "my_routines")
async def show_my_routines(callback: CallbackQuery):
    user_id = callback.from_user.id
    routines = routine_db.get_user_routines(user_id)
    
    if not routines:
        await callback.message.answer("📭 У тебя пока нет сохраненных программ")
        return
    
    response = "📋 **Твои сохраненные программы:**\n\n"
    
    for i, routine in enumerate(routines, 1):
        response += f"{i}. **{routine['name']}**\n"
        response += f"   {routine['data']['description']}\n\n"
    
    await callback.message.answer(response)