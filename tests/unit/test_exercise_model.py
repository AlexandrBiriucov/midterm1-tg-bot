import pytest

from src.models.exercise import Exercise

def test_exercise_model():
    exercise = Exercise(name="Bench Press", category="Chest")
    assert exercise.name == "Bench Press"
