from typing import Dict, List, Any, AsyncGenerator
import asyncio
import json
from fastapi import Request
import redis.asyncio as redis
from core.logging import setup_logger

logger = setup_logger(__name__)


class SSEManager:
    def __init__(self, redis_client: redis.Redis | None):
        self.clients: Dict[int, List[asyncio.Queue]] = {}
        self.lock = asyncio.Lock()

        self.redis = redis_client
        self.pubsub = self.redis.pubsub() if self.redis else None
        self.listener_task: asyncio.Task | None = None

    async def start_listener(self):
        """Lance le listener Redis si Redis est actif."""
        if self.redis:
            self.pubsub = self.redis.pubsub()
            self.listener_task = asyncio.create_task(self._redis_listener())

    async def shutdown(self):
        """Arrête le listener Redis"""
        if self.listener_task:
            self.listener_task.cancel()
            try:
                await self.listener_task
            except asyncio.CancelledError:
                pass

        if self.pubsub:
            await self.pubsub.close()

    async def _redis_listener(self):
        """Écoute les messages Redis et les redispatche localement"""
        if not self.pubsub:
            return

        await self.pubsub.psubscribe("sse:user:*", "sse:broadcast")

        async for message in self.pubsub.listen():
            if message["type"] not in ("pmessage", "message"):
                continue

            try:
                data = json.loads(message["data"])
            except Exception:
                continue

            channel = message.get("channel")
            if isinstance(channel, bytes):
                channel = channel.decode()

            # Broadcast global
            if channel == "sse:broadcast":
                await self._notify_local_all(data)
                continue

            # Channel user spécifique
            if channel.startswith("sse:user:"):
                try:
                    user_id = int(channel.split(":")[-1])
                except ValueError:
                    continue
                await self._notify_local_user(user_id, data)

    async def add_client(self, user_id: int) -> AsyncGenerator[str, None]:
        """Ajoute un client SSE"""
        queue = asyncio.Queue()

        async with self.lock:
            self.clients.setdefault(user_id, []).append(queue)

        try:
            while True:
                message = await queue.get()
                yield f"data: {json.dumps(message)}\n\n"
        finally:
            async with self.lock:
                if user_id in self.clients and queue in self.clients[user_id]:
                    self.clients[user_id].remove(queue)
                    if not self.clients[user_id]:
                        del self.clients[user_id]

    async def notify_user(self, user_id: int, message: Dict[str, Any]):
        """Envoie un message à un utilisateur. Redis si dispo, sinon local"""
        if self.redis:
            try:
                await self.redis.publish(f"sse:user:{user_id}", json.dumps(message))
            except Exception as e:
                logger.error(f"Erreur Redis notify_user: {e}")

        await self._notify_local_user(user_id, message)

    async def notify_all(self, message: Dict[str, Any]):
        """Broadcast global. Redis si dispo, sinon local."""
        if self.redis:
            try:
                await self.redis.publish("sse:broadcast", json.dumps(message))
            except Exception as e:
                logger.error(f"Erreur Redis notify_all: {e}")
        await self._notify_local_all(message)

    async def _notify_local_user(self, user_id: int, message: Dict[str, Any]):
        """Envoie un message localement à tous les clients d’un user"""
        async with self.lock:
            if user_id in self.clients:
                for queue in list(self.clients[user_id]):
                    try:
                        await queue.put(message)
                    except Exception as e:
                        logger.error(f"SSE local error user {user_id}: {e}")

    async def _notify_local_all(self, message: Dict[str, Any]):
        """Envoie un message localement à tous les clients"""
        async with self.lock:
            for user_id in list(self.clients.keys()):
                for queue in list(self.clients[user_id]):
                    try:
                        await queue.put(message)
                    except Exception as e:
                        logger.error(f"SSE local error broadcast user {user_id}: {e}")


def get_sse_manager(request: Request) -> SSEManager:
    """Fournit l'instance SSEManager attachée à l'application."""
    return request.app.state.sse_manager
