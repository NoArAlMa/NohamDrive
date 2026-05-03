from typing import Dict, List, Any, AsyncGenerator, Tuple
import asyncio
import json
from fastapi import Request
import redis.asyncio as redis
from core.logging import setup_logger

logger = setup_logger(__name__)

ClientConnection = Tuple[str, asyncio.Queue]


class SSEManager:
    def __init__(self, redis_client: redis.Redis | None):
        self.clients: Dict[int, List[ClientConnection]] = {}
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

    async def _redis_listener(self) -> None:
        """Écoute Redis et redispatche les messages vers les clients locaux."""
        if not self.pubsub:
            return

        await self.pubsub.psubscribe("sse:user:*", "sse:broadcast")

        async for message in self.pubsub.listen():
            if message["type"] not in ("pmessage", "message"):
                continue

            try:
                data = json.loads(message["data"])
            except Exception:
                logger.warning("Invalid JSON from Redis, skipping message")
                continue

            channel = message.get("channel")
            if isinstance(channel, bytes):
                channel = channel.decode()

            if channel == "sse:broadcast":
                await self._notify_local_all(data)

            elif channel.startswith("sse:user:"):
                try:
                    user_id = int(channel.split(":")[-1])
                    await self._notify_local_user(user_id, data)
                except ValueError:
                    logger.warning(f"Invalid user_id in channel: {channel}")

    async def add_client(self, user_id: int, token: str) -> AsyncGenerator[str, None]:
        """
        Ajoute un client SSE et retourne un flux d'événements.
        """
        queue: asyncio.Queue = asyncio.Queue()

        async with self.lock:
            self.clients.setdefault(user_id, []).append((token, queue))

        logger.info(f"SSE client connected (user={user_id})")

        try:
            while True:
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=15)

                    event_name = message.get("event", "message")
                    payload = {k: v for k, v in message.items() if k != "event"}

                    yield f"event: {event_name}\n"
                    yield f"data: {json.dumps(payload)}\n\n"

                except asyncio.TimeoutError:
                    yield ": ping\n\n"

        finally:
            await self._remove_client(user_id, queue)
            logger.info(f"SSE client disconnected (user={user_id})")

    async def _remove_client(self, user_id: int, queue: asyncio.Queue) -> None:
        """Supprime proprement un client."""
        async with self.lock:
            if user_id not in self.clients:
                return

            self.clients[user_id] = [
                (t, q) for (t, q) in self.clients[user_id] if q != queue
            ]

            if not self.clients[user_id]:
                del self.clients[user_id]

    async def notify_user(self, user_id: int, message: Dict[str, Any]) -> None:
        """
        Envoie un message à un utilisateur.
        """
        if self.redis:
            try:
                await self.redis.publish(f"sse:user:{user_id}", json.dumps(message))
            except Exception as e:
                logger.error(f"Redis notify_user error: {e}")
        else:
            await self._notify_local_user(user_id, message)

    async def notify_all(self, message: Dict[str, Any]) -> None:
        """Envoie un message à tous les clients."""
        if self.redis:
            try:
                await self.redis.publish("sse:broadcast", json.dumps(message))
            except Exception as e:
                logger.error(f"Redis notify_all error: {e}")
        else:
            await self._notify_local_all(message)

    async def _notify_local_user(self, user_id: int, message: Dict[str, Any]) -> None:
        """Envoie un message à tous les clients d’un utilisateur en local"""
        async with self.lock:
            for _, queue in self.clients.get(user_id, []):
                try:
                    await queue.put(message)
                except Exception as e:
                    logger.error(f"SSE queue error (user={user_id}): {e}")

    async def _notify_local_all(self, message: Dict[str, Any]) -> None:
        """Broadcast à tous les clients connectés en local"""
        async with self.lock:
            for user_id, connections in self.clients.items():
                for _, queue in connections:
                    try:
                        await queue.put(message)
                    except Exception as e:
                        logger.error(f"SSE broadcast error (user={user_id}): {e}")


def get_sse_manager(request: Request) -> SSEManager:
    """Fournit l'instance SSEManager attachée à l'application."""
    return request.app.state.sse_manager
