import sqlite3
import json

class RoutineDatabase:
    def __init__(self, db_path='fitness_bot.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Инициализация таблиц для routines"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_routines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                routine_name TEXT,
                routine_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Routine database initialized")
    
    def save_custom_routine(self, user_id, routine_name, routine_data):
        """Сохранение кастомной routine"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO custom_routines (user_id, routine_name, routine_data) VALUES (?, ?, ?)',
            (user_id, routine_name, json.dumps(routine_data))
        )
        
        conn.commit()
        conn.close()
        return True
    
    def get_user_routines(self, user_id):
        """Получение всех routines пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT routine_name, routine_data FROM custom_routines WHERE user_id = ?',
            (user_id,)
        )
        
        routines = cursor.fetchall()
        conn.close()
        
        result = []
        for name, data in routines:
            result.append({
                'name': name,
                'data': json.loads(data)
            })
        
        return result
    
    def delete_routine(self, user_id, routine_name):
        """Удаление routine"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'DELETE FROM custom_routines WHERE user_id = ? AND routine_name = ?',
            (user_id, routine_name)
        )
        
        conn.commit()
        conn.close()
        return True

# Создаем глобальный экземпляр базы данных
routine_db = RoutineDatabase()