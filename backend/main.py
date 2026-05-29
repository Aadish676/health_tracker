from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from database import Base, engine
from routes import tracker, user

import models

Base.metadata.create_all(bind=engine)


def add_column_if_missing(table_name, column_name, column_type):
    with engine.begin() as connection:
        columns = connection.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
        existing_columns = {column[1] for column in columns}

        if column_name not in existing_columns:
            connection.execute(
                text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
            )


add_column_if_missing("meals", "carbs", "FLOAT DEFAULT 0")
add_column_if_missing("meals", "fat", "FLOAT DEFAULT 0")
add_column_if_missing("meals", "quantity_grams", "FLOAT DEFAULT 100")
add_column_if_missing("meals", "quantity_count", "FLOAT DEFAULT 0")

app = FastAPI(title="Health Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "https://health-tracker-ten-lac.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user.router)
app.include_router(tracker.router)


@app.get("/")
def home():
    return {
        "message": "Health Tracker API Running"
    }
