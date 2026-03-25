from datetime import datetime

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int
    username: str
    full_name: str
    email: EmailStr
    creation_date: datetime


class CompleteUser(User):
    password: str
