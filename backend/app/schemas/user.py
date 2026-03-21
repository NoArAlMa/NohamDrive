from datetime import datetime

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    username: str
    full_name: str
    email: EmailStr
    creation_date: datetime
