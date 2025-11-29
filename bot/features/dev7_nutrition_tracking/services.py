import aiohttp
import logging
import sqlite3
from datetime import date
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Configuration
USDA_API_KEY = "3X3lZVkwbI7csqXUY0fOxkKm1bdBN8OeJSwZX74y"
USDA_BASE_URL = "https://api.nal.usda.gov/fdc/v1"


class NutritionCalculator:
    """Calculate nutritional needs based on user parameters"""
    
    @staticmethod
    def calculate_bmr(gender: str, weight_kg: float, height_cm: float, age: int) -> float:
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation"""
        if gender.lower() == "male":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:  # female
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        return bmr
    
    @staticmethod
    def calculate_tdee(bmr: float, activity_multiplier: float) -> float:
        """Calculate Total Daily Energy Expenditure"""
        return bmr * activity_multiplier
    
    @staticmethod
    def calculate_macros(calories: float, goal_type: str, weight_kg: float) -> Dict[str, float]:
        """Calculate macro distribution based on goal"""
        # Protein: 1.6-2.2g per kg body weight (higher for weight loss)
        if goal_type == "loss":
            protein = weight_kg * 2.0
            # Higher protein, lower carbs for weight loss
            protein_cals = protein * 4
            fat_cals = calories * 0.30  # 30% from fat
            carb_cals = calories - protein_cals - fat_cals
        elif goal_type == "gain":
            protein = weight_kg * 1.8
            # Moderate protein, higher carbs for weight gain
            protein_cals = protein * 4
            fat_cals = calories * 0.25  # 25% from fat
            carb_cals = calories - protein_cals - fat_cals
        else:  # maintain
            protein = weight_kg * 1.6
            # Balanced macro split
            protein_cals = protein * 4
            fat_cals = calories * 0.30  # 30% from fat
            carb_cals = calories - protein_cals - fat_cals
        
        return {
            "protein": protein,
            "carbs": carb_cals / 4,  # 4 calories per gram
            "fat": fat_cals / 9  # 9 calories per gram
        }
    
    @staticmethod
    def calculate_goals(gender: str, age: int, weight_kg: float, height_cm: float, 
                       activity_multiplier: float, goal_type: str) -> Dict[str, float]:
        """Calculate complete nutritional goals"""
        bmr = NutritionCalculator.calculate_bmr(gender, weight_kg, height_cm, age)
        tdee = NutritionCalculator.calculate_tdee(bmr, activity_multiplier)
        
        # Adjust calories based on goal
        if goal_type == "loss":
            target_calories = tdee - 500  # 500 calorie deficit
        elif goal_type == "gain":
            target_calories = tdee + 300  # 300 calorie surplus
        else:  # maintain
            target_calories = tdee
        
        macros = NutritionCalculator.calculate_macros(target_calories, goal_type, weight_kg)
        
        return {
            "calories": target_calories,
            "protein": macros["protein"],
            "carbs": macros["carbs"],
            "fat": macros["fat"],
            "bmr": bmr,
            "tdee": tdee
        }


class DatabaseManager:
    def __init__(self, db_path="nutrition_tracker.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with necessary tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nutrition_users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Food database table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS foods (
                fdc_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                calories_per_100g REAL,
                protein_per_100g REAL,
                carbs_per_100g REAL,
                fat_per_100g REAL,
                fiber_per_100g REAL,
                sodium_per_100g REAL,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User goals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nutrition_user_goals (
                user_id INTEGER PRIMARY KEY,
                daily_calories REAL,
                daily_protein REAL,
                daily_carbs REAL,
                daily_fat REAL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES nutrition_users (user_id)
            )
        ''')
        
        # Daily meals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nutrition_meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date DATE,
                meal_type TEXT,
                fdc_id INTEGER,
                food_name TEXT,
                portion_grams REAL,
                calories REAL,
                protein REAL,
                carbs REAL,
                fat REAL,
                logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES nutrition_users (user_id),
                FOREIGN KEY (fdc_id) REFERENCES foods (fdc_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id: int, username: str = None):
        """Add new user to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO nutrition_users (user_id, username) 
            VALUES (?, ?)
        ''', (user_id, username))
        conn.commit()
        conn.close()
    
    def cache_food(self, food_data: dict):
        """Cache food data in local database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        fdc_id = food_data.get('fdc_id')
        name = food_data.get('name')
        
        cursor.execute('''
            INSERT OR REPLACE INTO foods 
            (fdc_id, name, calories_per_100g, protein_per_100g, carbs_per_100g, 
             fat_per_100g, fiber_per_100g, sodium_per_100g)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            fdc_id, name, food_data.get('calories', 0),
            food_data.get('protein', 0), food_data.get('carbs', 0),
            food_data.get('fat', 0), food_data.get('fiber', 0),
            food_data.get('sodium', 0)
        ))
        
        conn.commit()
        conn.close()
    
    def get_cached_food(self, fdc_id: int) -> Optional[dict]:
        """Get cached food data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM foods WHERE fdc_id = ?', (fdc_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'fdc_id': result[0],
                'name': result[1],
                'calories': result[2],
                'protein': result[3],
                'carbs': result[4],
                'fat': result[5],
                'fiber': result[6],
                'sodium': result[7]
            }
        return None
    
    def set_user_goals(self, user_id: int, calories: float, protein: float, carbs: float, fat: float):
        """Set user's daily nutrition goals"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO nutrition_user_goals 
            (user_id, daily_calories, daily_protein, daily_carbs, daily_fat)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, calories, protein, carbs, fat))
        conn.commit()
        conn.close()
    
    def get_user_goals(self, user_id: int) -> Optional[dict]:
        """Get user's daily nutrition goals"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM nutrition_user_goals WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'calories': result[1],
                'protein': result[2],
                'carbs': result[3],
                'fat': result[4]
            }
        return None
    
    def log_meal(self, user_id: int, meal_type: str, fdc_id: int, food_name: str, 
                 portion_grams: float, calories: float, protein: float, carbs: float, fat: float):
        """Log a meal entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        today = date.today()
        
        cursor.execute('''
            INSERT INTO nutrition_meals 
            (user_id, date, meal_type, fdc_id, food_name, portion_grams, 
             calories, protein, carbs, fat)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, today, meal_type, fdc_id, food_name, portion_grams,
              calories, protein, carbs, fat))
        
        conn.commit()
        conn.close()
    
    def get_daily_intake(self, user_id: int, target_date: date = None) -> dict:
        """Get user's daily nutritional intake"""
        if target_date is None:
            target_date = date.today()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT SUM(calories), SUM(protein), SUM(carbs), SUM(fat)
            FROM nutrition_meals 
            WHERE user_id = ? AND date = ?
        ''', (user_id, target_date))
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            'calories': result[0] or 0,
            'protein': result[1] or 0,
            'carbs': result[2] or 0,
            'fat': result[3] or 0
        }
    
    def get_daily_meals(self, user_id: int, target_date: date = None) -> List[dict]:
        """Get user's meals for a specific date"""
        if target_date is None:
            target_date = date.today()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT meal_type, food_name, portion_grams, calories, protein, carbs, fat, logged_at
            FROM nutrition_meals 
            WHERE user_id = ? AND date = ?
            ORDER BY logged_at DESC
        ''', (user_id, target_date))
        
        results = cursor.fetchall()
        conn.close()
        
        meals = []
        for row in results:
            meals.append({
                'meal_type': row[0],
                'food_name': row[1],
                'portion_grams': row[2],
                'calories': row[3],
                'protein': row[4],
                'carbs': row[5],
                'fat': row[6],
                'logged_at': row[7]
            })
        
        return meals


class NutritionBot:
    def __init__(self):
        self.session = None
        self.db = DatabaseManager()
        self.temp_food_data = {}
        self.calculator = NutritionCalculator()
    
    async def ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def search_food(self, query: str, limit: int = 5):
        """Search for food using USDA API"""
        await self.ensure_session()
        
        url = f"{USDA_BASE_URL}/foods/search"
        params = {
            "api_key": USDA_API_KEY,
            "query": query,
            "pageSize": limit,
            "dataType": ["Foundation", "SR Legacy"]
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('foods', [])
                else:
                    logger.error(f"API request failed with status {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error searching food: {e}")
            return []
    
    async def get_food_details(self, fdc_id: int):
        """Get detailed food information"""
        # First check cache
        cached = self.db.get_cached_food(fdc_id)
        if cached:
            return cached
        
        await self.ensure_session()
        
        # If not cached, fetch from API
        url = f"{USDA_BASE_URL}/food/{fdc_id}"
        params = {"api_key": USDA_API_KEY}
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract and format nutrition data
                    food_data = self.extract_nutrition_data(data)
                    
                    # Cache the food data
                    self.db.cache_food(food_data)
                    
                    return food_data
                else:
                    logger.error(f"API request failed with status {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error getting food details: {e}")
            return None
    
    def extract_nutrition_data(self, api_data: dict) -> dict:
        """Extract nutrition data from USDA API response"""
        food_data = {
            'fdc_id': api_data.get('fdcId'),
            'name': api_data.get('description', 'Unknown food'),
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fat': 0,
            'fiber': 0,
            'sodium': 0
        }
        
        nutrients = api_data.get('foodNutrients', [])
        
        for nutrient in nutrients:
            nutrient_id = nutrient.get('nutrient', {}).get('id', 0)
            value = nutrient.get('amount', 0)
            
            if nutrient_id == 1008:  # Energy (kcal)
                food_data['calories'] = value
            elif nutrient_id == 1003:  # Protein
                food_data['protein'] = value
            elif nutrient_id == 1005:  # Carbohydrates
                food_data['carbs'] = value
            elif nutrient_id == 1004:  # Total lipid (fat)
                food_data['fat'] = value
            elif nutrient_id == 1079:  # Fiber
                food_data['fiber'] = value
            elif nutrient_id == 1093:  # Sodium
                food_data['sodium'] = value / 1000  # Convert mg to g
        
        return food_data


# Global instance
nutrition_bot = NutritionBot()