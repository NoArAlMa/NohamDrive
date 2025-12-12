from fastapi import APIRouter
from app.schemas.terminal import TerminalRequest, TerminalResponse
from typing import Dict, Callable

router = APIRouter(prefix="/terminal", tags=["Terminal"])

COMMANDS: Dict[str, Callable] = {
    # TODO : Ajouter les fonctions au fur et à mesure
}


@router.post("/exec/", response_model=TerminalResponse)
async def execute_command(
    command: str,
    request: TerminalRequest,
    user_id: int = 1,  # TODO : A remplacer avec le système d'auth
) -> TerminalResponse:
    return_data = {"command": command, "request": request}
    return TerminalResponse(data=return_data)
