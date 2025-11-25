import pytest

def get_ws_url(token,user_id):
    return f"ws://localhost:8000/chat/ws/{user_id}?token={token}"

@pytest.mark.asyncio
async def test_ws_chat_connect(client,get_token):
    user_id = 1  # Assuming testuser
    with client.websocket_connect(f"/chat/ws/{user_id}?token={get_token}") as ws:
        try:
            msg = await ws.receive_json()
            # wait for the ping probably 10 secs
            if msg.get("type") == "ping":
                # send a pong and the test is passed
                await ws.send_json({"type": "pong"})
        except Exception:
            pass