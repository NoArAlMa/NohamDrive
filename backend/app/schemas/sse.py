from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class SSEMessage(BaseModel):
    """Message standardisé pour les événements SSE."""

    event: str = Field(
        ..., description="Type d'événement (upload, delete, rename, etc.)"
    )
    user_id: int = Field(..., description="ID de l'utilisateur concerné")
    message: str = Field(..., description="Message lisible pour l'utilisateur")
    payload: Optional[Dict[str, Any]] = Field(
        None, description="Données métier spécifiques à l'événement."
    )
    timestamp: Optional[str] = Field(
        None,
        description="Timestamp ISO du message (facultatif, utile pour debug ou UI)",
    )
