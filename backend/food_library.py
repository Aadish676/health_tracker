COMMON_FOODS = {
    "banana": {"serving": "100 g", "calories": 89, "protein": 1.1, "carbs": 22.8, "fat": 0.3},
    "apple": {"serving": "100 g", "calories": 52, "protein": 0.3, "carbs": 13.8, "fat": 0.2},
    "orange": {"serving": "100 g", "calories": 47, "protein": 0.9, "carbs": 11.8, "fat": 0.1},
    "mango": {"serving": "100 g", "calories": 60, "protein": 0.8, "carbs": 15.0, "fat": 0.4},
    "grapes": {"serving": "100 g", "calories": 69, "protein": 0.7, "carbs": 18.1, "fat": 0.2},
    "watermelon": {"serving": "100 g", "calories": 30, "protein": 0.6, "carbs": 7.6, "fat": 0.2},
    "papaya": {"serving": "100 g", "calories": 43, "protein": 0.5, "carbs": 10.8, "fat": 0.3},
    "pineapple": {"serving": "100 g", "calories": 50, "protein": 0.5, "carbs": 13.1, "fat": 0.1},
    "rice cooked": {"serving": "100 g", "calories": 130, "protein": 2.7, "carbs": 28.2, "fat": 0.3},
    "brown rice cooked": {"serving": "100 g", "calories": 123, "protein": 2.7, "carbs": 25.6, "fat": 1.0},
    "white rice cooked": {"serving": "100 g", "calories": 130, "protein": 2.7, "carbs": 28.2, "fat": 0.3},
    "roti": {"serving": "1 medium", "grams": 40, "calories": 120, "protein": 3.5, "carbs": 22.0, "fat": 3.0},
    "chapati": {"serving": "1 medium", "grams": 40, "calories": 120, "protein": 3.5, "carbs": 22.0, "fat": 3.0},
    "oats": {"serving": "100 g", "calories": 389, "protein": 16.9, "carbs": 66.3, "fat": 6.9},
    "poha": {"serving": "100 g", "calories": 130, "protein": 2.6, "carbs": 23.8, "fat": 3.3},
    "upma": {"serving": "100 g", "calories": 120, "protein": 3.0, "carbs": 19.0, "fat": 4.0},
    "idli": {"serving": "1 idli", "grams": 39, "calories": 58, "protein": 1.6, "carbs": 12.0, "fat": 0.4},
    "dosa": {"serving": "1 medium dosa", "grams": 97, "calories": 168, "protein": 3.9, "carbs": 29.4, "fat": 3.7},
    "boiled egg": {"serving": "1 egg", "grams": 50, "calories": 78, "protein": 6.3, "carbs": 0.6, "fat": 5.3},
    "egg": {"serving": "1 large", "grams": 50, "calories": 72, "protein": 6.3, "carbs": 0.4, "fat": 4.8},
    "egg white": {"serving": "1 egg white", "grams": 33, "calories": 17, "protein": 3.6, "carbs": 0.2, "fat": 0.1},
    "omelette": {"serving": "1 egg omelette", "grams": 61, "calories": 94, "protein": 6.4, "carbs": 0.6, "fat": 7.0},
    "chicken breast": {"serving": "100 g", "calories": 165, "protein": 31.0, "carbs": 0.0, "fat": 3.6},
    "fish": {"serving": "100 g", "calories": 128, "protein": 26.0, "carbs": 0.0, "fat": 2.7},
    "salmon": {"serving": "100 g", "calories": 208, "protein": 20.4, "carbs": 0.0, "fat": 13.4},
    "paneer": {"serving": "100 g", "calories": 265, "protein": 18.3, "carbs": 1.2, "fat": 20.8},
    "tofu": {"serving": "100 g", "calories": 76, "protein": 8.1, "carbs": 1.9, "fat": 4.8},
    "soy chunks": {"serving": "100 g", "calories": 345, "protein": 52.0, "carbs": 33.0, "fat": 0.5},
    "dal cooked": {"serving": "100 g", "calories": 116, "protein": 9.0, "carbs": 20.1, "fat": 0.4},
    "moong dal cooked": {"serving": "100 g", "calories": 105, "protein": 7.0, "carbs": 19.0, "fat": 0.4},
    "rajma cooked": {"serving": "100 g", "calories": 127, "protein": 8.7, "carbs": 22.8, "fat": 0.5},
    "chickpeas cooked": {"serving": "100 g", "calories": 164, "protein": 8.9, "carbs": 27.4, "fat": 2.6},
    "milk": {"serving": "100 ml", "calories": 61, "protein": 3.2, "carbs": 4.8, "fat": 3.3},
    "curd": {"serving": "100 g", "calories": 61, "protein": 3.5, "carbs": 4.7, "fat": 3.3},
    "greek yogurt": {"serving": "100 g", "calories": 59, "protein": 10.2, "carbs": 3.6, "fat": 0.4},
    "peanut butter": {"serving": "100 g", "calories": 588, "protein": 25.1, "carbs": 20.0, "fat": 50.0},
    "almonds": {"serving": "100 g", "calories": 579, "protein": 21.2, "carbs": 21.6, "fat": 49.9},
    "potato boiled": {"serving": "100 g", "calories": 87, "protein": 1.9, "carbs": 20.1, "fat": 0.1},
    "sweet potato": {"serving": "100 g", "calories": 86, "protein": 1.6, "carbs": 20.1, "fat": 0.1},
    "broccoli": {"serving": "100 g", "calories": 34, "protein": 2.8, "carbs": 6.6, "fat": 0.4},
    "spinach": {"serving": "100 g", "calories": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4},
    "cucumber": {"serving": "100 g", "calories": 15, "protein": 0.7, "carbs": 3.6, "fat": 0.1},
    "tomato": {"serving": "100 g", "calories": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.1},
}


def _scale(macros, grams=None, count=None):
    if count and macros.get("grams"):
        multiplier = count
        display_grams = macros["grams"] * count
        serving_size = f"{count:g} x {macros['serving']}"
    else:
        display_grams = grams or macros.get("grams") or 100
        base_grams = macros.get("grams") or 100
        multiplier = display_grams / base_grams
        serving_size = f"{display_grams:g} g"

    return {
        "serving_size": serving_size,
        "quantity_grams": round(display_grams, 1),
        "quantity_count": count or 0,
        "calories": round(macros["calories"] * multiplier),
        "protein": round(macros["protein"] * multiplier, 1),
        "carbs": round(macros["carbs"] * multiplier, 1),
        "fat": round(macros["fat"] * multiplier, 1),
    }


def find_common_foods(query, grams=100, count=0):
    normalized_query = query.strip().lower()
    matches = []

    for name, macros in COMMON_FOODS.items():
        if normalized_query == name or normalized_query in name or name in normalized_query:
            scaled = _scale(macros, grams=grams, count=count)
            matches.append(
                {
                    "match_score": 0 if normalized_query == name else 1,
                    "name": name.title(),
                    **scaled,
                    "source": "Common foods library",
                }
            )

    matches.sort(key=lambda item: (item["match_score"], item["name"]))
    return [
        {field: value for field, value in item.items() if field != "match_score"}
        for item in matches[:6]
    ]
