from pydantic import BaseModel

from app.utils.response import BaseResponse
from typing import Optional


class TerminalRequest(BaseModel):
    currentPath: str
    args: list[str]


class TerminalReturn(BaseModel):
    currentPath: str
    output: Optional[str]
    error: Optional[str]


class TerminalResponse(BaseResponse[TerminalReturn]): ...
