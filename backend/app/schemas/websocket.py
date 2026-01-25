from typing import Optional, Any
from pydantic import BaseModel


class SSEMessage(BaseModel):
    event: str
    user_id: int
    message: str
    data: Optional[Any]
