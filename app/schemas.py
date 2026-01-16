from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator
from datetime import datetime
from app import models, config
from typing import Optional, List, Union, Any
from fastapi import Query

# COMMON SCHEMAS

class PaginationMetadata(BaseModel):
    """Reusable pagination metadata"""
    total: int
    limit: int
    offset: int
    has_more: bool

class SuccessResponse(BaseModel):
    """General Success response"""
    message: str

class ErrorResponse(BaseModel):
    """General Error response"""
    detail: str

class MediaInfo(BaseModel):
    """General Media metadata"""
    url: str
    type: Optional[str] = None
    
class ReactionInfo(BaseModel):
    """General Reaction details"""
    reaction: str
    user_id: int
    username: str
    profile_pic: Optional[str] = None

# USER SCHEMAS

class UserSignupRequest(BaseModel):
    """Request schema for user signup"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=72)
    nickname: str = Field(..., min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    
class UserLoginRequest(BaseModel):
    """Request schema for user login"""
    username: str
    password: str

class UserUpdateRequest(BaseModel):
    """Request schema for updating user profile"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    bio: Optional[str] = Field(None, max_length=500)
    email: Optional[EmailStr] = None

class UserBasicResponse(BaseModel):
    """General Minimal user info"""
    id: int
    username: str
    nickname: str
    profile_pic: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class UserProfileResponse(BaseModel):
    """General Complete user profile data"""
    id: int
    username: str
    nickname: str
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    posts_count: int
    followers_count: int
    following_count: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserResponse(BaseModel):
    """General Standard user response after User Account Creation"""
    id: int
    username: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# AUTHENTICATION SCHEMAS

class TokenModel(BaseModel):
    """JWT token response"""
    id: int
    username: str
    accessToken: str
    tokenType: str

# POST SCHEMAS

class PostCreateRequest(BaseModel):
    """Request schema for creating a post"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    enable_comments: bool = True
    hashtags: Optional[str] = None

class PostUpdateRequest(BaseModel):
    """Request schema for updating a post"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    enable_comments: Optional[bool] = None
    hashtags: Optional[str] = None

class PostDetailResponse(BaseModel):
    """Complete post details"""
    id: int
    title: str
    content: str
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    likes: int
    dislikes: int
    views: int
    comments_count: int
    enable_comments: bool
    hashtags: Optional[str] = None
    created_at: datetime
    owner: UserBasicResponse
    
    model_config = ConfigDict(from_attributes=True)

class PostListItemResponse(BaseModel):
    """Post item in a list (lighter version)"""
    id: int
    title: str
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    likes: int
    comments_count: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PostListResponse(BaseModel):
    """Paginated list of posts"""
    posts: List[PostListItemResponse]
    pagination: PaginationMetadata

class PostAnalytics(BaseModel):
    """Post analytics data"""
    post_id: int
    views: int
    likes: int
    dislikes: int
    comments: int
    created_at: datetime

# COMMENT SCHEMAS

class CommentCreateRequest(BaseModel):
    """Request schema for creating a comment"""
    post_id: int
    content: str = Field(..., min_length=1, max_length=1000)

class CommentUpdateRequest(BaseModel):
    """Request schema for updating a comment"""
    comment_content: str = Field(..., min_length=1, max_length=1000)

class CommentDetailResponse(BaseModel):
    """Complete comment details"""
    id: int
    post_id: int
    content: str
    likes: int
    created_at: datetime
    user: UserBasicResponse
    
    model_config = ConfigDict(from_attributes=True)

class CommentListResponse(BaseModel):
    """Paginated list of comments"""
    comments: List[CommentDetailResponse]
    pagination: PaginationMetadata

# VOTE SCHEMAS

class VoteRequest(BaseModel):
    """Request schema for voting on a post"""
    post_id: int
    choice: bool  # True = like, False = dislike

class CommentVoteRequest(BaseModel):
    """Request schema for voting on a comment"""
    comment_id: int
    choice: bool  # True = like

class VoteResponse(BaseModel):
    """Response after voting"""
    message: str
    likes: Optional[int] = None
    dislikes: Optional[int] = None

