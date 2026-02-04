from asyncio import Lock
from typing import Any, Dict, Set
from fastapi import WebSocket
from core.logging import setup_logger

logger = setup_logger(__name__)


class WebSocketManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.lock = Lock()

    async def connect(self, websocket: WebSocket):
        async with self.lock:
            await websocket.accept()
            self.active_connections.add(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self.lock:
            self.active_connections.discard(websocket)

    async def notify_clients(self, message: Dict[str, Any]):
        async with self.lock:
            for connection in self.active_connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Erreur notification WebSocket: {e}")
                    self.active_connections.discard(connection)

    async def send_ping(self, websocket: WebSocket):
        await websocket.send_text("ping")

    async def receive_pong(self, websocket: WebSocket):
        data = await websocket.receive_text()
        if data == "ping":
            await websocket.send_text("pong")


websocket_manager = WebSocketManager()
