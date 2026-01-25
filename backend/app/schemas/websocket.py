from pydantic import BaseModel


class WSMessage(BaseModel):
    event: str
    user_id: int
    path: str
    message: str
    filename: str | None = None
    new_name: str | None = None
    old_path: str | None = None
    new_path: str | None = None
