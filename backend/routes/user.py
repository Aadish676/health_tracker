from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import SessionLocal
from models import User
from auth import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter()


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register")
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.email == request.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    new_user = User(
        name=request.name,
        email=request.email,
        password=hash_password(request.password)
    )

    db.add(new_user)
    db.commit()

    return {"message": "User registered"}


@router.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == request.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid email"
        )

    if not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=400,
            detail="Invalid password"
        )

    token = create_access_token(
        {"user_id": user.id}
    )

    return {"access_token": token}