# CONNECTION SCHEMAS (Follow/Unfollow)

class FollowResponse(BaseModel):
    """Response after follow/unfollow action"""
    message: str
    following_count: Optional[int] = None

# SEARCH SCHEMAS

class SearchRequest(BaseModel):
    """Request schema for search"""
    q: str = Field(..., min_length=1)
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)
    orderBy: Optional[str] = "created_at"

class SearchResultResponse(BaseModel):
    """Search result response"""
    result_type: str  # "users" or "posts"
    users: Optional[List[UserBasicResponse]] = None
    posts: Optional[List[PostListItemResponse]] = None
    total: int

# FEED SCHEMAS

class FeedItemResponse(BaseModel):
    """Feed item with post and owner"""
    post_id: int
    post: PostListItemResponse
    owner: UserBasicResponse

class FeedResponse(BaseModel):
    """Feed response with pagination"""
    feed: List[FeedItemResponse]
    total: int

# PASSWORD & OTP SCHEMAS

class PasswordChangeInitRequest(BaseModel):
    """Request to initiate password change"""
    email: EmailStr

class PasswordResetRequest(BaseModel):
    """Request to reset password with OTP"""
    otp: str = Field(..., min_length=6, max_length=6)
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=72)

# MESSAGE & CHAT SCHEMAS

class MessageCreateRequest(BaseModel):
    """Request schema for sending a message"""
    to: int
    content: Optional[str] = None
    media_url: Optional[str] = None
    media_type: Optional[str] = None

class MessageEditRequest(BaseModel):
    """Request schema for editing a message"""
    message_id: int
    new_content: str
    receiver_id: int

class MessageDeleteRequest(BaseModel):
    """Request schema for deleting a message"""
    message_id: int
    receiver_id: int

class MessageReactionRequest(BaseModel):
    """Request schema for reacting to a message"""
    message_id: int
    reaction: str  # emoji

class MessageDetailResponse(BaseModel):
    """Message response"""
    id: int
    content: Optional[str]
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    sender_id: int
    receiver_id: int
    created_at: datetime
    is_read: bool
    is_edited: bool
    edited_at: Optional[datetime] = None
    reaction_count: int
    is_reply: bool = False
    
    model_config = ConfigDict(from_attributes=True)

class ReplyMessageRequest(BaseModel):
    """Request schema for replying to a message"""
    to: int
    reply_msg_id: int
    content: Optional[str] = None
    media_url: Optional[str] = None
    media_type: Optional[str] = None

class ChatMessageItem(BaseModel):
    """Chat message item in history"""
    type: str = "message"
    id: int
    content: Optional[str]
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    sender_id: int
    receiver_id: int
    timestamp: str
    is_edited: bool
    reaction_count: int
    is_read: bool
    is_reply: bool
    reply_to: Optional[dict] = None

class SharedPostItem(BaseModel):
    """Shared post item in chat history"""
    type: str = "shared_post"
    shared_id: int
    post_id: int
    sender_id: int
    receiver_id: int
    title: str
    media_type: Optional[str]
    media_url: Optional[str]
    sender_nickname: str
    message: Optional[str]
    sent_at: str
    is_read: bool

class ChatHistoryResponse(BaseModel):
    """Complete chat history"""
    history: List[Union[ChatMessageItem, SharedPostItem]]

class CanEditResponse(BaseModel):
    """Response for can edit check"""
    can_edit: bool
    message: Optional[str] = None

# SHARED POST SCHEMAS

class SharePostRequest(BaseModel):
    """Request schema for sharing a post"""
    post_id: int
    to_user_id: int
    message: Optional[str] = None

class SharedPostDetailResponse(BaseModel):
    """Shared post response"""
    id: int
    post_id: int
    from_user_id: int
    to_user_id: int
    message: Optional[str]
    created_at: datetime
    is_read: bool
    
    model_config = ConfigDict(from_attributes=True)

class ReplyToShareRequest(BaseModel):
    """Request schema for replying to a shared post"""
    shared_post_id: int
    to: int
    content: Optional[str] = None
    media_url: Optional[str] = None
    media_type: Optional[str] = None

