from fastapi import WebSocket
from typing import List, Dict
import json,asyncio
# a connection manager class for managing any websocket request
# from any user rather writing each for every guy
class ConnectionManager:
    def __init__(self):
        # creates a dictionary of type {int,WebSocket}
        # to map a user to his given webSocket for live chat
        # {user_id: websocket}
        self.active_connections:Dict[int, WebSocket]={}
    # this is the method in which we implement the connection logic of a websocket
    async def connect(self, user_id: int, websocket: WebSocket):
        # this is where the http request is upgraded to a websocket protocol
        # it takes a 1 or 2 secs for the handshake process so the server shouldn't 
        # freeze here rather it need to serve other requests too so we use the await here
        await websocket.accept()
        # after the upgrade we put the current user into our active connections dict
        self.active_connections[user_id] = websocket
        # for debugging purposes
        print(f"User {user_id} connected via WebSocket")
    # whenever the user closes the tab or
    # the server crashes or
    # we manually disconnect the user only then this disconnect is hit
    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            print(f"User {user_id} disconnected")
    # we use this method to send a json to the sender to 
    # let him know that the message is sent without any errors
    # and can be used further to add more features like typing,status etc
    async def send_personal_message(self,message:dict,user_id: int):
        if user_id in self.active_connections:
            # json.dumps() in python converts back a dict to json 
            await self.active_connections[user_id].send_text(json.dumps(message))
    # we use this method to send the message from the sender to the reciver 
    # we usually send a string here in development
    # later we can send a json to the reciver id needed
    async def send_to_user(self, message: str, receiver_id: int):
    # Send plain text to receiver
     if receiver_id in self.active_connections:
        await self.active_connections[receiver_id].send_text(message)
    async def send_ping(self, websocket: WebSocket):
        try:
            # Step 1: Send "ping"
            await websocket.send_json({"type": "ping"})
            # Step 2: Wait max 10 sec for "pong"
            await asyncio.wait_for(websocket.receive_json(),timeout=10.0)
            # If we reach here → pong received → GOOD
            return True
        except asyncio.TimeoutError:
            # No pong in 10 sec → zombie
            return False
        except Exception:
            # Network error → zombie
            return False
        
    async def periodic_ping(self):
        while True:
            await asyncio.sleep(20)  # Wait 20 sec
            user_ids = list(self.active_connections.keys())  # Copy to avoid error
            for user_id in user_ids:
                ws = self.active_connections.get(user_id)
                if ws:
                    if not await self.send_ping(ws):
                        print(f"Zombie: User {user_id} → removing")
                        self.disconnect(user_id)
# the instance of the class which 
# manages all users websocket requests
manager = ConnectionManager()