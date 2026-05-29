from datetime import datetime
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from auth import decode_access_token
from database import SessionLocal
from food_library import find_common_foods
from models import BodyWeight, Goal, Meal, Sleep, SocialPost, User, Workout
from schemas import BodyWeightCreate, ChatRequest, GoalCreate, MealCreate, PostCreate, SleepCreate, WorkoutCreate

router = APIRouter()

OPEN_FOOD_FACTS_URL = "https://world.openfoodfacts.org/cgi/search.pl"
OPEN_FOOD_FACTS_BARCODE_URL = "https://world.openfoodfacts.org/api/v2/product"

WORKOUT_MET_VALUES = {
    "walking": 3.5,
    "brisk walking": 4.3,
    "running": 9.8,
    "jogging": 7.0,
    "cycling": 7.5,
    "swimming": 8.0,
    "yoga": 2.5,
    "strength training": 6.0,
    "weight lifting": 6.0,
    "football": 8.0,
    "basketball": 6.5,
    "dancing": 5.0,
    "jump rope": 12.3,
    "hiit": 8.0,
}

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "athlete": 1.9,
}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing access token")

    token = authorization.replace("Bearer ", "", 1)
    payload = decode_access_token(token)

    if not payload or "user_id" not in payload:
        raise HTTPException(status_code=401, detail="Invalid access token")

    user = db.query(User).filter(User.id == payload["user_id"]).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def serialize_record(record):
    return {
        column.name: getattr(record, column.name)
        for column in record.__table__.columns
    }


def update_model(record, payload):
    for field, value in payload.model_dump().items():
        setattr(record, field, value)


def round_number(value):
    if value is None:
        return 0
    return round(float(value), 1)


def calculate_maintenance(age, sex, height_cm, weight_kg, activity_level):
    sex_adjustment = 5 if sex.lower() == "male" else -161
    bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + sex_adjustment
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
    return round(bmr * multiplier)


def default_goals(user_id):
    maintenance = calculate_maintenance(20, "male", 170, 70, "moderate")
    return Goal(
        user_id=user_id,
        age=20,
        sex="male",
        height_cm=170,
        weight_kg=70,
        activity_level="moderate",
        goal_type="maintain",
        maintenance_calories=maintenance,
        calorie_goal=maintenance,
        protein_goal=120,
        carbs_goal=250,
        fat_goal=70,
    )


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
    }


