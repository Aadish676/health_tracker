from pydantic import BaseModel


class MealCreate(BaseModel):
    name: str
    meal_type: str
    quantity_grams: float = 100
    quantity_count: float = 0
    calories: int
    protein: float = 0
    carbs: float = 0
    fat: float = 0
    entry_date: str


class SleepCreate(BaseModel):
    hours: float
    quality: str
    entry_date: str


class WorkoutCreate(BaseModel):
    activity: str
    duration: int
    calories_burned: int
    entry_date: str


class PostCreate(BaseModel):
    content: str
    mood: str = "Motivated"


class GoalCreate(BaseModel):
    age: int = 20
    sex: str = "male"
    height_cm: float = 170
    weight_kg: float = 70
    activity_level: str = "moderate"
    goal_type: str = "maintain"
    maintenance_calories: int = 2200
    calorie_goal: int = 2200
    protein_goal: float = 120
    carbs_goal: float = 250
    fat_goal: float = 70


class ChatRequest(BaseModel):
    message: str


class BodyWeightCreate(BaseModel):
    weight_kg: float
    entry_date: str
