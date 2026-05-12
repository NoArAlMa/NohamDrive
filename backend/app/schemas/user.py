from datetime import datetime

from pydantic import BaseModel, EmailStr
from pydantic import field_validator
import re


class User(BaseModel):
    id: int
    username: str
    full_name: str
    email: EmailStr
    creation_date: datetime


class CompleteUser(User):
    password: str


class UserUpdate(BaseModel):
    username: str
    email: EmailStr
    full_name: str

    @field_validator("username")
    def username_valid(cls, value: str) -> str:
        value = value.strip()
        if not 3 <= len(value) <= 20:
            raise ValueError("The username must be between 3 and 20 characters long.")
        if not re.match(r"^[a-zA-Z0-9_.-]+$", value):
            raise ValueError(
                "The username can only contain letters, numbers, _, ., or -."
            )
        return value

    @field_validator("full_name")
    def full_name_valid(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Full name cannot be empty")
        if len(value) > 75:
            raise ValueError("Full name must be less than 75 characters long")
        return value


class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    def password_complexity(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be more than 8 letter")
        if not re.search(r"[A-Z]", value):
            raise ValueError("The password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", value):
            raise ValueError("The password must contain at least one lowercase letter.")
        if not re.search(r"\d", value):
            raise ValueError("The password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("The password must contain one special letter")
        return value
