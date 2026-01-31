# socket_manager.py
from fastapi import WebSocket
from typing import Dict
import json, asyncio
from datetime import datetime
from fastapi.websockets import WebSocketState

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
        self.active_connections[user_id]["ping_task"] = asyncio.create_task(
    self._per_connection_pinger(user_id)
)
        print(f"User {user_id} connected via WebSocket")

    def disconnect(self, user_id: int,client_initiated: bool = True):
        conn = self.active_connections.get(user_id)
        if conn:
            task = conn.get("ping_task")
            if task:
                task.cancel()  # cancel the per-connection pinger
                # if client hasnt intiated that is we the server are kicking off
                # this guyy so there will be no incoming ws.close() except ours
                if not client_initiated:
                    ws = conn.get("ws")
                    if ws and ws.application_state == WebSocketState.CONNECTED:
                        try:
                            asyncio.create_task(ws.close(code=1000, reason="Server initiated disconnect"))
                        except:
                            pass
            del self.active_connections[user_id]
            print(f"User {user_id} disconnected")

    async def send_personal_message(self,message:dict,user_id:int):
        conn = self.active_connections.get(user_id)
        if conn:
            await conn["ws"].send_json(message)
        
    async def send_json_to_user(self,message:dict,user_id:int):
        print(f"entered into mtd 'send_json_to_user' to send to {user_id}")
        for i in self.active_connections.keys():
          print(type(i))
        conn = self.active_connections.get(user_id)
        print(conn)
        if conn:
            print("is payload being sent to recv")
            await conn["ws"].send_text(json.dumps(message))

    async def send_to_user(self,message:str,receiver_id: int):
        conn = self.active_connections.get(receiver_id)
        if conn:
            await conn["ws"].send_text(message)

    def mark_pong(self,user_id: int):
        """Called by main reader when a pong is received for user_id."""
        conn = self.active_connections.get(user_id)
        if conn and conn["ws"].application_state == WebSocketState.CONNECTED:
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
            print(f"Sent ping to user {user_id}")
            # wait for main reader to set the event
            await asyncio.wait_for(event.wait(), timeout=20.0)
            print(f"Pong received from user {user_id}")
            return True
        except asyncio.TimeoutError:
            print(f"Timeout waiting for pong from user {user_id}")
            return False
        except Exception as e:
            print(f"Error sending ping to user {user_id}: {e}")
            return False
    async def _per_connection_pinger(self,user_id:int):
        """Independent ping loop for a single connection."""
        try:
            while True:
                await asyncio.sleep(20.0)
                ok = await self.send_ping(user_id)
                if not ok:
                    print(f"Zombie: User {user_id} → removing (per-connection pinger)")
                    # disconnect will cancel this task and remove conn
                    self.disconnect(user_id,client_initiated=False)
                    break
        except asyncio.CancelledError:
            # expected when disconnect cancels this task
            print(f"Ping task cancelled for user {user_id}")
        except Exception as e:
            print(f"Per-connection pinger error for user {user_id}: {e}")
                    
    async def typing_status(self,type:str,receiver_id:int,typing_status:bool):
            message={
            "type":type,
            "typing_status":typing_status
            }
            return await self.send_personal_message(message=message,user_id=receiver_id)
# single manager instance
manager = ConnectionManager()