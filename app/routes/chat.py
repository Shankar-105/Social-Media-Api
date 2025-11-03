from fastapi import APIRouter, WebSocket, WebSocketDisconnect,Depends,Query
from app import schemas, models, oauth2,db
from sqlalchemy.orm import Session
from app.my_utils.websocket import manager
import json
from datetime import datetime
router = APIRouter(prefix="/chat",tags=["chat"])

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    token: str=Query(None,description="Search query params"),
    db: Session=Depends(db.getDb)
):
    # we check whether the token is sent or not 
    # if not sent then we close the socket connection 
    # because we require token to validate or authunicate the user
    if not token:
        await websocket.close(code=1008)
        return
    try:
        # get the user from the token passed token
        current_user = oauth2.getCurrentUser(token,db)
        # if he is a different guy well then close the socket connection
        # this prevents spoofing other users acccessing or pretending to be the actual user
        if current_user.id != user_id:
            await websocket.close(code=1008)
            return
    except:
        await websocket.close(code=1008)
        return
    # well if the token has passed all the above tests
    # make a connection request by using the manager obj 
    await manager.connect(user_id,websocket)
    try:
        # after connecting the user successfully
        # enter him into the live chat the while True:
        # which stays forever until any of ther three disconnect cases are hit
        while True:
            # the sender may send data at any time
            # so waiting for the data until he sends is ridiculous
            # so we use await which allows the server to do other unfinished jobs
            data = await websocket.receive_text()
            # if msg is sent by the sender well its time 
            # to send the msg to the rexciver and store it in db 
            # but wait you cannot directly send that msg from 
            # the frontend or the sender because the sender's JS sends the data 
            # in the form of JSON so as we need to store that messsage in db 
            # and also send a string to the reciver there is a neeed to convert 
            # that json data to a python dict son.loads() does that for us 
            message_data = json.loads(data)
            print("data successfully loaded")
            # Save to DB
            # store it in db so create a models.Message obj
            msg = models.Message(
                content=message_data["content"],
                sender_id=user_id,
                receiver_id=message_data["to"]
            )
            db.add(msg)
            db.commit()
            db.refresh(msg)
            print("added to db")
            # Send to receiver if online
            # now send a string to reciver call the send_to_user method
            await manager.send_to_user(f"User {user_id}: {msg.content}",msg.receiver_id)
            print("entered into message sender method via send_to_user")
            # collect the response data that is the sender data so that 
            # we use this for future enhancements to let the sender know
            # much more about the status of the msg that he sent
            response_data = {
                "id": msg.id,
                "content": msg.content,
                "sender_id": msg.sender_id,
                "receiver_id": msg.receiver_id,
                "timestamp": msg.created_at.isoformat()  # ← Convert datetime to string
            }
            # call the send_personal_message from websockets.py
            await manager.send_personal_message(response_data,user_id)
            print("entered into message sender method directly")
    # this except block it hit when the user closes the tab
    # or the server stops or crashes
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    # this is hit if any exception in the code like any syntax or validation errors
    except Exception as e:
        print(e)
        manager.disconnect(user_id)