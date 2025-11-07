# socket_manager.py
from fastapi import WebSocket
from typing import Dict
import json, asyncio
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        # store dict per user: {user_id: {"ws": WebSocket, "pong_event": Event, "last_pong": datetime}}
        self.active_connections: Dict[int, Dict] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = {
            "ws": websocket,
            "pong_event": asyncio.Event(),
            "last_pong": datetime.utcnow()
        }
        print(f"User {user_id} connected via WebSocket")

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            print(f"User {user_id} disconnected")

    async def send_personal_message(self, message: dict, user_id: int):
        conn = self.active_connections.get(user_id)
        if conn:
            await conn["ws"].send_text(json.dumps(message))

    async def send_to_user(self, message: str, receiver_id: int):
        conn = self.active_connections.get(receiver_id)
        if conn:
            await conn["ws"].send_text(message)

    def mark_pong(self, user_id: int):
        """Called by main reader when a pong is received for user_id."""
        conn = self.active_connections.get(user_id)
        if conn:
            # set event so send_ping can continue
            conn["pong_event"].set()
            conn["last_pong"] = datetime.utcnow()
            # create a fresh event for next ping
            conn["pong_event"] = asyncio.Event()
            print(f"Marked pong for user {user_id}")

    async def send_ping(self,user_id:int) -> bool:
        """Send ping to the given user's websocket and wait for the corresponding event."""
        conn = self.active_connections.get(user_id)
        if not conn:
            return False
        ws = conn["ws"]
        event = conn["pong_event"]
        try:
            # clear event (it was re-created after last pong)
            # send ping
            await ws.send_json({"type": "ping"})
            # wait for main reader to set the event
            await asyncio.wait_for(event.wait(), timeout=10.0)
            return True
        except asyncio.TimeoutError:
            print(f"Timeout waiting for pong from user {user_id}")
            return False
        except Exception as e:
            print(f"Error sending ping to user {user_id}: {e}")
            return False

    async def periodic_ping(self):
        while True:
            await asyncio.sleep(20)
            user_ids = list(self.active_connections.keys())
            for user_id in user_ids:
                ok = await self.send_ping(user_id)
                if not ok:
                    print(f"Zombie: User {user_id} → removing")
                    self.disconnect(user_id)

# single manager instance
manager = ConnectionManager()