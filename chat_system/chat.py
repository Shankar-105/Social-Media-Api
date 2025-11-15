from fastapi import APIRouter, WebSocket, WebSocketDisconnect,Depends,Query
from app import schemas, models, oauth2,db
from sqlalchemy.orm import Session
from app.my_utils.socket_manager import manager
from chat_system import delete_msg,delete_shares,edit_msg,load_missed_msgs,msg_reaction,share_reaction,reply_msg
import json,asyncio
from datetime import datetime
router = APIRouter(tags=["chat"])

# ping_task=None

@router.websocket("/chat/ws/{user_id}")
async def chat(
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
    # load missed content  
    missed_content=await load_missed_msgs.load_missed_content(current_user.id,db)
    if missed_content:
        missed_content.reverse()
    for item in missed_content:
        try:
            await websocket.send_json(item)
        except:
            print("WebSocket broken during missed content delivery")
            break
    try:
        while True:
            data = await websocket.receive_text()
            try:
               message_data = json.loads(data)
            except json.JSONDecodeError:
        # Not a JSON message (could be plain chat text) — handle or ignore
                  print("Received non-JSON chat payload; ignoring or handle as needed:", repr(data))
                  continue
            # if the type is delete_for_everyone
            if message_data.get("type") == "delete_for_everyone":
                    try:
                        msg_id = int(message_data["message_id"])
                        recv_id = int(message_data["receiver_id"])
                    except (ValueError, TypeError):
                        print("Invalid ID format in delete_for_everyone")
                        continue  # or send error
                    await delete_msg.delete_for_everyone(
                        db=db,
                        message_id=msg_id,
                        sender_id=current_user.id,
                        receiver_id=recv_id
                    )
            elif message_data.get("type") == "reaction":
                reacted_by=current_user.id
                reaction_emoji=message_data.get("reaction")
                msg_id=message_data.get("message_id")
                reactionPayLoad=schemas.ReactionPayload(
                     message_id=msg_id,
                     reaction=reaction_emoji
                )
                await msg_reaction.react(reactionPayLoad,reacted_by,db)
            elif message_data.get("type") == "shared_post_reaction":
                reacted_by = current_user.id
                reaction_emoji = message_data.get("reaction")
                shared_id = message_data.get("shared_post_id")

                reaction_payload = schemas.ReactionPayload(
                    message_id=shared_id,  # reuse field
                    reaction=reaction_emoji
                )
                await share_reaction.react_to_shared_post(reaction_payload,reacted_by,db)
            elif message_data.get("type") == "edit_message":
                try:
                        msg_id = int(message_data.get("msg_id"))
                        new_content = message_data.get("new_content").strip()
                        recv_id = int(message_data.get("receiver_id"))
                except (ValueError,TypeError):
                        print("Invalid ID format in edit_msg")
                        continue  # or send error
                await edit_msg.edit_message(
                        db=db,
                        message_id=msg_id,
                        new_content=new_content,
                        sender_id=current_user.id,
                        recv_id=recv_id
                    )
            # if its a pong then simply mark it and set the event
            elif message_data.get("type") == "pong":
                print("Pong received — user alive")
                manager.mark_pong(user_id)
                continue
            # if its of type delete_share_for_everyone
            # simply call the method whcih does that job
            elif message_data.get("type") == "delete_share_for_everyone":
                try:
                        share_id = int(message_data["message_id"])
                        recv_id = int(message_data["receiver_id"])
                except (ValueError,TypeError):
                        print("Invalid ID format in delete_for_everyone")
                        continue  # or send error
                await delete_shares.delete_share_for_everyone(
                        db=db,
                        share_id=share_id,
                        sender_id=current_user.id,
                        receiver_id=recv_id
                    )
            # if its of type - typing 
            elif message_data.get("type") == "typing":
                 type=message_data.get("type")
                 is_typing=message_data.get("is_typing")
                 receiver_id=message_data.get("receiver_id")
                 await manager.typing_status(type=type,receiver_id=receiver_id,typing_status=is_typing)

            elif message_data.get("type") == "reply_message":
                receiver_id=int(message_data.get("to"))
                content=message_data.get("content")
                reply_msg_id=int(message_data.get("reply_msg_id"))
                payload=schemas.ReplyMessageSchema(
                     to=receiver_id,
                     reply_msg_id=reply_msg_id,
                     content=content
                )
                await reply_msg.reply_msg(payload,current_user.id,db)
            # else then its a chat message
            else:
            # Save to DB (ALWAYS — even if offline)
                msg = models.Message(
                    content=message_data.get("content"),
                    sender_id=user_id,
                    receiver_id=message_data.get("to")
                )
                db.add(msg)
                db.commit()
                db.refresh(msg)
                print("added to db")
                # Check if receiver is in active_connections
                receiver_id = msg.receiver_id
                if receiver_id in manager.active_connections:
                    try:
                        # Try to send (if fails, it's a zombie)
                        await manager.send_to_user(
                            f"User {user_id}: {msg.content}", 
                            receiver_id
                        )
                        print("Message sent via WebSocket")
                        msg.is_read = True
                        msg.read_at=datetime.utcnow()
                        db.commit()
                        print(f"Message {msg.id} marked as READ")
                    except Exception as e:
                        # Send failed → zombie socket → remove
                        print(f"Send failed: {e}")
                        manager.disconnect(receiver_id)
                        # TODO: Later, send push notification here
                else:
                    # Offline → don't send, just save in DB
                    print("Receiver offline — message saved in DB")
                    # TODO: Later, send push notification here
                # Send response back to sender
                response_data = {
                    "id": msg.id,
                    "content": msg.content,
                    "sender_id": msg.sender_id,
                    "receiver_id": msg.receiver_id,
                    "timestamp": msg.created_at.isoformat(),
                    "is_read":msg.is_read
                }
                await manager.send_personal_message(response_data, user_id)
                print("Response sent to sender")
    except WebSocketDisconnect:
        # this is executed only when the client tries to disconnect
        # like in development clicking on the disconnect button in the
        # tools like postman or in production just getting out of the app
        # at this point of time remember the frontend tool has already
        # intiated the close that is it has already sent a ws.close()
        # frame to the websocket server and it handles it you dont need 
        # again do a ws.close() here which leads to the run time errors
        # like its happening now so we take off that ws.close() and only
        # do a ws.close() manually that is we writing ws.close() only when
        # we want to kick off the user that is when he doesnt send a pong
        # and cases like that so we use a client_intitated var and do few
        # checks on it inside the disconnect method 
        manager.disconnect(user_id,client_initiated=True)
    except Exception as e:
        # some probelm with the client so we (the server) are 
        # kicking him offf after printing whats the probelm
        print(e)
        manager.disconnect(user_id,client_initiated=False)