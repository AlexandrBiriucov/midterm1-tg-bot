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

from localization.utils import t
from bot.features.dev1_workout_tracking.services import get_lang

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


# Translation dictionaries for database values
MUSCLE_GROUPS = {
    "Chest": {"en": "Chest", "ru": "Грудь"},
    "Back": {"en": "Back", "ru": "Спина"},
    "Shoulders": {"en": "Shoulders", "ru": "Плечи"},
    "Arms": {"en": "Arms", "ru": "Руки"},
    "Legs": {"en": "Legs", "ru": "Ноги"},
    "Abs": {"en": "Abs", "ru": "Пресс"},
    "Cardio": {"en": "Cardio", "ru": "Кардио"},
    "Functional": {"en": "Functional", "ru": "Функциональные"},
    "Stretching": {"en": "Stretching", "ru": "Растяжка"}
}

MUSCLES = {
    # Chest
    "Pectorals": {"en": "Pectorals", "ru": "Грудные"},
    "Upper Chest": {"en": "Upper Chest", "ru": "Верх груди"},
    "Lower Chest": {"en": "Lower Chest", "ru": "Низ груди"},

    # Back
    "Lats": {"en": "Lats", "ru": "Широчайшие"},
    "Traps": {"en": "Traps", "ru": "Трапеции"},
    "Lower Back": {"en": "Lower Back", "ru": "Поясница"},
    "Rhomboids": {"en": "Rhomboids", "ru": "Ромбовидные"},

    # Shoulders
    "Front Delts": {"en": "Front Delts", "ru": "Передние дельты"},
    "Side Delts": {"en": "Side Delts", "ru": "Средние дельты"},
    "Rear Delts": {"en": "Rear Delts", "ru": "Задние дельты"},

    # Arms
    "Biceps": {"en": "Biceps", "ru": "Бицепс"},
    "Triceps": {"en": "Triceps", "ru": "Трицепс"},
    "Forearms": {"en": "Forearms", "ru": "Предплечья"},

    # Legs
    "Quadriceps": {"en": "Quadriceps", "ru": "Квадрицепс"},
    "Hamstrings": {"en": "Hamstrings", "ru": "Бицепс бедра"},
    "Glutes": {"en": "Glutes", "ru": "Ягодицы"},
    "Calves": {"en": "Calves", "ru": "Икры"},
    "Adductors": {"en": "Adductors", "ru": "Приводящие"},
    "Hamstrings, Glutes": {"en": "Hamstrings, Glutes", "ru": "Бицепс бедра, Ягодицы"},

    # Abs
    "Rectus Abdominis": {"en": "Rectus Abdominis", "ru": "Прямая мышца живота"},
    "Obliques": {"en": "Obliques", "ru": "Косые мышцы"},
    "Full Core": {"en": "Full Core", "ru": "Весь корпус"},

    # Cardio
    "Full Body": {"en": "Full Body", "ru": "Всё тело"},
    "Lower Body": {"en": "Lower Body", "ru": "Низ тела"},

    # Functional
    "Compound": {"en": "Compound", "ru": "Комплексные"},

    # Stretching
    "Flexibility": {"en": "Flexibility", "ru": "Гибкость"}
}

EQUIPMENT = {
    "Barbell": {"en": "Barbell", "ru": "Штанга"},
    "Dumbbell": {"en": "Dumbbell", "ru": "Гантели"},
    "Bodyweight": {"en": "Bodyweight", "ru": "Вес тела"},
    "Cable": {"en": "Cable", "ru": "Блочный тренажёр"},
    "Machine": {"en": "Machine", "ru": "Тренажёр"},
    "EZ-Bar": {"en": "EZ-Bar", "ru": "EZ-штанга"},
    "Bench": {"en": "Bench", "ru": "Скамья"},
    "Pull-up Bar": {"en": "Pull-up Bar", "ru": "Турник"},
    "Kettlebell": {"en": "Kettlebell", "ru": "Гиря"},
    "Rope": {"en": "Rope", "ru": "Канат"},
    "Sled": {"en": "Sled", "ru": "Сани"},
    "Sandbag": {"en": "Sandbag", "ru": "Мешок с песком"},
    "Battle Ropes": {"en": "Battle Ropes", "ru": "Боевые канаты"},
    "Medicine Ball": {"en": "Medicine Ball", "ru": "Медицинбол"},
    "Jump Rope": {"en": "Jump Rope", "ru": "Скакалка"},
    "Box": {"en": "Box", "ru": "Бокс"},
    "Mat": {"en": "Mat", "ru": "Коврик"}
}

DIFFICULTY = {
    "Easy": {"en": "Easy", "ru": "Лёгкий"},
    "Medium": {"en": "Medium", "ru": "Средний"},
    "Hard": {"en": "Hard", "ru": "Сложный"}
}