@router.get("/food-lookup")
def food_lookup(query: str, grams: float = 100, count: float = 0):
    if not query.strip():
        raise HTTPException(status_code=400, detail="Food name is required")
    if grams <= 0:
        raise HTTPException(status_code=400, detail="Food weight must be positive")

    suggestions = find_common_foods(query, grams=grams, count=count)

    params = urlencode(
        {
            "search_terms": query,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": 6,
            "fields": "product_name,nutriments,serving_size",
        }
    )
    request = Request(
        f"{OPEN_FOOD_FACTS_URL}?{params}",
        headers={"User-Agent": "health-tracker-local-app/1.0"},
    )

    try:
        with urlopen(request, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        if suggestions:
            return {"query": query, "grams": grams, "results": suggestions}
        raise HTTPException(status_code=502, detail="Could not reach the food nutrition database.") from exc

    multiplier = grams / 100

    for product in data.get("products", []):
        nutriments = product.get("nutriments", {})
        name = product.get("product_name") or query.title()

        suggestions.append(
            {
                "name": name,
                "serving_size": product.get("serving_size") or "100 g",
                "quantity_grams": grams,
                "quantity_count": count,
                "calories": round_number(nutriments.get("energy-kcal_100g") * multiplier if nutriments.get("energy-kcal_100g") is not None else 0),
                "protein": round_number(nutriments.get("proteins_100g") * multiplier if nutriments.get("proteins_100g") is not None else 0),
                "carbs": round_number(nutriments.get("carbohydrates_100g") * multiplier if nutriments.get("carbohydrates_100g") is not None else 0),
                "fat": round_number(nutriments.get("fat_100g") * multiplier if nutriments.get("fat_100g") is not None else 0),
                "source": "Open Food Facts",
            }
        )

    useful_suggestions = [
        item for item in suggestions
        if item["calories"] or item["protein"] or item["carbs"] or item["fat"]
    ]

    return {"query": query, "grams": grams, "results": useful_suggestions[:10]}


@router.get("/barcode-lookup/{barcode}")
def barcode_lookup(barcode: str, grams: float = 100, count: float = 0):
    request = Request(
        f"{OPEN_FOOD_FACTS_BARCODE_URL}/{barcode}.json",
        headers={"User-Agent": "health-tracker-local-app/1.0"},
    )

    try:
        with urlopen(request, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Could not reach barcode database.") from exc

    if data.get("status") != 1:
        raise HTTPException(status_code=404, detail="Barcode not found")

    product = data.get("product", {})
    nutriments = product.get("nutriments", {})
    multiplier = grams / 100

    return {
        "name": product.get("product_name") or f"Barcode {barcode}",
        "serving_size": product.get("serving_size") or f"{grams:g} g",
        "quantity_grams": grams,
        "quantity_count": count,
        "calories": round_number(nutriments.get("energy-kcal_100g") * multiplier if nutriments.get("energy-kcal_100g") is not None else 0),
        "protein": round_number(nutriments.get("proteins_100g") * multiplier if nutriments.get("proteins_100g") is not None else 0),
        "carbs": round_number(nutriments.get("carbohydrates_100g") * multiplier if nutriments.get("carbohydrates_100g") is not None else 0),
        "fat": round_number(nutriments.get("fat_100g") * multiplier if nutriments.get("fat_100g") is not None else 0),
        "source": "Open Food Facts barcode",
    }


@router.get("/workout-estimate")
def workout_estimate(activity: str, duration: int = 30, weight_kg: float = 70):
    if duration <= 0 or weight_kg <= 0:
        raise HTTPException(status_code=400, detail="Duration and weight must be positive")

    normalized = activity.strip().lower()
    met = WORKOUT_MET_VALUES.get(normalized)

    if met is None:
        for name, value in WORKOUT_MET_VALUES.items():
            if name in normalized or normalized in name:
                met = value
                break

    if met is None:
        met = 5.0

    calories = round((met * 3.5 * weight_kg / 200) * duration)

    return {
        "activity": activity,
        "duration": duration,
        "weight_kg": weight_kg,
        "calories_burned": calories,
        "met": met,
        "source": "MET activity estimate",
    }


@router.post("/maintenance-calories")
def maintenance_calories(goal: GoalCreate):
    maintenance = calculate_maintenance(
        goal.age,
        goal.sex,
        goal.height_cm,
        goal.weight_kg,
        goal.activity_level,
    )
    return {"maintenance_calories": maintenance}


@router.get("/goals")
def get_goals(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    goals = db.query(Goal).filter(Goal.user_id == user.id).first()

    if not goals:
        goals = default_goals(user.id)
        db.add(goals)
        db.commit()
        db.refresh(goals)

    return serialize_record(goals)


@router.put("/goals")
def save_goals(
    goal_data: GoalCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    goals = db.query(Goal).filter(Goal.user_id == user.id).first()
    maintenance = calculate_maintenance(
        goal_data.age,
        goal_data.sex,
        goal_data.height_cm,
        goal_data.weight_kg,
        goal_data.activity_level,
    )
    data = goal_data.model_dump()
    data["maintenance_calories"] = maintenance

    if not goals:
        goals = Goal(user_id=user.id, **data)
        db.add(goals)
    else:
        for field, value in data.items():
            setattr(goals, field, value)

    db.commit()
    db.refresh(goals)
    return serialize_record(goals)


@router.post("/chat")
def nutrition_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    message = request.message.lower()
    today = datetime.utcnow().date().isoformat()
    meals = db.query(Meal).filter(Meal.user_id == user.id, Meal.entry_date == today).all()
    goals = db.query(Goal).filter(Goal.user_id == user.id).first()

    calories = sum(meal.calories for meal in meals)
    protein = round(sum(meal.protein or 0 for meal in meals), 1)
    carbs = round(sum(meal.carbs or 0 for meal in meals), 1)
    fat = round(sum(meal.fat or 0 for meal in meals), 1)

    if not goals:
        goals = default_goals(user.id)
        db.add(goals)
        db.commit()
        db.refresh(goals)

    calorie_left = goals.calorie_goal - calories
    protein_left = round(goals.protein_goal - protein, 1)
    carbs_left = round(goals.carbs_goal - carbs, 1)
    fat_left = round(goals.fat_goal - fat, 1)

    suggestions = []

    if "protein" in message or protein_left > 25:
        suggestions.append(
            f"You still have about {max(protein_left, 0)}g protein left. Good options: paneer, chicken breast, eggs, dal, tofu, Greek yogurt."
        )

    if "calorie" in message or "cut" in message or "fat loss" in message:
        if calorie_left >= 0:
            suggestions.append(f"You have about {calorie_left} calories left today. Keep the next meal high-protein and high-fiber.")
        else:
            suggestions.append(f"You are about {abs(calorie_left)} calories over target today. Keep the next meal lighter and avoid liquid calories.")

    if "carb" in message:
        suggestions.append(f"Carbs today: {carbs}g. Target: {goals.carbs_goal}g. Remaining: {max(carbs_left, 0)}g.")

    if "fat" in message:
        suggestions.append(f"Fat today: {fat}g. Target: {goals.fat_goal}g. Remaining: {max(fat_left, 0)}g.")

    if "what should i eat" in message or "suggest" in message or "next meal" in message:
        if protein_left > 20 and calorie_left > 300:
            suggestions.append("Try a balanced meal: rice or roti, dal or chicken/tofu/paneer, vegetables, and curd.")
        elif calorie_left < 250:
            suggestions.append("Try a light option: cucumber salad, curd, boiled eggs, or a small fruit portion.")
        else:
            suggestions.append("Try a moderate snack: Greek yogurt with fruit, sprouts, paneer/tofu, or oats.")

    if not suggestions:
        suggestions.append(
            "Today you have logged "
            f"{calories} calories, {protein}g protein, {carbs}g carbs, and {fat}g fat. "
            "Ask me about protein, calories, fat loss, carbs, or what to eat next."
        )

    return {
        "reply": " ".join(suggestions),
        "today": {
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fat,
        },
        "remaining": {
            "calories": calorie_left,
            "protein": protein_left,
            "carbs": carbs_left,
            "fat": fat_left,
        },
    }


@router.post("/meals")
def add_meal(
    meal: MealCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    new_meal = Meal(user_id=user.id, **meal.model_dump())
    db.add(new_meal)
    db.commit()
    db.refresh(new_meal)
    return serialize_record(new_meal)


@router.get("/meals")
def list_meals(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    meals = (
        db.query(Meal)
        .filter(Meal.user_id == user.id)
        .order_by(Meal.id.desc())
        .all()
    )
    return [serialize_record(meal) for meal in meals]


@router.delete("/meals/{meal_id}")
def delete_meal(
    meal_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    meal = db.query(Meal).filter(Meal.id == meal_id, Meal.user_id == user.id).first()

    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    db.delete(meal)
    db.commit()
    return {"message": "Meal deleted"}


@router.put("/meals/{meal_id}")
def update_meal(
    meal_id: int,
    meal_data: MealCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    meal = db.query(Meal).filter(Meal.id == meal_id, Meal.user_id == user.id).first()

    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    update_model(meal, meal_data)
    db.commit()
    db.refresh(meal)
    return serialize_record(meal)


@router.post("/sleep")
def add_sleep(
    sleep: SleepCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    new_sleep = Sleep(user_id=user.id, **sleep.model_dump())
    db.add(new_sleep)
    db.commit()
    db.refresh(new_sleep)
    return serialize_record(new_sleep)


@router.get("/sleep")
def list_sleep(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sleep_entries = (
        db.query(Sleep)
        .filter(Sleep.user_id == user.id)
        .order_by(Sleep.id.desc())
        .all()
    )
    return [serialize_record(entry) for entry in sleep_entries]


@router.delete("/sleep/{sleep_id}")
def delete_sleep(
    sleep_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sleep = db.query(Sleep).filter(Sleep.id == sleep_id, Sleep.user_id == user.id).first()

    if not sleep:
        raise HTTPException(status_code=404, detail="Sleep entry not found")

    db.delete(sleep)
    db.commit()
    return {"message": "Sleep entry deleted"}


@router.put("/sleep/{sleep_id}")
def update_sleep(
    sleep_id: int,
    sleep_data: SleepCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sleep = db.query(Sleep).filter(Sleep.id == sleep_id, Sleep.user_id == user.id).first()

    if not sleep:
        raise HTTPException(status_code=404, detail="Sleep entry not found")

    update_model(sleep, sleep_data)
    db.commit()
    db.refresh(sleep)
    return serialize_record(sleep)


@router.post("/workouts")
def add_workout(
    workout: WorkoutCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    new_workout = Workout(user_id=user.id, **workout.model_dump())
    db.add(new_workout)
    db.commit()
    db.refresh(new_workout)
    return serialize_record(new_workout)


@router.get("/workouts")
def list_workouts(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    workouts = (
        db.query(Workout)
        .filter(Workout.user_id == user.id)
        .order_by(Workout.id.desc())
        .all()
    )
    return [serialize_record(workout) for workout in workouts]


@router.delete("/workouts/{workout_id}")
def delete_workout(
    workout_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    workout = (
        db.query(Workout)
        .filter(Workout.id == workout_id, Workout.user_id == user.id)
        .first()
    )

    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    db.delete(workout)
    db.commit()
    return {"message": "Workout deleted"}


@router.put("/workouts/{workout_id}")
def update_workout(
    workout_id: int,
    workout_data: WorkoutCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    workout = (
        db.query(Workout)
        .filter(Workout.id == workout_id, Workout.user_id == user.id)
        .first()
    )

    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    update_model(workout, workout_data)
    db.commit()
    db.refresh(workout)
    return serialize_record(workout)


@router.post("/body-weight")
def add_body_weight(
    weight: BodyWeightCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    new_weight = BodyWeight(user_id=user.id, **weight.model_dump())
    db.add(new_weight)
    db.commit()
    db.refresh(new_weight)
    return serialize_record(new_weight)


@router.get("/body-weight")
def list_body_weight(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    weights = (
        db.query(BodyWeight)
        .filter(BodyWeight.user_id == user.id)
        .order_by(BodyWeight.entry_date.desc(), BodyWeight.id.desc())
        .all()
    )
    return [serialize_record(weight) for weight in weights]


@router.put("/body-weight/{weight_id}")
def update_body_weight(
    weight_id: int,
    weight_data: BodyWeightCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    weight = (
        db.query(BodyWeight)
        .filter(BodyWeight.id == weight_id, BodyWeight.user_id == user.id)
        .first()
    )

    if not weight:
        raise HTTPException(status_code=404, detail="Body weight entry not found")

    update_model(weight, weight_data)
    db.commit()
    db.refresh(weight)
    return serialize_record(weight)


@router.delete("/body-weight/{weight_id}")
def delete_body_weight(
    weight_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    weight = (
        db.query(BodyWeight)
        .filter(BodyWeight.id == weight_id, BodyWeight.user_id == user.id)
        .first()
    )

    if not weight:
        raise HTTPException(status_code=404, detail="Body weight entry not found")

    db.delete(weight)
    db.commit()
    return {"message": "Body weight entry deleted"}


@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    meals = db.query(Meal).filter(Meal.user_id == user.id).all()
    sleep_entries = db.query(Sleep).filter(Sleep.user_id == user.id).all()
    workouts = db.query(Workout).filter(Workout.user_id == user.id).all()
    body_weights = db.query(BodyWeight).filter(BodyWeight.user_id == user.id).order_by(BodyWeight.entry_date.asc(), BodyWeight.id.asc()).all()
    goals = db.query(Goal).filter(Goal.user_id == user.id).first()
    today = datetime.utcnow().date().isoformat()
    today_meals = [meal for meal in meals if meal.entry_date == today]

    total_calories = sum(meal.calories for meal in meals)
    total_protein = round(sum(meal.protein or 0 for meal in meals), 1)
    total_carbs = round(sum(meal.carbs or 0 for meal in meals), 1)
    total_fat = round(sum(meal.fat or 0 for meal in meals), 1)
    today_calories = sum(meal.calories for meal in today_meals)
    today_protein = round(sum(meal.protein or 0 for meal in today_meals), 1)
    today_carbs = round(sum(meal.carbs or 0 for meal in today_meals), 1)
    today_fat = round(sum(meal.fat or 0 for meal in today_meals), 1)
    total_burned = sum(workout.calories_burned for workout in workouts)
    total_minutes = sum(workout.duration for workout in workouts)
    average_sleep = 0

    if sleep_entries:
        average_sleep = round(
            sum(entry.hours for entry in sleep_entries) / len(sleep_entries),
            1,
        )

    return {
        "totals": {
            "meals": len(meals),
            "calories": total_calories,
            "protein": total_protein,
            "carbs": total_carbs,
            "fat": total_fat,
            "workouts": len(workouts),
            "minutes": total_minutes,
            "calories_burned": total_burned,
            "sleep_entries": len(sleep_entries),
            "average_sleep": average_sleep,
        },
        "recent": {
            "meals": [serialize_record(meal) for meal in meals[-5:]][::-1],
            "sleep": [serialize_record(entry) for entry in sleep_entries[-5:]][::-1],
            "workouts": [serialize_record(workout) for workout in workouts[-5:]][::-1],
            "body_weight": [serialize_record(weight) for weight in body_weights[-5:]][::-1],
        },
        "today": {
            "calories": today_calories,
            "protein": today_protein,
            "carbs": today_carbs,
            "fat": today_fat,
        },
        "goals": serialize_record(goals) if goals else None,
        "body_weight": {
            "current": body_weights[-1].weight_kg if body_weights else None,
            "start": body_weights[0].weight_kg if body_weights else None,
            "change": round(body_weights[-1].weight_kg - body_weights[0].weight_kg, 1) if len(body_weights) > 1 else 0,
        },
    }


@router.post("/posts")
def add_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    new_post = SocialPost(
        user_id=user.id,
        author_name=user.name,
        content=post.content,
        mood=post.mood,
        likes=0,
        created_at=datetime.utcnow().isoformat(timespec="seconds"),
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return serialize_record(new_post)


@router.get("/posts")
def list_posts(db: Session = Depends(get_db)):
    posts = db.query(SocialPost).order_by(SocialPost.id.desc()).limit(50).all()
    return [serialize_record(post) for post in posts]


@router.post("/posts/{post_id}/like")
def like_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(SocialPost).filter(SocialPost.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.likes += 1
    db.commit()
    db.refresh(post)
    return serialize_record(post)
