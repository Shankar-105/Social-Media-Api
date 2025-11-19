from pydantic import BaseModel,ConfigDict,Field
from datetime import datetime
from app import models,config
from typing import Optional,List
from fastapi import Query
# while the user is creating a post user shouldn't send any unncessary
# data other than the below mentioned fields when user does this
# we need to warn user that correct data isn't sent for creating a post
# so we define a schema to tell the frontend what need to be sent by the 
# user while creating a post 
# structure or schema of the post using pydantic's BaseModel class
class PostEssentials(BaseModel):
    title:str
    content:str
    enable_comments:bool=True
    hashtags:str=None

# while the user retrives the posts or when a new post is created
# there's no need of showing the user all the data about the post
# rather only data to be seen is shown so the below schema is a 
# pydantic model while returning post data to user
class PostResponse(BaseModel):
    @staticmethod
    def displayUsersPosts(post:models.Post):
        return {
            "post_media":f"{config.settings.base_url}/{config.settings.media_folder}/{post.media_path}",
            "likes":post.likes,
            "comments":post.comments_cnt
        }
# user shouldn't send any unncessary data so we need
# to validate it through a model like below
# if user sends any other data while signUp other than
# those 'username and 'passsword' then through this schema
# pydantic sends an warning to the frontend to tell the user that 
# correct data isn't sent via our api's
class UserEssentials(BaseModel):
    username:str
    password: str = Field(..., max_length=72)
    nickname:str

# when the new account for a user is created there's no meaning in
# showing all his data so we just show him what's to be shown after 
# the creation of an account
class UserResponse(BaseModel):
    id:int
    username:str
    created_at:datetime
    model_config = ConfigDict( 
        from_attributes=True
    )

# class UserLoginCred(UserEssentials):
#     pass

class TokenModel(BaseModel):
    id:int
    username:str
    accessToken:str
    tokenType:str

class VoteModel(BaseModel):
    post_id:int
    choice:bool
class VoteResponseModel(BaseModel):
    message:str

class UserUpdateInfo(BaseModel):
  username:Optional[str]=None
  bio:Optional[str]=None

class Comment(BaseModel):
    post_id:int
    content:str

class PostAnalytics(BaseModel):
    post_id:int
    views:int
    likes:int
    dislikes:int
    comments:int
    createdOn:datetime

class EditCommentModel(BaseModel):
    comment_content:str

class CommentVoteModel(BaseModel):
    comment_id:int
    choice:bool
class SearchFeature(BaseModel):
    q:str=Query(None, description="Search query")
    limit:int=10
    offset:int=0
    orderBy:Optional[str]="created_at"

class UserProfile(BaseModel):
    profilePicture:str|None
    username:str
    nickname:str
    bio:str|None
    posts:int
    followers:int
    following:int

class ResetPassword(BaseModel):
    otp:str
    old_password:str
    new_password:str

class UserProfileDisplay(BaseModel):
    @staticmethod
    def displayUserProfilePic(user:models.User):
        return {
            "profile_pic":f"{config.settings.base_url}/profilepics/{user.profile_picture}"
        }
    
class CommentsResponse(BaseModel):
    @staticmethod
    def displayComments(comments:models.Comments):
        return {
            "comment":comments.comment_content,
            "likes":comments.likes,
            "created_at":comments.created_at,
            "created_by":comments.user.username,
            "user_id":comments.user.id
        }
    
class UserOut(BaseModel):  # Basic user info for post author
    id: int
    username: str
    profile_pic:Optional[str]

class FeedPost(BaseModel):
    post_id:int
    owner:UserOut
    class Config:
        from_attributes = True  # For ORM

class MessageResponse(BaseModel):
    id: int
    content: str
    sender_id: int
    receiver_id: int
    created_at: datetime
    is_read: bool

    class Config:
        from_attributes = True

class ChatHistory(BaseModel):
    content: str
    sender_id: int
    receiver_id: int
    created_at : datetime
    is_read: bool
    class Config:
        from_attributes = True  # Important for SQLAlchemy
class FeedResponse(BaseModel):
    feed:List[FeedPost]
    total:int  # For pagination

class SharePostCreate(BaseModel):
    post_id: int
    to_user_id: int
    message: Optional[str] = None

class SharedPostResponse(BaseModel):
    id: int
    post_id: int
    from_user_id: int
    to_user_id: int
    message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class ReactionPayload(BaseModel):
    message_id: int
    reaction: str  # e.g., "❤️"

class ReactedUsers(BaseModel):
    user_id: int
    username: str
    profile_pic: Optional[str] = None
    reaction: str

class ReplyMessageSchema(BaseModel):
    to:int
    reply_msg_id:int
    content:str

class MessageSchema(BaseModel):
    to:int
    content:str

class ReplyToShareSchema(BaseModel):
    content:str
    shared_post_id: int   # the SharedPost.id they're replying to
    to:int               # receiver user_id
    class Config:
        from_attributes = True