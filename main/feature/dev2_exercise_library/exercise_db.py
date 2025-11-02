#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exercise Database Manager for Dev2 Exercise Library
SQLite-based exercise database management
"""

import sqlite3
import logging
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Database file path - stored in feature directory
DB_FILE = Path(__file__).parent / "exercises.db"


class ExerciseDatabase:
    """SQLite database management for exercises"""

    def __init__(self, db_file=DB_FILE):
        self.db_file = db_file
        self._create_database()
        self._test_connection()

    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_file)

    def _create_database(self):
        """Create database structure if it doesn't exist"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                muscle_group TEXT NOT NULL,
                muscle TEXT NOT NULL,
                equipment TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                description TEXT NOT NULL,
                instructions TEXT,
                tips TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_muscle_group ON exercises(muscle_group)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_equipment ON exercises(equipment)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_difficulty ON exercises(difficulty)")

        conn.commit()
        conn.close()

    def _test_connection(self):
        """Test database connection"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM exercises")
            count = cursor.fetchone()[0]
            conn.close()
            logger.info(f"✅ Exercise database connected: {count} exercises")

            if count == 0:
                logger.warning("⚠️ Exercise database is empty! Run initialize_exercises.py to populate it.")
        except Exception as e:
            logger.error(f"❌ Exercise database connection error: {e}")
            raise

    def get_all_exercises(self) -> List[Dict]:
        """Get all exercises"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM exercises ORDER BY name')
            columns = [description[0] for description in cursor.description]
            exercises = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return exercises
        except Exception as e:
            logger.error(f"Error fetching exercises: {e}")
            return []
        finally:
            conn.close()

    def get_exercises_by_filter(self, muscle_group=None, muscle=None,
                                equipment=None, difficulty=None) -> List[Dict]:
        """Filter exercises"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            query = "SELECT * FROM exercises WHERE 1=1"
            params = []

            if muscle_group:
                query += " AND muscle_group = ?"
                params.append(muscle_group)

            if muscle:
                query += " AND muscle = ?"
                params.append(muscle)

            if equipment:
                query += " AND equipment = ?"
                params.append(equipment)

            if difficulty:
                query += " AND difficulty = ?"
                params.append(difficulty)

            query += " ORDER BY name"

            cursor.execute(query, params)
            columns = [description[0] for description in cursor.description]
            exercises = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return exercises
        except Exception as e:
            logger.error(f"Error filtering exercises: {e}")
            return []
        finally:
            conn.close()

    def get_unique_values(self, field: str) -> List[str]:
        """Get unique field values"""
        conn = self._get_connection()
        cursor = conn.cursor()

        
        try:
            cursor.execute(f'SELECT DISTINCT {field} FROM exercises WHERE {field} IS NOT NULL ORDER BY {field}')
            values = [row[0] for row in cursor.fetchall()]
            return values
        except Exception as e:
            logger.error(f"Error fetching unique values: {e}")
            return []
        finally:
            conn.close()

    def get_exercise_by_name(self, name: str) -> Optional[Dict]:
        """Find exercise by name"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM exercises WHERE name = ?', (name,))
            row = cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
        except Exception as e:
            logger.error(f"Error searching exercise: {e}")
            return None
        finally:
            conn.close()

    def search_exercises(self, query: str, limit: int = 10) -> List[Dict]:
        """Search exercises by name"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM exercises 
                WHERE name LIKE ? 
                ORDER BY 
                    CASE 
                        WHEN name LIKE ? THEN 1
                        WHEN name LIKE ? THEN 2
                        ELSE 3
                    END
                LIMIT ?
            """, (f'%{query}%', f'{query}%', f'%{query}', limit))

            columns = [description[0] for description in cursor.description]
            exercises = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return exercises
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
        finally:
            conn.close()

    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT COUNT(*) FROM exercises")
            total_exercises = cursor.fetchone()[0]

            stats = {
                'total_exercises': total_exercises,
                'muscle_groups': len(self.get_unique_values('muscle_group')),
                'equipment_types': len(self.get_unique_values('equipment')),
                'difficulty_levels': len(self.get_unique_values('difficulty'))
            }

            return stats
        except Exception as e:
            logger.error(f"Error fetching statistics: {e}")
            return {
                'total_exercises': 0,
                'muscle_groups': 0,
                'equipment_types': 0,
                'difficulty_levels': 0
            }
        finally:
            conn.close()

    def add_exercise(self, name: str, muscle_group: str, muscle: str, 
                     equipment: str, difficulty: str, description: str, 
                     instructions: str = "", tips: str = ""):
        """Add a single exercise to database"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO exercises (name, muscle_group, muscle, equipment, difficulty, 
                                     description, instructions, tips)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, muscle_group, muscle, equipment, difficulty,
                  description, instructions, tips))
            conn.commit()
            logger.info(f"Added exercise: {name}")
        except Exception as e:
            logger.error(f"Error adding exercise: {e}")
        finally:
            conn.close()

    def clear_database(self):
        """Clear all exercises from database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM exercises")
            conn.commit()
            logger.info("Database cleared")
        except Exception as e:
            logger.error(f"Error clearing database: {e}")
        finally:
            conn.close()
