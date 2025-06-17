from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, crud
from database import get_db
from models import User
from utils import require_role
from schemas import UserCreate, UserOut
from utils import hash_password
from fastapi import Path

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/", response_model=list[UserOut])
def get_all_users(db: Session = Depends(get_db), user:dict =Depends(require_role(["admin"]))):
    user = db.query(models.User).all()
    return user


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), user: dict =Depends(require_role(["admin"]))):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, user_update: UserCreate, db: Session = Depends(get_db), user: dict = Depends(require_role(["admin"]))):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.email = user_update.email
    db_user.hashed_password = hash_password(user_update.password)
    db_user.role = user_update.role

    db.commit()
    db.refresh(db_user)

    return db_user


@router.get("/")
def get_all_users(db: Session = Depends(get_db), user: dict = Depends(require_role(["admin"]))):
    user = db.query(User).all()
    return users


@router.post("/", response_model=schemas.UserOut) 
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@router.get("/{user_id}", response_model=schemas.UserOut)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete("/users/{user_id}", status_code=204)
def delete_user(
    user_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    user: dict = Depends(require_role(["admin"]))
):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, details="User not found")

        db.delete(db_user)
        db.commit()
        return

from fastapi import APIRouter, Request, Depends
from permissions import role_required
from utils import require_role


router = APIRouter()

@router.get("/admin/dashboard")
def get_admin_data(request: Request, _: None = Depends(role_required(["Admin","Manager"]))):
	return{"message": "Hello Admin or Manager!"}

@router.get("/admin-only")
def admin_dashboard(user=Depends(require_role("admin"))):
	return{"message": f"Welcome, admin {user.email}!"}