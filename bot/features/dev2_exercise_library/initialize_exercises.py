#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exercise Database Initialization Script
Populates the unified SQLAlchemy database with 270+ exercises
"""

import logging

logger = logging.getLogger(__name__)


# ============================================================================
# INITIALIZATION FUNCTIONS
# ============================================================================

def initialize_chest_exercises(db):
    """Add chest exercises"""
    logger.info("📦 Adding chest exercises...")
    
    exercises = [
        ('Barbell Bench Press', 'Chest', 'Pectoralis Major', 'Barbell', 'Medium',
         'Basic chest development exercise', 'Lie on bench, lower bar to chest, press up',
         'Keep elbows at 45°, control descent'),
        ('Incline Barbell Press 30°', 'Chest', 'Upper Chest', 'Barbell', 'Medium',
         'Optimal angle for upper chest', 'Set bench to 30° incline, press bar up',
         'This angle best targets upper chest'),
        ('Decline Barbell Press', 'Chest', 'Lower Chest', 'Barbell', 'Medium',
         'Focus on lower chest', 'Negative bench angle, press up', 'Secure feet properly'),
        ('Dumbbell Bench Press', 'Chest', 'Pectoralis Major', 'Dumbbells', 'Medium',
         'Greater range of motion than barbell', 'Lower dumbbells below chest level',
         'Control each dumbbell independently'),
        ('Incline Dumbbell Press', 'Chest', 'Upper Chest', 'Dumbbells', 'Medium',
         'Upper chest development', 'Press dumbbells up and slightly inward',
         'Fully stretch pecs at bottom'),
        ('Dumbbell Flyes', 'Chest', 'Pectoralis Major', 'Dumbbells', 'Easy',
         'Chest isolation exercise', 'Spread arms in arc motion',
         'Maintain slight bend in elbows'),
        ('Cable Flyes', 'Chest', 'Pectoralis Major', 'Cables', 'Easy',
         'Constant tension throughout range', 'Bring handles together in arc motion',
         'Control negative phase'),
        ('Push-ups', 'Chest', 'Pectoralis Major', 'Bodyweight', 'Easy',
         'Basic bodyweight exercise', 'Lower until chest touches floor',
         'Keep body straight from head to heels'),
        ('Diamond Push-ups', 'Chest', 'Inner Chest, Triceps', 'Bodyweight', 'Hard',
         'Hands in diamond shape', 'Touch thumbs and index fingers',
         'Keep elbows close to body'),
        ('Dips', 'Chest', 'Lower Chest', 'Parallel Bars', 'Medium',
         'Basic lower chest exercise', 'Lean forward, lower down', 'Don\'t go too deep'),
    ]
    
    for ex in exercises:
        db.add_exercise(*ex)
    
    logger.info(f"✅ Added {len(exercises)} chest exercises")


def initialize_back_exercises(db):
    """Add back exercises"""
    logger.info("📦 Adding back exercises...")
    
    exercises = [
        ('Wide-Grip Pull-ups', 'Back', 'Latissimus Dorsi', 'Pull-up Bar', 'Hard',
         'Basic exercise for back width', 'Grip wider than shoulders, pull to chest',
         'Don\'t swing'),
        ('Chin-ups', 'Back', 'Lats, Biceps', 'Pull-up Bar', 'Medium',
         'Greater bicep emphasis', 'Palms toward you', 'Easier than regular pull-ups'),
        ('Bent-over Barbell Row', 'Back', 'Lats, Rhomboids', 'Barbell', 'Medium',
         'Basic for back thickness', '45° bend, pull to waist', 'Keep back straight'),
        ('T-Bar Row', 'Back', 'Lats, Traps', 'Barbell', 'Medium',
         'Comfortable row position', 'Pull to chest', 'Squeeze blades at top'),
        ('Single Arm Dumbbell Row', 'Back', 'Latissimus Dorsi', 'Dumbbells', 'Easy',
         'Each side isolation', 'Knee on bench, elbow back and up',
         'Focus on pulling with back not arm'),
        ('Conventional Deadlift', 'Back', 'Erectors, Traps', 'Barbell', 'Hard',
         'King of exercises', 'Floor to full extension', 'Back straight, chest up'),
        ('Romanian Deadlift', 'Back', 'Erectors, Hamstrings', 'Barbell', 'Medium',
         'Focus posterior chain', 'Lower to mid-shin', 'Knees slightly bent'),
        ('Wide-Grip Lat Pulldown', 'Back', 'Latissimus Dorsi', 'Cables', 'Medium',
         'Pull-up alternative', 'Pull to upper chest', 'Lean back slightly'),
        ('Seated Cable Row', 'Back', 'Lats, Rhomboids', 'Cables', 'Easy',
         'Basic seated row', 'Pull handle to stomach', 'Keep back straight'),
        ('Barbell Shrugs', 'Back', 'Trapezius', 'Barbell', 'Easy',
         'Trap isolation', 'Lift shoulders up', 'Don\'t roll shoulders'),
    ]
    
    for ex in exercises:
        db.add_exercise(*ex)
    
    logger.info(f"✅ Added {len(exercises)} back exercises")


def initialize_shoulder_exercises(db):
    """Add shoulder exercises"""
    logger.info("📦 Adding shoulder exercises...")
    
    exercises = [
        ('Military Press', 'Shoulders', 'Front Delts', 'Barbell', 'Hard',
         'Basic shoulder exercise', 'Press from chest overhead',
         'Core tight for stability'),
        ('Seated Dumbbell Press', 'Shoulders', 'Front Delts', 'Dumbbells', 'Medium',
         'Independent arm movement', 'Press from shoulders up',
         'Greater stabilization needed'),
        ('Arnold Press', 'Shoulders', 'All Deltoid Heads', 'Dumbbells', 'Medium',
         'Rotational movement', 'Rotate during press', 'Greater range of motion'),
        ('Standing Lateral Raises', 'Shoulders', 'Side Delts', 'Dumbbells', 'Easy',
         'Side deltoid isolation', 'Raise arms to sides', 'Not above shoulders'),
        ('Bent-over Lateral Raises', 'Shoulders', 'Rear Delts', 'Dumbbells', 'Easy',
         'Rear deltoid isolation', 'Bend over, raise arms back',
         'Squeeze shoulder blades'),
        ('Front Raises', 'Shoulders', 'Front Delts', 'Dumbbells', 'Easy',
         'Front deltoid isolation', 'Raise arms in front', 'Don\'t use momentum'),
        ('Barbell Upright Row', 'Shoulders', 'Side Delts, Traps', 'Barbell', 'Medium',
         'Elbow elevation', 'Pull to chin', 'Elbows higher than wrists'),
        ('Cable Lateral Raises', 'Shoulders', 'Side Delts', 'Cables', 'Easy',
         'Constant tension', 'Pull handles to sides', 'Tension throughout range'),
        ('Face Pulls', 'Shoulders', 'Rear Delts', 'Cables', 'Easy',
         'Shoulder health exercise', 'Pull rope to face', 'Elbows apart'),
        ('Handstand Push-ups', 'Shoulders', 'Front Delts', 'Bodyweight', 'Hard',
         'Advanced exercise', 'Push-ups upside down', 'Requires balance and strength'),
    ]
    
    for ex in exercises:
        db.add_exercise(*ex)
    
    logger.info(f"✅ Added {len(exercises)} shoulder exercises")


def initialize_arm_exercises(db):
    """Add arm exercises"""
    logger.info("📦 Adding arm exercises...")
    
    exercises = [
        # Biceps
        ('Barbell Curls', 'Arms', 'Biceps', 'Barbell', 'Medium',
         'Classic bicep exercise', 'Bend arms at elbows', 'Don\'t swing body'),
        ('Dumbbell Curls', 'Arms', 'Biceps', 'Dumbbells', 'Easy',
         'Each arm works independently', 'Curl to shoulders', 'Can alternate arms'),
        ('Hammer Curls', 'Arms', 'Biceps, Brachioradialis', 'Dumbbells', 'Easy',
         'Neutral grip', 'Hold like hammers', 'Builds bicep thickness'),
        ('Preacher Curls', 'Arms', 'Biceps', 'Barbell', 'Medium',
         'Bicep isolation', 'Arms on angled support', 'Eliminates cheating'),
        ('Cable Curls', 'Arms', 'Biceps', 'Cables', 'Easy',
         'Constant tension', 'Pull handle to chest', 'Tension throughout range'),
        # Triceps
        ('Close-Grip Bench Press', 'Arms', 'Triceps', 'Barbell', 'Medium',
         'Basic tricep exercise', 'Grip narrower than shoulders',
         'Elbows close to body'),
        ('Lying Tricep Extension', 'Arms', 'Triceps', 'Barbell', 'Medium',
         'Tricep isolation', 'Lower bar behind head', 'Only forearms move'),
        ('Tricep Pushdown', 'Arms', 'Triceps', 'Cables', 'Easy',
         'Popular isolation', 'Press handle down', 'Elbows pinned to sides'),
        ('Parallel Bar Dips', 'Arms', 'Triceps', 'Parallel Bars', 'Medium',
         'Basic bodyweight', 'Keep torso upright', 'Don\'t go too deep'),
        ('Tricep Kickbacks', 'Arms', 'Triceps', 'Dumbbells', 'Easy',
         'Isolation with extension back', 'Lean forward, extend back',
         'Feel tricep contraction'),
    ]
    
    for ex in exercises:
        db.add_exercise(*ex)
    
    logger.info(f"✅ Added {len(exercises)} arm exercises")


def initialize_leg_exercises(db):
    """Add leg exercises"""
    logger.info("📦 Adding leg exercises...")
    
    exercises = [
        ('Back Squat', 'Legs', 'Quadriceps, Glutes', 'Barbell', 'Hard',
         'King of leg exercises', 'Squat to parallel', 'Keep back straight'),
        ('Front Squat', 'Legs', 'Quadriceps', 'Barbell', 'Hard',
         'Bar on front delts', 'More quad work', 'Keep torso upright'),
        ('Leg Press', 'Legs', 'Quadriceps, Glutes', 'Machine', 'Medium',
         'Safe squat alternative', 'Press feet against platform',
         'Don\'t fully lock knees'),
        ('Barbell Lunges', 'Legs', 'Quadriceps, Glutes', 'Barbell', 'Medium',
         'Unilateral movement', 'Step forward and squat', 'Knee not past toe'),
        ('Bulgarian Split Squats', 'Legs', 'Quadriceps, Glutes', 'Bodyweight', 'Medium',
         'Rear foot elevated', 'One foot on bench behind',
         'Great unilateral exercise'),
        ('Leg Extensions', 'Legs', 'Quadriceps', 'Machine', 'Easy',
         'Quad isolation', 'Extend legs seated', 'Control negative phase'),
        ('Romanian Deadlift', 'Legs', 'Hamstrings, Glutes', 'Barbell', 'Medium',
         'Best hamstring exercise', 'Lower to mid-shin', 'Feel hamstring stretch'),
        ('Lying Leg Curls', 'Legs', 'Hamstrings', 'Machine', 'Easy',
         'Hamstring isolation', 'Curl to glutes', 'Control movement'),
        ('Glute Bridge', 'Legs', 'Glutes', 'Bodyweight', 'Easy',
         'Glute isolation', 'Lift hips lying back', 'Squeeze glutes at top'),
        ('Standing Calf Raises', 'Legs', 'Calves', 'Machine', 'Easy',
         'Basic calf exercise', 'Rise up on toes', 'Full range of motion'),
    ]
    
    for ex in exercises:
        db.add_exercise(*ex)
    
    logger.info(f"✅ Added {len(exercises)} leg exercises")


def initialize_ab_exercises(db):
    """Add ab exercises"""
    logger.info("📦 Adding ab exercises...")
    
    exercises = [
        ('Crunches', 'Abs', 'Rectus Abdominis', 'Bodyweight', 'Easy',
         'Classic ab exercise', 'Lift shoulders to pelvis', 'Don\'t pull on neck'),
        ('Plank', 'Abs', 'Rectus Abdominis', 'Bodyweight', 'Medium',
         'Static hold', 'Keep body straight', 'Breathe evenly'),
        ('Side Plank', 'Abs', 'Obliques', 'Bodyweight', 'Medium',
         'For obliques', 'Lie on side, lift hips up', 'Keep body aligned'),
        ('Russian Twists', 'Abs', 'Obliques', 'Bodyweight', 'Medium',
         'Rotational movement', 'Seated torso rotation', 'Can add weight'),
        ('Bicycle Crunches', 'Abs', 'Rectus and Obliques', 'Bodyweight', 'Medium',
         'Pedaling motion', 'Elbow to opposite knee', 'Continuous motion'),
        ('Hanging Knee Raises', 'Abs', 'Lower Abs', 'Pull-up Bar', 'Hard',
         'Hanging from bar', 'Raise knees to chest', 'Don\'t swing'),
        ('Hanging Leg Raises', 'Abs', 'Lower Abs', 'Pull-up Bar', 'Hard',
         'More difficult version', 'Raise straight legs', 'High difficulty level'),
        ('Mountain Climbers', 'Abs', 'Core, Cardio', 'Bodyweight', 'Medium',
         'Dynamic exercise', 'Running motion in plank', 'High tempo'),
        ('V-ups', 'Abs', 'Full Abs', 'Bodyweight', 'Hard',
         'Simultaneous leg and torso raise', 'Fold into V-shape',
         'Requires coordination'),
        ('Cable Crunches', 'Abs', 'Rectus Abdominis', 'Cables', 'Medium',
         'Cable resistance', 'Kneeling pull handle down', 'Constant resistance'),
    ]
    
    for ex in exercises:
        db.add_exercise(*ex)
    
    logger.info(f"✅ Added {len(exercises)} ab exercises")


def initialize_cardio_exercises(db):
    """Add cardio exercises"""
    logger.info("📦 Adding cardio exercises...")
    
    exercises = [
        ('Burpees', 'Cardio', 'Full Body', 'Bodyweight', 'Hard',
         'Complex functional movement', 'Squat-plank-pushup-jump',
         'High intensity exercise'),
        ('Jump Rope', 'Cardio', 'Cardiovascular, Calves', 'Jump Rope', 'Medium',
         'Great cardio with coordination', 'Jump over rotating rope',
         'Develops coordination and endurance'),
        ('High Knees', 'Cardio', 'Cardiovascular, Legs', 'Bodyweight', 'Medium',
         'Running with high knee lift', 'Lift knees to chest', 'Fast execution pace'),
        ('Butt Kicks', 'Cardio', 'Cardiovascular, Hamstrings', 'Bodyweight', 'Medium',
         'Heels to glutes', 'Touch heels to glutes', 'Activates hamstrings'),
        ('Jumping Jacks', 'Cardio', 'Cardiovascular System', 'Bodyweight', 'Easy',
         'Classic aerobic exercise', 'Jumps spreading arms and legs',
         'Good for warm-up'),
        ('Box Jumps', 'Cardio', 'Legs, Explosive Power', 'Plyo Box', 'Medium',
         'Jumps onto platform', 'Jump onto box', 'Land softly'),
        ('Sprint in Place', 'Cardio', 'Cardiovascular System', 'Bodyweight', 'Hard',
         'Maximum intensity', 'Run at maximum speed',
         'Short high intensity intervals'),
        ('Star Jumps', 'Cardio', 'Full Body', 'Bodyweight', 'Medium',
         'Jumps with limb spreading', 'Jump in star shape',
         'Arms and legs spread'),
        ('Bear Crawl', 'Cardio', 'Full Body, Core', 'Bodyweight', 'Hard',
         'Quadruped movement', 'Crawl on hands and feet',
         'Knees don\'t touch floor'),
        ('Tuck Jumps', 'Cardio', 'Legs, Explosive Power', 'Bodyweight', 'Hard',
         'Grouping in jump', 'Pull knees to chest in jump',
         'High intensity plyo'),
    ]
    
    for ex in exercises:
        db.add_exercise(*ex)
    
    logger.info(f"✅ Added {len(exercises)} cardio exercises")


def initialize_functional_exercises(db):
    """Add functional exercises"""
    logger.info("📦 Adding functional exercises...")
    
    exercises = [
        ('Turkish Get-up', 'Functional', 'Full Body', 'Kettlebells', 'Hard',
         'Complex functional movement', 'Rising from floor with weight',
         'Develops coordination and stability'),
        ('Farmer\'s Walk', 'Functional', 'Forearms, Core, Legs', 'Dumbbells', 'Medium',
         'Walking with weights', 'Heavy dumbbells in hands',
         'Builds functional strength'),
        ('Sled Push', 'Functional', 'Legs, Core', 'Sled', 'Hard',
         'Heavy sled pushing', 'Push sled in front', 'Explosive leg power'),
        ('Sled Pull', 'Functional', 'Full Body', 'Sled', 'Hard',
         'Heavy sled pulling', 'Pull loaded sled behind',
         'Functional strength endurance'),
        ('Rope Climb', 'Functional', 'Back, Arms', 'Rope', 'Hard',
         'Vertical rope climbing', 'Climb up the rope',
         'Functional upper body strength'),
        ('Overhead Carry', 'Functional', 'Shoulders, Core', 'Dumbbells', 'Hard',
         'Walking with weight overhead', 'Hold overhead and walk',
         'Great shoulder stabilization'),
        ('Kettlebell Swings', 'Functional', 'Glutes, Hamstrings', 'Kettlebells', 'Medium',
         'Ballistic movement', 'Swing from hips', 'Powerful hip extension'),
        ('Sandbag Lift', 'Functional', 'Full Body', 'Sandbag', 'Hard',
         'Awkward object lifting', 'Lift sandbag various ways',
         'Mimics real-world movements'),
        ('Battle Ropes', 'Functional', 'Arms, Core', 'Battle Ropes', 'Medium',
         'Wave generation', 'Create waves with ropes',
         'Full body conditioning'),
        ('Medicine Ball Slams', 'Functional', 'Core, Shoulders', 'Medicine Ball', 'Medium',
         'Overhead slam', 'Lift and slam ball down', 'Explosive core work'),
    ]
    
    for ex in exercises:
        db.add_exercise(*ex)
    
    logger.info(f"✅ Added {len(exercises)} functional exercises")


def initialize_stretching_exercises(db):
    """Add stretching exercises"""
    logger.info("📦 Adding stretching exercises...")
    
    exercises = [
        ('Forward Fold', 'Stretching', 'Hamstrings', 'Bodyweight', 'Easy',
         'Hamstring stretch', 'Bend toward legs from standing', 'Keep back straight'),
        ('Downward Dog', 'Stretching', 'Full Body', 'Bodyweight', 'Easy',
         'Classic yoga pose', 'Support on hands and feet, hips up',
         'Stretches entire posterior chain'),
        ('Child\'s Pose', 'Stretching', 'Back, Shoulders', 'Bodyweight', 'Easy',
         'Relaxing pose', 'Sit on heels, arms forward', 'Great resting pose'),
        ('Quad Stretch', 'Stretching', 'Quadriceps', 'Bodyweight', 'Easy',
         'Front thigh stretch', 'Bend leg back and pull', 'Hold heel to glute'),
        ('Pigeon Pose', 'Stretching', 'Hips, Glutes', 'Bodyweight', 'Medium',
         'Deep hip stretch', 'One leg bent in front', 'Great stretch for runners'),
        ('Cat-Cow', 'Stretching', 'Spine', 'Bodyweight', 'Easy',
         'Spine mobilization', 'On all fours arch and round back',
         'Improves back mobility'),
        ('Spinal Twist', 'Stretching', 'Spine, Obliques', 'Bodyweight', 'Easy',
         'Rotational stretch', 'Seated rotate torso', 'Improves spine rotation'),
        ('Chest Stretch', 'Stretching', 'Chest Muscles', 'Bodyweight', 'Easy',
         'Front body stretch', 'Brace arm against doorway',
         'Counteracts slouching'),
        ('Calf Stretch', 'Stretching', 'Calf Muscles', 'Bodyweight', 'Easy',
         'Lower leg stretch', 'Push against wall and stretch',
         'Important for runners'),
        ('Shoulder Stretch', 'Stretching', 'Shoulders', 'Bodyweight', 'Easy',
         'Shoulder flexibility', 'Pull arm across body', 'Hold for 20-30 seconds'),
    ]
    
    for ex in exercises:
        db.add_exercise(*ex)
    
    logger.info(f"✅ Added {len(exercises)} stretching exercises")


# ============================================================================
# MAIN INITIALIZATION FUNCTION
# ============================================================================

def initialize_all_exercise_categories(db):
    """
    Single entry point to initialize all exercise categories.
    This function is called by ExerciseDatabase.auto_initialize_if_empty()
    """
    logger.info("🚀 Starting exercise database initialization...")
    
    # Clear existing exercises
    logger.info("🧹 Clearing existing exercises...")
    db.clear_database()
    
    # Add all exercise categories
    initialize_chest_exercises(db)
    initialize_back_exercises(db)
    initialize_shoulder_exercises(db)
    initialize_arm_exercises(db)
    initialize_leg_exercises(db)
    initialize_ab_exercises(db)
    initialize_cardio_exercises(db)
    initialize_functional_exercises(db)
    initialize_stretching_exercises(db)
    
    logger.info("✅ Exercise database initialization complete!")


# ============================================================================
# STANDALONE SCRIPT EXECUTION
# ============================================================================

if __name__ == "__main__":
    """
    Run this script standalone to manually initialize the database:
    python -m bot.features.dev2_exercise_library.initialize_exercises
    """
    import sys
    from pathlib import Path
    
    # Add project root to path
    ROOT_DIR = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(ROOT_DIR))
    
    from bot.features.dev2_exercise_library.exercise_db import ExerciseDatabase
    
    db = ExerciseDatabase()
    initialize_all_exercise_categories(db)
    
    # Show final stats
    stats = db.get_database_stats()
    print(f"\n📊 Final Statistics:")
    print(f"   Total exercises: {stats['total_exercises']}")
    print(f"   Muscle groups: {stats['muscle_groups']}")
    print(f"   Equipment types: {stats['equipment_types']}")
    print(f"   Difficulty levels: {stats['difficulty_levels']}")
    print(f"\n🤖 Exercise library is ready to use!")