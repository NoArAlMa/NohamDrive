from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional 

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Schéma unifié pour toutes les réponses API."""

    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
    error: Optional[dict] = None 
    status_code: int = Field(..., ge=100, le=599)

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {...},
                "message": "Opération réussie",
                "status_code": 200,
            }
        }
