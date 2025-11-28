"""
Business logic for timer functionality.
All database operations for timers.
"""
from datetime import datetime
from typing import Optional

from bot.core.models import TimerPreset, User
from bot.core.database import get_session


# ==========================================
# TIMER PRESETS CRUD
# ==========================================

def add_timer_preset(
    telegram_id: int,
    name: str,
    hours: int,
    minutes: int,
    seconds: int
) -> TimerPreset:
    """Create a new timer preset"""
    with get_session() as session:
        preset = TimerPreset(
            user_id=telegram_id,
            name=name,
            hours=hours,
            minutes=minutes,
            seconds=seconds
        )
        session.add(preset)
        session.commit()
        session.refresh(preset)
        return preset


def get_user_timer_presets(telegram_id: int) -> list[TimerPreset]:
    """Get all timer presets for a user"""
    with get_session() as session:
        presets = (
            session.query(TimerPreset)
            .filter(TimerPreset.user_id == telegram_id)
            .order_by(TimerPreset.created_at.desc())
            .all()
        )
        return presets


def get_timer_preset_by_id(preset_id: int) -> Optional[TimerPreset]:
    """Get a specific timer preset by ID"""
    with get_session() as session:
        preset = (
            session.query(TimerPreset)
            .filter(TimerPreset.timer_preset_id == preset_id)
            .first()
        )
        return preset


def delete_timer_preset(preset_id: int) -> bool:
    """Delete a timer preset"""
    with get_session() as session:
        preset = session.query(TimerPreset).filter(TimerPreset.timer_preset_id == preset_id).first()
        if preset:
            session.delete(preset)
            session.commit()
            return True
        return False


def update_timer_preset(
    preset_id: int,
    name: str,
    hours: int,
    minutes: int,
    seconds: int
) -> Optional[TimerPreset]:
    """Update an existing timer preset"""
    with get_session() as session:
        preset = session.query(TimerPreset).filter(TimerPreset.timer_preset_id == preset_id).first()
        if preset:
            preset.name = name
            preset.hours = hours
            preset.minutes = minutes
            preset.seconds = seconds
            session.commit()
            session.refresh(preset)
            return preset
        return None


# ==========================================
# VALIDATION HELPERS
# ==========================================

def validate_time_values(hours: int, minutes: int, seconds: int) -> tuple[bool, str]:
    """
    Validate timer time values.
    Returns: (is_valid, error_message)
    """
    if hours < 0 or minutes < 0 or seconds < 0:
        return False, "❌ Time values cannot be negative!"
    
    if hours == 0 and minutes == 0 and seconds == 0:
        return False, "❌ Timer duration must be greater than 0!"
    
    if minutes > 59:
        return False, "❌ Minutes must be between 0 and 59!"
    
    if seconds > 59:
        return False, "❌ Seconds must be between 0 and 59!"
    
    total_seconds = hours * 3600 + minutes * 60 + seconds
    if total_seconds > 86400:  # 24 hours
        return False, "❌ Timer cannot exceed 24 hours!"
    
    return True, ""


def parse_time_string(time_str: str) -> tuple[Optional[tuple[int, int, int]], str]:
    """
    Parse time string in format HH:MM:SS, MM:SS, or SS
    Returns: ((hours, minutes, seconds), error_message)
    """
    try:
        parts = time_str.strip().split(':')
        
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
        elif len(parts) == 2:
            hours = 0
            minutes, seconds = map(int, parts)
        elif len(parts) == 1:
            hours = 0
            minutes = 0
            seconds = int(parts[0])
        else:
            return None, "❌ Invalid format! Use HH:MM:SS, MM:SS, or SS"
        
        is_valid, error_msg = validate_time_values(hours, minutes, seconds)
        if not is_valid:
            return None, error_msg
        
        return (hours, minutes, seconds), ""
    
    except ValueError:
        return None, "❌ Invalid format! Use numbers only (e.g., 8:00 or 0:8:0)"


def format_time_display(hours: int, minutes: int, seconds: int) -> str:
    """Format time for display"""
    return f"{hours}h {minutes}m {seconds}s"