from src.models.exercise import Exercise

INITIAL_EXERCISES = [
    {"name": "Bench Press", "category": "Chest", "primary_muscle": "Pectorals"},
    {"name": "Squat", "category": "Legs", "primary_muscle": "Quadriceps"},
    {"name": "Deadlift", "category": "Back", "primary_muscle": "Erector Spinae"}
]

def seed_exercises(session):
    for exercise_data in INITIAL_EXERCISES:
        exercise = Exercise(**exercise_data)
        session.add(exercise)
    session.commit()
