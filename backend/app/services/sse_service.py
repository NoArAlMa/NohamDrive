from typing import Dict, List, Any, AsyncGenerator
import asyncio
import json
from core.logging import setup_logger

logger = setup_logger(__name__)


class SSEManager:
    def __init__(self):
        self.clients: Dict[
            int, List[asyncio.Queue]
        ] = {}  # {user_id: [queue1, queue2, ...]}
        self.lock = asyncio.Lock()

    async def add_client(self, user_id: int) -> AsyncGenerator[str, None]:
        queue = asyncio.Queue()
        async with self.lock:
            if user_id not in self.clients:
                self.clients[user_id] = []
            self.clients[user_id].append(queue)
        try:
            while True:
                message = await queue.get()
                yield f"data: {json.dumps(message)}\n\n"
        finally:
            async with self.lock:
                if user_id in self.clients and queue in self.clients[user_id]:
                    self.clients[user_id].remove(queue)
                    if not self.clients[
                        user_id
                    ]:  # Plus de connexions pour cet utilisateur
                        del self.clients[user_id]

    async def notify_user(self, user_id: int, message: Dict[str, Any]):
        async with self.lock:
            if user_id in self.clients:
                for client_queue in self.clients[user_id]:
                    try:
                        await client_queue.put(message)
                        logger.info(f"Notification envoyée à user {user_id}: {message}")
                    except Exception as e:
                        logger.error(
                            f"Erreur notification SSE pour user {user_id}: {e}"
                        )
                        if client_queue in self.clients[user_id]:
                            self.clients[user_id].remove(client_queue)
                            if not self.clients[user_id]:
                                del self.clients[user_id]

    async def notify_all(self, message: Dict[str, Any]):
        async with self.lock:
            for user_id, queues in self.clients.items():
                for client_queue in queues:
                    try:
                        await client_queue.put(message)
                    except Exception as e:
                        logger.error(
                            f"Erreur notification SSE pour user {user_id}: {e}"
                        )
                        if client_queue in queues:
                            queues.remove(client_queue)
                            if not queues:
                                del self.clients[user_id]


sse_manager = SSEManager()
