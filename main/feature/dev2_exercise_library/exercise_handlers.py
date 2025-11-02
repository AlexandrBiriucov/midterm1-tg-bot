#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exercise Library Handlers for Dev2
Integrated exercise search and filtering
"""

import logging
from typing import List
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
)

from .exercise_db import ExerciseDatabase

logger = logging.getLogger(__name__)

# Create router for exercise library
exercise_router = Router()

# Initialize database
db = ExerciseDatabase()


# FSM States
class ExerciseStates(StatesGroup):
    selecting_muscle_group = State()
    selecting_muscle = State()
    selecting_equipment = State()
    selecting_difficulty = State()
    selecting_exercise = State()
    exercise_selected = State()


# Helper function to create inline keyboard
def create_inline_keyboard(items: List[str], prefix: str, add_back: bool = False) -> InlineKeyboardMarkup:
    """Create inline keyboard from list of items"""
    buttons = []

    for i in range(0, len(items), 2):
        row = []
        for j in range(i, min(i + 2, len(items))):
            display_text = items[j][:25] + "..." if len(items[j]) > 25 else items[j]
            row.append(InlineKeyboardButton(
                text=display_text,
                callback_data=f"{prefix}_{items[j]}"
            ))
        buttons.append(row)

    if add_back:
        buttons.append([InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="exercise_back"
        )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Command handlers
@exercise_router.message(Command("exercise"))
async def cmd_exercise(message: Message, state: FSMContext):
    """Handle /exercise command - start exercise selection"""
    await state.clear()
    await start_exercise_selection(message, state)


@exercise_router.message(Command("exercise_stats"))
async def cmd_exercise_stats(message: Message):
    """Handle /exercise_stats command - show database statistics"""
    stats = db.get_database_stats()

    stats_text = (
        f"📊 *Статистика базы упражнений*\n\n"
        f"📈 Всего упражнений: *{stats['total_exercises']}*\n"
        f"💪 Групп мышц: *{stats['muscle_groups']}*\n"
        f"🏋️ Типов оборудования: *{stats['equipment_types']}*\n"
        f"📊 Уровней сложности: *{stats['difficulty_levels']}*\n\n"
        f"🗄️ База данных содержит подробные описания, "
        f"инструкции и советы для каждого упражнения."
    )

    await message.answer(stats_text, parse_mode="Markdown")


# Start exercise selection process
async def start_exercise_selection(message: Message, state: FSMContext):
    """Start exercise selection process"""
    await state.set_state(ExerciseStates.selecting_muscle_group)

    muscle_groups = db.get_unique_values('muscle_group')

    if not muscle_groups:
        await message.answer(
            "⚠️ База данных пуста! Пожалуйста, инициализируйте базу данных.\n"
            "Запустите: python feature/dev2_exercise_library/initialize_exercises.py"
        )
        return

    keyboard = create_inline_keyboard(muscle_groups, "mg")

    text = "🎯 *Шаг 1/4: Выберите группу мышц*"
    await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)


# Filter selection handlers
@exercise_router.callback_query(StateFilter(ExerciseStates.selecting_muscle_group))
async def process_muscle_group_selection(callback: CallbackQuery, state: FSMContext):
    """Handle muscle group selection"""
    muscle_group = callback.data.replace("mg_", "")
    await state.update_data(muscle_group=muscle_group)
    await state.set_state(ExerciseStates.selecting_muscle)

    filtered_exercises = db.get_exercises_by_filter(muscle_group=muscle_group)
    available_muscles = list(set(ex['muscle'] for ex in filtered_exercises))
    muscles = sorted(available_muscles)

    keyboard = create_inline_keyboard(muscles, "m", add_back=True)

    text = (
        f"🎯 *Шаг 2/4: Выберите конкретную мышцу*\n\n"
        f"**{muscle_group}**"
    )

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()


@exercise_router.callback_query(StateFilter(ExerciseStates.selecting_muscle))
async def process_muscle_selection(callback: CallbackQuery, state: FSMContext):
    """Handle muscle selection"""
    data = await state.get_data()

    muscle = callback.data.replace("m_", "")
    await state.update_data(muscle=muscle)
    await state.set_state(ExerciseStates.selecting_equipment)

    filtered_exercises = db.get_exercises_by_filter(
        muscle_group=data["muscle_group"], muscle=muscle
    )
    available_equipment = list(set(ex['equipment'] for ex in filtered_exercises))
    equipment_list = sorted(available_equipment)

    keyboard = create_inline_keyboard(equipment_list, "eq", add_back=True)

    text = (
        f"🎯 *Шаг 3/4: Выберите оборудование*\n\n"
        f"**{data['muscle_group']} → {muscle}**"
    )

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()


@exercise_router.callback_query(StateFilter(ExerciseStates.selecting_equipment))
async def process_equipment_selection(callback: CallbackQuery, state: FSMContext):
    """Handle equipment selection"""
    data = await state.get_data()

    equipment = callback.data.replace("eq_", "")
    await state.update_data(equipment=equipment)
    await state.set_state(ExerciseStates.selecting_difficulty)

    filtered_exercises = db.get_exercises_by_filter(
        muscle_group=data["muscle_group"],
        muscle=data["muscle"], equipment=equipment
    )
    available_difficulties = list(set(ex['difficulty'] for ex in filtered_exercises))

    # Sort by difficulty
    difficulty_order = ['Easy', 'Medium', 'Hard']
    available_difficulties.sort(key=lambda x: difficulty_order.index(x) if x in difficulty_order else 999)

    keyboard = create_inline_keyboard(available_difficulties, "diff", add_back=True)

    text = (
        f"🎯 *Шаг 4/4: Выберите уровень сложности*\n\n"
        f"**{data['muscle_group']} → {data['muscle']} → {equipment}**"
    )

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()


@exercise_router.callback_query(StateFilter(ExerciseStates.selecting_difficulty))
async def process_difficulty_selection(callback: CallbackQuery, state: FSMContext):
    """Handle difficulty selection"""
    data = await state.get_data()

    difficulty = callback.data.replace("diff_", "")
    await state.update_data(difficulty=difficulty)
    await state.set_state(ExerciseStates.selecting_exercise)

    exercises = db.get_exercises_by_filter(
        muscle_group=data["muscle_group"], muscle=data["muscle"],
        equipment=data["equipment"], difficulty=difficulty
    )

    if not exercises:
        await callback.message.edit_text(
            "😕 Упражнений с такими параметрами не найдено. Попробуйте изменить фильтры.",
            parse_mode="Markdown"
        )
        return

    exercise_names = [ex['name'] for ex in exercises]
    keyboard = create_inline_keyboard(exercise_names, "ex", add_back=True)

    text = (
        f"🎯 *Выберите упражнение ({len(exercises)} доступно)*\n\n"
        f"**{data['muscle_group']} → {data['muscle']} → {data['equipment']} → {difficulty}**"
    )

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()


@exercise_router.callback_query(StateFilter(ExerciseStates.selecting_exercise))
async def process_exercise_selection(callback: CallbackQuery, state: FSMContext):
    """Handle specific exercise selection"""
    exercise_name = callback.data.replace("ex_", "")
    exercise_data = db.get_exercise_by_name(exercise_name)

    if not exercise_data:
        await callback.answer("❌ Упражнение не найдено")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="exercise_back"),
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="exercise_main_menu")
        ]
    ])

    name = exercise_data['name']
    muscle_group = exercise_data['muscle_group']
    muscle = exercise_data['muscle']
    equipment = exercise_data['equipment']
    difficulty = exercise_data['difficulty']
    description = exercise_data['description']
    instructions = exercise_data.get('instructions', '')
    tips = exercise_data.get('tips', '')

    # Get emoji for difficulty
    difficulty_emoji = {'Easy': '🟢', 'Medium': '🟡', 'Hard': '🔴'}.get(difficulty, '')

    text = (
        f"✅ *Упражнение выбрано*\n\n"
        f"🏋️ **{name}**\n\n"
        f"💪 **{muscle_group}** → {muscle}\n"
        f"🏋️‍♂️ **{equipment}**\n"
        f"{difficulty_emoji} **{difficulty}**\n\n"
        f"📝 *Описание:* {description}\n\n"
    )

    if instructions:
        text += f"📋 *Техника выполнения:* {instructions}\n\n"

    if tips:
        text += f"💡 *Советы и рекомендации:* {tips}"
    else:
        text += f"💡 *Советы:* Начните с разминки, следите за техникой и дышите равномерно во время выполнения."

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()
    await state.set_state(ExerciseStates.exercise_selected)


# Navigation handlers
@exercise_router.callback_query(F.data == "exercise_back")
async def process_back(callback: CallbackQuery, state: FSMContext):
    """Handle back navigation"""
    current_state = await state.get_state()
    
    if current_state == ExerciseStates.selecting_muscle:
        # Go back to muscle group selection
        await state.set_state(ExerciseStates.selecting_muscle_group)
        await start_exercise_selection(callback.message, state)
    elif current_state == ExerciseStates.selecting_equipment:
        # Go back to muscle selection
        data = await state.get_data()
        await state.set_state(ExerciseStates.selecting_muscle_group)
        await process_muscle_group_selection(
            CallbackQuery(data=f"mg_{data['muscle_group']}", message=callback.message), 
            state
        )
    # Add more back navigation logic as needed
    
    await callback.answer()


@exercise_router.callback_query(F.data == "exercise_main_menu")
async def process_main_menu(callback: CallbackQuery, state: FSMContext):
    """Return to main menu"""
    await state.clear()
    await callback.message.edit_text(
        "Возвращаюсь в главное меню... Используйте /help для списка команд."
    )
    await callback.answer()