def translate_value(value: str, dict_name: dict, lang: str) -> str:
    """Translate database value to user language"""
    translation = dict_name.get(value, {})
    return translation.get(lang, value)


def translate_list(items: List[str], dict_name: dict, lang: str) -> List[tuple]:
    """Translate list of items and return (translated, original) tuples"""
    return [(translate_value(item, dict_name, lang), item) for item in items]


# Helper function to create inline keyboard
def create_inline_keyboard(items: List[str], prefix: str, lang: str, translation_dict: dict = None,
                           add_back: bool = False) -> InlineKeyboardMarkup:
    """Create inline keyboard from list of items with optional translation"""
    buttons = []

    # Translate items if dictionary provided
    if translation_dict:
        translated_items = translate_list(items, translation_dict, lang)
    else:
        translated_items = [(item, item) for item in items]

    for i in range(0, len(translated_items), 2):
        row = []
        for j in range(i, min(i + 2, len(translated_items))):
            display_text, original_value = translated_items[j]
            display_text = display_text[:25] + "..." if len(display_text) > 25 else display_text
            row.append(InlineKeyboardButton(
                text=display_text,
                callback_data=f"{prefix}_{original_value}"
            ))
        buttons.append(row)

    if add_back:
        buttons.append([InlineKeyboardButton(
            text=t("exercise_back_button", lang),
            callback_data="exercise_back"
        )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Command handlers
@exercise_router.message(Command("exercise"))
async def cmd_exercise(message: Message, state: FSMContext):
    """Handle /exercise command - start exercise selection"""
    lang = get_lang(message.from_user.id)
    await state.clear()
    await state.update_data(lang=lang)
    await start_exercise_selection(message, state)


@exercise_router.message(Command("exercise_stats"))
async def cmd_exercise_stats(message: Message):
    """Handle /exercise_stats command - show database statistics"""
    lang = get_lang(message.from_user.id)
    stats = db.get_database_stats()

    await message.answer(
        t("exercise_db_stats", lang,
          total=stats['total_exercises'],
          groups=stats['muscle_groups'],
          equipment=stats['equipment_types'],
          levels=stats['difficulty_levels']),
        parse_mode="HTML"
    )


# Start exercise selection process
async def start_exercise_selection(message: Message, state: FSMContext):
    """Start exercise selection process"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    await state.set_state(ExerciseStates.selecting_muscle_group)

    muscle_groups = db.get_unique_values('muscle_group')

    if not muscle_groups:
        await message.answer(t("exercise_db_empty", lang))
        return

    keyboard = create_inline_keyboard(muscle_groups, "mg", lang, MUSCLE_GROUPS)

    await message.answer(
        t("exercise_step1", lang),
        parse_mode="HTML",
        reply_markup=keyboard
    )


# Filter selection handlers
@exercise_router.callback_query(StateFilter(ExerciseStates.selecting_muscle_group))
async def process_muscle_group_selection(callback: CallbackQuery, state: FSMContext):
    """Handle muscle group selection"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    muscle_group = callback.data.replace("mg_", "")
    await state.update_data(muscle_group=muscle_group)
    await state.set_state(ExerciseStates.selecting_muscle)

    filtered_exercises = db.get_exercises_by_filter(muscle_group=muscle_group)
    available_muscles = list(set(ex['muscle'] for ex in filtered_exercises))
    muscles = sorted(available_muscles)

    keyboard = create_inline_keyboard(muscles, "m", lang, MUSCLES, add_back=True)

    muscle_group_translated = translate_value(muscle_group, MUSCLE_GROUPS, lang)

    await callback.message.edit_text(
        t("exercise_step2", lang, muscle_group=muscle_group_translated),
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await callback.answer()


@exercise_router.callback_query(StateFilter(ExerciseStates.selecting_muscle))
async def process_muscle_selection(callback: CallbackQuery, state: FSMContext):
    """Handle muscle selection"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    muscle = callback.data.replace("m_", "")
    await state.update_data(muscle=muscle)
    await state.set_state(ExerciseStates.selecting_equipment)

    filtered_exercises = db.get_exercises_by_filter(
        muscle_group=data["muscle_group"], muscle=muscle
    )
    available_equipment = list(set(ex['equipment'] for ex in filtered_exercises))
    equipment_list = sorted(available_equipment)

    keyboard = create_inline_keyboard(equipment_list, "eq", lang, EQUIPMENT, add_back=True)

    muscle_group_translated = translate_value(data['muscle_group'], MUSCLE_GROUPS, lang)
    muscle_translated = translate_value(muscle, MUSCLES, lang)

    await callback.message.edit_text(
        t("exercise_step3", lang,
          muscle_group=muscle_group_translated,
          muscle=muscle_translated),
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await callback.answer()


@exercise_router.callback_query(StateFilter(ExerciseStates.selecting_equipment))
async def process_equipment_selection(callback: CallbackQuery, state: FSMContext):
    """Handle equipment selection"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

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

    keyboard = create_inline_keyboard(available_difficulties, "diff", lang, DIFFICULTY, add_back=True)

    muscle_group_translated = translate_value(data['muscle_group'], MUSCLE_GROUPS, lang)
    muscle_translated = translate_value(data['muscle'], MUSCLES, lang)
    equipment_translated = translate_value(equipment, EQUIPMENT, lang)

    await callback.message.edit_text(
        t("exercise_step4", lang,
          muscle_group=muscle_group_translated,
          muscle=muscle_translated,
          equipment=equipment_translated),
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await callback.answer()


@exercise_router.callback_query(StateFilter(ExerciseStates.selecting_difficulty))
async def process_difficulty_selection(callback: CallbackQuery, state: FSMContext):
    """Handle difficulty selection"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    difficulty = callback.data.replace("diff_", "")
    await state.update_data(difficulty=difficulty)
    await state.set_state(ExerciseStates.selecting_exercise)

    exercises = db.get_exercises_by_filter(
        muscle_group=data["muscle_group"], muscle=data["muscle"],
        equipment=data["equipment"], difficulty=difficulty
    )

    if not exercises:
        await callback.message.edit_text(
            t("exercise_no_results", lang),
            parse_mode="HTML"
        )
        return

    exercise_names = [ex['name'] for ex in exercises]
    keyboard = create_inline_keyboard(exercise_names, "ex", lang)

    muscle_group_translated = translate_value(data['muscle_group'], MUSCLE_GROUPS, lang)
    muscle_translated = translate_value(data['muscle'], MUSCLES, lang)
    equipment_translated = translate_value(data['equipment'], EQUIPMENT, lang)
    difficulty_translated = translate_value(difficulty, DIFFICULTY, lang)

    await callback.message.edit_text(
        t("exercise_select_final", lang,
          count=len(exercises),
          muscle_group=muscle_group_translated,
          muscle=muscle_translated,
          equipment=equipment_translated,
          difficulty=difficulty_translated),
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await callback.answer()


@exercise_router.callback_query(StateFilter(ExerciseStates.selecting_exercise))
async def process_exercise_selection(callback: CallbackQuery, state: FSMContext):
    """Handle specific exercise selection"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    exercise_name = callback.data.replace("ex_", "")
    exercise_data = db.get_exercise_by_name(exercise_name)

    if not exercise_data:
        await callback.answer(t("exercise_not_found", lang))
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=t("exercise_back_button", lang),
                callback_data="exercise_back"
            ),
            InlineKeyboardButton(
                text=t("exercise_main_menu_button", lang),
                callback_data="exercise_main_menu"
            )
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

    # Translate values
    muscle_group_translated = translate_value(muscle_group, MUSCLE_GROUPS, lang)
    muscle_translated = translate_value(muscle, MUSCLES, lang)
    equipment_translated = translate_value(equipment, EQUIPMENT, lang)
    difficulty_translated = translate_value(difficulty, DIFFICULTY, lang)

    # Get emoji for difficulty
    difficulty_emoji = {'Easy': '🟢', 'Medium': '🟡', 'Hard': '🔴'}.get(difficulty, '')

    text = (
        f"{t('exercise_selected', lang)}\n\n"
        f"🏋️ **{name}**\n\n"
        f"💪 **{muscle_group_translated}** → {muscle_translated}\n"
        f"🏋️‍♂️ **{equipment_translated}**\n"
        f"{difficulty_emoji} **{difficulty_translated}**\n\n"
        f"{t('exercise_description', lang)} {description}\n\n"
    )

    if instructions:
        text += f"{t('exercise_technique', lang)} {instructions}\n\n"

    if tips:
        text += f"{t('exercise_tips', lang)} {tips}"
    else:
        text += t('exercise_default_tips', lang)

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
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
        # Recreate callback with proper structure
        from aiogram.types import User, Chat
        fake_callback = CallbackQuery(
            id="fake",
            from_user=callback.from_user,
            chat_instance="fake",
            data=f"mg_{data['muscle_group']}",
            message=callback.message
        )
        await process_muscle_group_selection(fake_callback, state)
    # Add more back navigation logic as needed

    await callback.answer()


@exercise_router.callback_query(F.data == "exercise_main_menu")
async def process_main_menu(callback: CallbackQuery, state: FSMContext):
    """Return to main menu"""
    data = await state.get_data()
    lang = data.get('lang', 'en')

    await state.clear()
    await callback.message.edit_text(
        t("exercise_return_main", lang)
    )
    await callback.answer()