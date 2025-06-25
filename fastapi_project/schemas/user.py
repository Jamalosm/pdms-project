# fastapi_project/schemas/user.py

from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str = None
    role: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: str | None
    role: str

    class Config:
        orm_mode = True