class ShareReactionRequest(BaseModel):
    """Request schema for reacting to shared post"""
    shared_post_id: int
    reaction: str

# STATS & ANALYTICS SCHEMAS

class VoteStatsResponse(BaseModel):
    """User vote statistics"""
    liked_posts_count: int
    disliked_posts_count: int

class CommentStatsResponse(BaseModel):
    """User comment statistics"""
    total_comments: int
    unique_posts_commented: int

class UserPostsResponse(BaseModel):
    """Response for user's posts list"""
    posts: List[PostListItemResponse]
    total: int

# LEGACY SCHEMAS (keeping for backwards compatibility during transition)

class PostEssentials(BaseModel):
    """Legacy schema - consider using PostCreateRequest instead"""
    title: str
    content: str
    enable_comments: bool = True
    hashtags: Optional[str] = None

class UserEssentials(BaseModel):
    """Legacy schema - consider using UserSignupRequest instead"""
    username: str
    password: str = Field(..., max_length=72)
    nickname: str

class Comment(BaseModel):
    """Legacy schema - consider using CommentCreateRequest instead"""
    post_id: int
    content: str

class EditCommentModel(BaseModel):
    """Legacy schema - consider using CommentUpdateRequest instead"""
    comment_content: str

class VoteModel(BaseModel):
    """Legacy schema - consider using VoteRequest instead"""
    post_id: int
    choice: bool

class CommentVoteModel(BaseModel):
    """Legacy schema - consider using CommentVoteRequest instead"""
    comment_id: int
    choice: bool

class UserProfile(BaseModel):
    """Legacy user profile schema"""
    profilePicture: Optional[str] = None
    username: str
    nickname: str
    bio: Optional[str] = None
    posts: int
    followers: int
    following: int

class ResetPassword(BaseModel):
    """Legacy password reset schema"""
    otp: str
    old_password: str
    new_password: str

class SearchFeature(BaseModel):
    """Legacy search schema"""
    q: str = Query(None, description="Search query")
    limit: int = 10
    offset: int = 0
    orderBy: Optional[str] = "created_at"

class MessageResponse(BaseModel):
    """Legacy message response"""
    id: int
    content: str
    sender_id: int
    receiver_id: int
    created_at: datetime
    is_read: bool
    
    model_config = ConfigDict(from_attributes=True)

class ChatHistory(BaseModel):
    """Legacy chat history schema"""
    content: str
    sender_id: int
    receiver_id: int
    created_at: datetime
    is_read: bool
    
    model_config = ConfigDict(from_attributes=True)

class UserOut(BaseModel):
    """Legacy basic user info for post author"""
    id: int
    username: str
    profile_pic: Optional[str] = None

class FeedPost(BaseModel):
    """Legacy feed post schema"""
    post_id: int
    owner: UserOut
    
    model_config = ConfigDict(from_attributes=True)

class SharePostCreate(BaseModel):
    """Legacy share post schema"""
    post_id: int
    to_user_id: int
    message: Optional[str] = None

class SharedPostResponse(BaseModel):
    """Legacy shared post response"""
    id: int
    post_id: int
    from_user_id: int
    to_user_id: int
    message: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ReactionPayload(BaseModel):
    """Legacy reaction payload"""
    message_id: int
    reaction: str

class ReactedUsers(BaseModel):
    """Legacy reacted users schema"""
    user_id: int
    username: str
    profile_pic: Optional[str] = None
    reaction: str

class ReplyMessageSchema(BaseModel):
    """Legacy reply message schema"""
    to: int
    reply_msg_id: int
    content: Optional[str] = None
    media_url: Optional[str] = None
    media_type: Optional[str] = None

class ReplyToShareSchema(BaseModel):
    """Legacy reply to share schema"""
    shared_post_id: int
    content: Optional[str] = None
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    to: int
    
    model_config = ConfigDict(from_attributes=True)

class MessageSchema(BaseModel):
    """Legacy message schema"""
    to: int
    content: Optional[str] = None
    media_url: Optional[str] = None
    media_type: Optional[str] = None