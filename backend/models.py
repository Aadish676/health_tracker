from sqlalchemy import Column, Float, ForeignKey, Integer, String
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)


class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    name = Column(String)
    meal_type = Column(String)
    quantity_grams = Column(Float, default=100)
    quantity_count = Column(Float, default=0)
    calories = Column(Integer)
    protein = Column(Float, default=0)
    carbs = Column(Float, default=0)
    fat = Column(Float, default=0)
    entry_date = Column(String)


class Sleep(Base):
    __tablename__ = "sleep"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    hours = Column(Float)
    quality = Column(String)
    entry_date = Column(String)


class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    activity = Column(String)
    duration = Column(Integer)
    calories_burned = Column(Integer)
    entry_date = Column(String)


class SocialPost(Base):
    __tablename__ = "social_posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    author_name = Column(String)
    content = Column(String)
    mood = Column(String)
    likes = Column(Integer, default=0)
    created_at = Column(String)


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    age = Column(Integer, default=20)
    sex = Column(String, default="male")
    height_cm = Column(Float, default=170)
    weight_kg = Column(Float, default=70)
    activity_level = Column(String, default="moderate")
    goal_type = Column(String, default="maintain")
    maintenance_calories = Column(Integer, default=2200)
    calorie_goal = Column(Integer, default=2200)
    protein_goal = Column(Float, default=120)
    carbs_goal = Column(Float, default=250)
    fat_goal = Column(Float, default=70)


class BodyWeight(Base):
    __tablename__ = "body_weights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    weight_kg = Column(Float)
    entry_date = Column(String)
