"""
Unified database models for the entire GymBot project.
All tables are defined here using SQLAlchemy ORM.

STRUCTURE:
- Users table: user_id (BigInteger, primary key, autoincrement) - separate from telegram_id
- Each table has uniquely named primary key: exercise_id, workout_id, etc.
- Foreign keys reference users.user_id
"""
from datetime import datetime, timezone, date as date_type, time as time_type
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, Float, ForeignKey, Text, Index, JSON, Date, Time, BigInteger


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


# ============================================================================
# USER MODEL - Core user management
# ============================================================================

class User(Base):
    """Central user model - used across all features"""
    __tablename__ = "users"

    # user_id as auto-incrementing primary key (1, 2, 3, ...)
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # User information
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # Settings
    language: Mapped[str] = mapped_column(String(10), default="en")
    timezone_offset: Mapped[int] = mapped_column(Integer, default=0)
    
    # Statistics
    workout_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    workouts: Mapped[list["Workout"]] = relationship(
        "Workout", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    custom_routines: Mapped[list["CustomRoutine"]] = relationship(
        "CustomRoutine",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    timer_presets: Mapped[list["TimerPreset"]] = relationship(
        "TimerPreset",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    nutrition_goals: Mapped["NutritionGoal | None"] = relationship(
        "NutritionGoal",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    nutrition_meals: Mapped[list["NutritionMeal"]] = relationship(
        "NutritionMeal",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    training_notifications: Mapped[list["TrainingNotification"]] = relationship(
        "TrainingNotification",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(user_id={self.user_id}, telegram_id={self.telegram_id}, username={self.username})>"

# ============================================================================
# WORKOUT TRACKING MODELS - Dev1 feature
# ============================================================================

class Workout(Base):
    """Workout log entry"""
    __tablename__ = "workouts"

    workout_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    
    # Exercise data
    exercise: Mapped[str] = mapped_column(String(100), index=True)
    sets: Mapped[int] = mapped_column(Integer)
    reps: Mapped[int] = mapped_column(Integer)
    weight: Mapped[float] = mapped_column(Float)
    
    # Optional: Link to routine
    routine_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("custom_routines.routine_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Optional: Link to exercise library
    exercise_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("exercises.exercise_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="workouts")
    routine: Mapped["CustomRoutine | None"] = relationship(
        "CustomRoutine",
        back_populates="workouts"
    )
    exercise_ref: Mapped["Exercise | None"] = relationship(
        "Exercise",
        back_populates="workout_logs"
    )

    def __repr__(self):
        return f"<Workout(workout_id={self.workout_id}, exercise={self.exercise}, {self.sets}x{self.reps}x{self.weight}kg)>"
# ============================================================================
# EXERCISE LIBRARY MODELS - Dev2 feature
# ============================================================================

class Exercise(Base):
    """Exercise library - comprehensive exercise database"""
    __tablename__ = "exercises"
    
    exercise_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    muscle_group: Mapped[str] = mapped_column(String(100), nullable=False)
    muscle: Mapped[str] = mapped_column(String(100), nullable=False)
    equipment: Mapped[str] = mapped_column(String(100), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    tips: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    
    # Relationships
    workout_logs: Mapped[list["Workout"]] = relationship(
        "Workout",
        back_populates="exercise_ref"
    )
    
    # Indexes for fast filtering
    __table_args__ = (
        Index('idx_muscle_group', 'muscle_group'),
        Index('idx_equipment', 'equipment'),
        Index('idx_difficulty', 'difficulty'),
        Index('idx_muscle', 'muscle'),
    )

    def __repr__(self):
        return f"<Exercise(exercise_id={self.exercise_id}, name={self.name}, muscle_group={self.muscle_group})>"

    
# ============================================================================
# CUSTOM ROUTINES MODELS - Dev4 feature
# ============================================================================

class CustomRoutine(Base):
    """User's custom workout routines"""
    __tablename__ = "custom_routines"
    
    routine_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    
    # Routine info
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    schedule: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Exercise list stored as JSON
    exercises: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Metadata
    is_preset: Mapped[bool] = mapped_column(Integer, default=0)
    times_used: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="custom_routines")
    workouts: Mapped[list["Workout"]] = relationship(
        "Workout",
        back_populates="routine"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_user_routines', 'user_id'),
        Index('idx_routine_level', 'level'),
    )

    def __repr__(self):
        return f"<CustomRoutine(routine_id={self.routine_id}, name={self.name}, user_id={self.user_id})>"

# ============================================================================
# REST TIMER MODELS - Dev5 feature
# ============================================================================

class TimerPreset(Base):
    """User's custom timer presets"""
    __tablename__ = "timer_presets"
    
    timer_preset_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    
    # Preset info
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    hours: Mapped[int] = mapped_column(Integer, default=0)
    minutes: Mapped[int] = mapped_column(Integer, default=0)
    seconds: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="timer_presets")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_timer_presets', 'user_id'),
    )
    
    def total_seconds(self) -> int:
        """Calculate total duration in seconds"""
        return self.hours * 3600 + self.minutes * 60 + self.seconds
    
    def __repr__(self):
        return f"<TimerPreset(timer_preset_id={self.timer_preset_id}, name={self.name}, {self.hours}h {self.minutes}m {self.seconds}s)>"
    
    # ============================================================================
# NUTRITION TRACKING MODELS - Dev7 feature
# ============================================================================

class NutritionGoal(Base):
    """User's daily nutrition goals"""
    __tablename__ = "nutrition_goals"
    
    nutrition_goal_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False
    )
    
    # Daily nutrition targets
    daily_calories: Mapped[float] = mapped_column(Float, nullable=False)
    daily_protein: Mapped[float] = mapped_column(Float, nullable=False)
    daily_carbs: Mapped[float] = mapped_column(Float, nullable=False)
    daily_fat: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Optional: Store calculation metadata
    bmr: Mapped[float | None] = mapped_column(Float, nullable=True)
    tdee: Mapped[float | None] = mapped_column(Float, nullable=True)
    goal_type: Mapped[str | None] = mapped_column(String(20), nullable=True)  # loss/maintain/gain
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="nutrition_goals")
    
    def __repr__(self):
        return f"<NutritionGoal(nutrition_goal_id={self.nutrition_goal_id}, user_id={self.user_id}, calories={self.daily_calories})>"


class FoodCache(Base):
    """Cache for USDA food data to reduce API calls"""
    __tablename__ = "food_cache"
    
    food_cache_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fdc_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    
    # Nutrition per 100g
    calories_per_100g: Mapped[float] = mapped_column(Float, default=0)
    protein_per_100g: Mapped[float] = mapped_column(Float, default=0)
    carbs_per_100g: Mapped[float] = mapped_column(Float, default=0)
    fat_per_100g: Mapped[float] = mapped_column(Float, default=0)
    fiber_per_100g: Mapped[float | None] = mapped_column(Float, nullable=True)
    sodium_per_100g: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Timestamp
    cached_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    
    # Relationships
    nutrition_meals: Mapped[list["NutritionMeal"]] = relationship(
        "NutritionMeal",
        back_populates="food_cache"
    )
    
    def __repr__(self):
        return f"<FoodCache(food_cache_id={self.food_cache_id}, fdc_id={self.fdc_id}, name={self.name})>"


class NutritionMeal(Base):
    """Daily meal log entries"""
    __tablename__ = "nutrition_meals"
    
    nutrition_meal_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    
    # Meal info
    date: Mapped[date_type] = mapped_column(Date, index=True, nullable=False)
    meal_type: Mapped[str] = mapped_column(String(20), nullable=False)  # breakfast/lunch/dinner/snack
    
    # Food data (reference to cache)
    food_cache_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("food_cache.food_cache_id", ondelete="CASCADE"),
        nullable=False
    )
    fdc_id: Mapped[int] = mapped_column(Integer, nullable=False)
    food_name: Mapped[str] = mapped_column(String(300), nullable=False)
    portion_grams: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Calculated nutrition for this portion
    calories: Mapped[float] = mapped_column(Float, nullable=False)
    protein: Mapped[float] = mapped_column(Float, nullable=False)
    carbs: Mapped[float] = mapped_column(Float, nullable=False)
    fat: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Timestamp
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="nutrition_meals")
    food_cache: Mapped["FoodCache"] = relationship(
        "FoodCache",
        back_populates="nutrition_meals"
    )
    
    # Indexes for efficient queries
    __table_args__ = (
        Index('idx_user_date', 'user_id', 'date'),
        Index('idx_user_meal_type', 'user_id', 'meal_type'),
    )
    
    def __repr__(self):
        return f"<NutritionMeal(nutrition_meal_id={self.nutrition_meal_id}, user_id={self.user_id}, food={self.food_name}, {self.portion_grams}g)>"

# ============================================================================
# TRAINING NOTIFICATIONS MODEL - Dev8 feature
# ============================================================================

class TrainingNotification(Base):
    """Scheduled training notifications"""
    __tablename__ = "training_notifications"
    
    notification_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    
    # Schedule info
    weekday: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    hour: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-23
    minute: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-59
    reminder_minutes: Mapped[int] = mapped_column(Integer, nullable=False)  # Minutes before training
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="training_notifications")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_notifications', 'user_id'),
        Index('idx_weekday', 'weekday'),
    )
    
    def get_time(self) -> time_type:
        """Get time object from hour and minute"""
        return time_type(self.hour, self.minute)
    
    def __repr__(self):
        return f"<TrainingNotification(notification_id={self.notification_id}, user_id={self.user_id}, weekday={self.weekday}, {self.hour:02d}:{self.minute:02d})>"
