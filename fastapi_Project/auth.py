from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from database import get_db
from utils import verify_password, create_access_token, hash_password
import models
from schemas import UserCreate
from utils import require_role
from utils import create_refresh_token
from fastapi import Request

from dotenv import load_dotenv
import os

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid Credentials")

    # Create token payload
    token_data = {
        "sub": user.email,
        "role": user.role
    }

    # Generate both tokens
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }



@router.post("/register")  # ← fixed: colon (:) was wrong, should be slash (/)
def register(user: UserCreate, db: Session = Depends(get_db)):

    # check if user already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user instance
    new_user = models.User(
        email=user.email,
        hashed_password=hash_password(user.password),  # ← make sure hash_password is imported
        role=user.role
    )

    # save to db
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully", "user_id": new_user.id}


@router.get("/admin-only")
def admin_data(user: dict = Depends(require_role(["admin"]))):
    return {"message": f"Hello {user['email']}, you have admin access."}

@router.post("/refresh_token")
def refresh_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    refresh_token = auth_header.split(" ")[1]


    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")

        if email is None or role is None:
            raise HTTPException(status_code=401, details="Invalid refresh token")


        new_access_token = create_access_token(data={"sub": email, "role": role})


        return{"access_token": new_access_token, "token_type": "bearer"}


    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
