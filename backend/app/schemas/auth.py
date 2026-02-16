from pydantic import BaseModel, EmailStr, field_validator
import re


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str
    name: str

    # 🔹 Validator pour le mot de passe
    @field_validator("password")
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

    # 🔹 Validator pour le username
    @field_validator("username")
    def username_valid(cls, value: str) -> str:
        if not 3 <= len(value) <= 20:
            raise ValueError("The username must be between 3 and 20 characters long.")
        if not re.match(r"^[a-zA-Z0-9_.-]+$", value):
            raise ValueError(
                "The username can only contain letters, numbers, _, ., or -."
            )
        return value

    # 🔹 Validator pour le name
    @field_validator("name")
    def name_valid(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Name cannot be empty")
        if len(value) > 50:
            raise ValueError("Name must be less thant 50 characters long")
        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str
