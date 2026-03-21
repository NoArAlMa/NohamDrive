from datetime import datetime
from typing import List
from pydantic import BaseModel


class Token(BaseModel):
    token: str
    expiration_date: int | datetime
    creation_date: int | datetime
    scope: List[str]
