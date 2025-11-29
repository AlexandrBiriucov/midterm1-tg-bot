import aiohttp
import logging
from datetime import date
from typing import Dict, List, Optional
from sqlalchemy import func
from bot.core.database import get_session
from bot.core.models import User, NutritionGoal, FoodCache, NutritionMeal

logger = logging.getLogger(__name__)

# USDA API Configuration
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


class NutritionDatabase:
    """Database operations for nutrition tracking"""
    
    @staticmethod
    def ensure_user_exists(telegram_id: int, username: str = None):
        """Ensure user exists in database"""
        with get_session() as session:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if not user:
                user = User(
                    user_id=telegram_id,
                    telegram_id=telegram_id,
                    username=username
                )
                session.add(user)
                session.commit()
    
    @staticmethod
    def set_user_goals(user_id: int, calories: float, protein: float, 
                      carbs: float, fat: float, bmr: float = None, 
                      tdee: float = None, goal_type: str = None):
        """Set or update user's nutrition goals"""
        with get_session() as session:
            goal = session.query(NutritionGoal).filter_by(user_id=user_id).first()
            
            if goal:
                # Update existing goal
                goal.daily_calories = calories
                goal.daily_protein = protein
                goal.daily_carbs = carbs
                goal.daily_fat = fat
                goal.bmr = bmr
                goal.tdee = tdee
                goal.goal_type = goal_type
            else:
                # Create new goal
                goal = NutritionGoal(
                    user_id=user_id,
                    daily_calories=calories,
                    daily_protein=protein,
                    daily_carbs=carbs,
                    daily_fat=fat,
                    bmr=bmr,
                    tdee=tdee,
                    goal_type=goal_type
                )
                session.add(goal)
            
            session.commit()
    
    @staticmethod
    def get_user_goals(user_id: int) -> Optional[Dict]:
        """Get user's nutrition goals"""
        with get_session() as session:
            goal = session.query(NutritionGoal).filter_by(user_id=user_id).first()
            
            if goal:
                return {
                    'calories': goal.daily_calories,
                    'protein': goal.daily_protein,
                    'carbs': goal.daily_carbs,
                    'fat': goal.daily_fat,
                    'bmr': goal.bmr,
                    'tdee': goal.tdee,
                    'goal_type': goal.goal_type
                }
            return None
    
    @staticmethod
    def cache_food(food_data: dict):
        """Cache food data in database"""
        with get_session() as session:
            food = session.query(FoodCache).filter_by(fdc_id=food_data['fdc_id']).first()
            
            if food:
                # Update existing cache
                food.name = food_data['name']
                food.calories_per_100g = food_data.get('calories', 0)
                food.protein_per_100g = food_data.get('protein', 0)
                food.carbs_per_100g = food_data.get('carbs', 0)
                food.fat_per_100g = food_data.get('fat', 0)
                food.fiber_per_100g = food_data.get('fiber')
                food.sodium_per_100g = food_data.get('sodium')
            else:
                # Create new cache entry
                food = FoodCache(
                    fdc_id=food_data['fdc_id'],
                    name=food_data['name'],
                    calories_per_100g=food_data.get('calories', 0),
                    protein_per_100g=food_data.get('protein', 0),
                    carbs_per_100g=food_data.get('carbs', 0),
                    fat_per_100g=food_data.get('fat', 0),
                    fiber_per_100g=food_data.get('fiber'),
                    sodium_per_100g=food_data.get('sodium')
                )
                session.add(food)
            
            session.commit()
    
    @staticmethod
    def get_cached_food(fdc_id: int) -> Optional[Dict]:
        """Get cached food data"""
        with get_session() as session:
            food = session.query(FoodCache).filter_by(fdc_id=fdc_id).first()
            
            if food:
                return {
                    'fdc_id': food.fdc_id,
                    'name': food.name,
                    'calories': food.calories_per_100g,
                    'protein': food.protein_per_100g,
                    'carbs': food.carbs_per_100g,
                    'fat': food.fat_per_100g,
                    'fiber': food.fiber_per_100g,
                    'sodium': food.sodium_per_100g
                }
            return None
    
    @staticmethod
    def log_meal(user_id: int, meal_type: str, fdc_id: int, food_name: str,
                 portion_grams: float, calories: float, protein: float, 
                 carbs: float, fat: float):
        """Log a meal entry"""
        with get_session() as session:
            # Get the food_cache_id for this fdc_id
            food_cache = session.query(FoodCache).filter_by(fdc_id=fdc_id).first()
            
            if not food_cache:
                logger.error(f"FoodCache not found for fdc_id {fdc_id}")
                return
            
            meal = NutritionMeal(
                user_id=user_id,
                date=date.today(),
                meal_type=meal_type,
                food_cache_id=food_cache.food_cache_id,
                fdc_id=fdc_id,
                food_name=food_name,
                portion_grams=portion_grams,
                calories=calories,
                protein=protein,
                carbs=carbs,
                fat=fat
            )
            session.add(meal)
            session.commit()
    
    @staticmethod
    def get_daily_intake(user_id: int, target_date: date = None) -> Dict:
        """Get user's total daily intake"""
        if target_date is None:
            target_date = date.today()
        
        with get_session() as session:
            result = session.query(
                func.sum(NutritionMeal.calories).label('calories'),
                func.sum(NutritionMeal.protein).label('protein'),
                func.sum(NutritionMeal.carbs).label('carbs'),
                func.sum(NutritionMeal.fat).label('fat')
            ).filter(
                NutritionMeal.user_id == user_id,
                NutritionMeal.date == target_date
            ).first()
            
            return {
                'calories': result.calories or 0,
                'protein': result.protein or 0,
                'carbs': result.carbs or 0,
                'fat': result.fat or 0
            }
    
    @staticmethod
    def get_daily_meals(user_id: int, target_date: date = None) -> List[Dict]:
        """Get user's meals for a specific date"""
        if target_date is None:
            target_date = date.today()
        
        with get_session() as session:
            meals = session.query(NutritionMeal).filter(
                NutritionMeal.user_id == user_id,
                NutritionMeal.date == target_date
            ).order_by(NutritionMeal.logged_at.desc()).all()
            
            return [
                {
                    'meal_type': meal.meal_type,
                    'food_name': meal.food_name,
                    'portion_grams': meal.portion_grams,
                    'calories': meal.calories,
                    'protein': meal.protein,
                    'carbs': meal.carbs,
                    'fat': meal.fat,
                    'logged_at': meal.logged_at
                }
                for meal in meals
            ]


class NutritionBot:
    """Main nutrition bot service with USDA API integration"""
    
    def __init__(self):
        self.session = None
        self.db = NutritionDatabase()
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