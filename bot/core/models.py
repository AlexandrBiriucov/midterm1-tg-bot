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