#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exercise Database Service for Dev2 Exercise Library
Uses the unified SQLAlchemy database with ORM models
"""

import logging
from typing import List, Dict, Optional
from sqlalchemy import select, func, distinct
from sqlalchemy.exc import SQLAlchemyError

from bot.core.database import get_session
from bot.core.models import Exercise

logger = logging.getLogger(__name__)


class ExerciseDatabase:
    """
    Exercise database service using SQLAlchemy ORM.
    All operations use the unified database connection.
    """

    def get_all_exercises(self) -> List[Dict]:
        """Get all exercises"""
        try:
            with get_session() as session:
                stmt = select(Exercise).order_by(Exercise.name)
                result = session.execute(stmt)
                exercises = result.scalars().all()
                return [self._exercise_to_dict(ex) for ex in exercises]
        except SQLAlchemyError as e:
            logger.error(f"Error fetching exercises: {e}")
            return []

    def get_exercises_by_filter(
        self,
        muscle_group: Optional[str] = None,
        muscle: Optional[str] = None,
        equipment: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> List[Dict]:
        """Filter exercises by multiple criteria"""
        try:
            with get_session() as session:
                stmt = select(Exercise)
                
                # Apply filters
                if muscle_group:
                    stmt = stmt.where(Exercise.muscle_group == muscle_group)
                if muscle:
                    stmt = stmt.where(Exercise.muscle == muscle)
                if equipment:
                    stmt = stmt.where(Exercise.equipment == equipment)
                if difficulty:
                    stmt = stmt.where(Exercise.difficulty == difficulty)
                
                stmt = stmt.order_by(Exercise.name)
                result = session.execute(stmt)
                exercises = result.scalars().all()
                return [self._exercise_to_dict(ex) for ex in exercises]
        except SQLAlchemyError as e:
            logger.error(f"Error filtering exercises: {e}")
            return []

    def get_unique_values(self, field: str) -> List[str]:
        """Get unique values for a given field"""
        try:
            with get_session() as session:
                # Map field names to Exercise model attributes
                field_mapping = {
                    'muscle_group': Exercise.muscle_group,
                    'muscle': Exercise.muscle,
                    'equipment': Exercise.equipment,
                    'difficulty': Exercise.difficulty
                }
                
                if field not in field_mapping:
                    logger.error(f"Invalid field: {field}")
                    return []
                
                column = field_mapping[field]
                stmt = select(distinct(column)).where(column.isnot(None)).order_by(column)
                result = session.execute(stmt)
                return [row[0] for row in result]
        except SQLAlchemyError as e:
            logger.error(f"Error fetching unique values: {e}")
            return []

    def get_exercise_by_name(self, name: str) -> Optional[Dict]:
        """Find exercise by exact name"""
        try:
            with get_session() as session:
                stmt = select(Exercise).where(Exercise.name == name)
                result = session.execute(stmt)
                exercise = result.scalar_one_or_none()
                return self._exercise_to_dict(exercise) if exercise else None
        except SQLAlchemyError as e:
            logger.error(f"Error searching exercise: {e}")
            return None

    def search_exercises(self, query: str, limit: int = 10) -> List[Dict]:
        """Search exercises by name with LIKE query"""
        try:
            with get_session() as session:
                # Case-insensitive search
                pattern = f"%{query}%"
                stmt = select(Exercise).where(
                    Exercise.name.ilike(pattern)
                ).order_by(Exercise.name).limit(limit)
                
                result = session.execute(stmt)
                exercises = result.scalars().all()
                return [self._exercise_to_dict(ex) for ex in exercises]
        except SQLAlchemyError as e:
            logger.error(f"Search error: {e}")
            return []

    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        try:
            with get_session() as session:
                # Total exercises
                total_stmt = select(func.count(Exercise.exercise_id))
                total_result = session.execute(total_stmt)
                total_exercises = total_result.scalar()
                
                stats = {
                    'total_exercises': total_exercises or 0,
                    'muscle_groups': len(self.get_unique_values('muscle_group')),
                    'equipment_types': len(self.get_unique_values('equipment')),
                    'difficulty_levels': len(self.get_unique_values('difficulty'))
                }
                
                return stats
        except SQLAlchemyError as e:
            logger.error(f"Error fetching statistics: {e}")
            return {
                'total_exercises': 0,
                'muscle_groups': 0,
                'equipment_types': 0,
                'difficulty_levels': 0
            }

    def add_exercise(
        self,
        name: str,
        muscle_group: str,
        muscle: str,
        equipment: str,
        difficulty: str,
        description: str,
        instructions: str = "",
        tips: str = ""
    ) -> bool:
        """Add a single exercise to database"""
        try:
            with get_session() as session:
                exercise = Exercise(
                    name=name,
                    muscle_group=muscle_group,
                    muscle=muscle,
                    equipment=equipment,
                    difficulty=difficulty,
                    description=description,
                    instructions=instructions or None,
                    tips=tips or None
                )
                session.add(exercise)
                session.commit()
                logger.info(f"Added exercise: {name}")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error adding exercise: {e}")
            return False

    def clear_database(self) -> bool:
        """Clear all exercises from database"""
        try:
            with get_session() as session:
                session.query(Exercise).delete()
                session.commit()
                logger.info("Exercise database cleared")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error clearing database: {e}")
            return False

    def auto_initialize_if_empty(self) -> bool:
        """
        Automatically initialize exercise database if empty.
        Returns True if initialization was performed, False if exercises already exist.
        """
        stats = self.get_database_stats()
        
        if stats['total_exercises'] > 0:
            logger.info(f"📚 Exercise database already initialized ({stats['total_exercises']} exercises)")
            return False
        
        logger.info("🔄 Exercise database is empty. Auto-initializing...")
        
        # Import initialization functions
        from .initialize_exercises import initialize_all_exercise_categories
        
        # Initialize all categories
        initialize_all_exercise_categories(self)
        
        # Show final stats
        final_stats = self.get_database_stats()
        logger.info(f"✅ Exercise database initialized with {final_stats['total_exercises']} exercises")
        
        return True

    @staticmethod
    def _exercise_to_dict(exercise: Exercise) -> Dict:
        """Convert Exercise ORM object to dictionary"""
        if not exercise:
            return {}
        
        return {
            'id': exercise.exercise_id,
            'name': exercise.name,
            'muscle_group': exercise.muscle_group,
            'muscle': exercise.muscle,
            'equipment': exercise.equipment,
            'difficulty': exercise.difficulty,
            'description': exercise.description,
            'instructions': exercise.instructions or '',
            'tips': exercise.tips or '',
            'created_at': exercise.created_at
        }
