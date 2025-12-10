from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional
from datetime import datetime

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """Modèle de base pour toutes les réponses API, utilisable à la fois avec `response_model` et en retour direct."""

    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = "Request successful"
    timestamp: datetime = Field(default_factory=datetime.now)
    status_code: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"key": "value"},
                "message": "Opération réussie",
                "timestamp": "2025-12-09T12:00:00Z",
            }
        }
