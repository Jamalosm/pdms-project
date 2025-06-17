from fastapi import FastAPI, FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db         #  your database session getter
from schemas import UserCreate, UserOut
import crud                         #The file you created above
import models
from database import engine

from auth import router as auth_router
from users import router as users_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(users_router)

from models import Base
from database import engine

#create database tables
models.Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
	return{"message": "Welcome to FastAPI"}

