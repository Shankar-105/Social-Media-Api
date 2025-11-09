from app.db import Base
from sqlalchemy import Column,Integer,String,Boolean,ForeignKey,Table,DateTime,UniqueConstraint
from sqlalchemy.sql.expression import null,text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func
# structure or model of the db tables
connections = Table(
    'connections', Base.metadata,
    Column('followed_id',Integer,ForeignKey('users.id',ondelete="CASCADE"),primary_key=True),
    Column('follower_id',Integer,ForeignKey('users.id',ondelete="CASCADE"),primary_key=True)
)

class SharedPost(Base):
    __tablename__ = "shared_posts"

    id = Column(Integer,primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"))
    from_user_id = Column(Integer, ForeignKey("users.id"))
    to_user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(String, nullable=True)  # Optional caption when sharing
    created_at = Column(DateTime, default=datetime.utcnow)
    is_read=Column(Boolean,default=False,server_default="false")
    # Relationships
    post = relationship("Post",back_populates="shared_posts")
    from_user = relationship("User", foreign_keys=[from_user_id],back_populates="sent_posts")
    to_user = relationship("User", foreign_keys=[to_user_id],back_populates="received_posts")

# models.py
class DeletedMessage(Base):
    __tablename__ = "deleted_messages"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    # Unique: one user can't delete same msg twice
    __table_args__ = (UniqueConstraint('user_id', 'message_id',name='uq_user_deleted_msg'),)

class OTP(Base):
    __tablename__ = "otps"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)  # Only 1 per email
    otp = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
class Votes(Base):
    __tablename__='votes'
    post_id=Column(Integer,ForeignKey("posts.id",ondelete="CASCADE"),primary_key=True,nullable=False)
    user_id=Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),primary_key=True,nullable=False)
    action=Column(Boolean,nullable=False)

class CommentVotes(Base):
    __tablename__='comment_votes'
    comment_id=Column(Integer,ForeignKey("comments.id",ondelete="CASCADE"),primary_key=True,nullable=False)
    user_id=Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),primary_key=True,nullable=False)
    like=Column(Boolean,nullable=False)

class Comments(Base):
    __tablename__='comments'
    id = Column(Integer,primary_key=True)
    post_id=Column(Integer,ForeignKey("posts.id",ondelete="CASCADE"),nullable=False)
    user_id=Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
    comment_content=Column(String,nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    likes=Column(Integer,default=0,server_default=text("0"),nullable=False)
class Post(Base):
    __tablename__='posts'
    id=Column(Integer,primary_key=True,nullable=False)
    media_path = Column(String, nullable=True)  # NEW: stores "posts_media/funny_cat.mp4"
    media_type = Column(String, nullable=True)  # "image" or "video"
    title=Column(String,nullable=False)
    content=Column(String,nullable=False)
    enable_comments=Column(Boolean,server_default="TRUE",nullable=False)
    created_at=Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    user_id=Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
    likes=Column(Integer,default=0,server_default="0",nullable=False)
    dis_likes=Column(Integer,default=0,server_default="0",nullable=False)
    views=Column(Integer,default=0,server_default=text("0"))
    comments_cnt=Column(Integer,default=0,server_default=text("0"))
    hashtags=Column(String,nullable=True)

    shared_posts = relationship("SharedPost",back_populates="post")
class PostView(Base):
    __tablename__ = "post_views"
    post_id = Column(Integer, ForeignKey("posts.id",ondelete="CASCADE"),primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id",ondelete="CASCADE"),primary_key=True)
    viewed_at = Column(DateTime,default=datetime.utcnow)
class User(Base):
      __tablename__='users'
      id=Column(Integer,primary_key=True,nullable=False)
      username=Column(String,nullable=False,unique=True)
      password=Column(String,nullable=False)
      nickname=Column(String,nullable=False)
      bio=Column(String,nullable=True)
      email=Column(String,nullable=True)
      profile_picture=Column(String,nullable=True)
      created_at=Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
      followers_cnt=Column(Integer,default=0,server_default="0",nullable=False)
      following_cnt=Column(Integer,default=0,server_default="0",nullable=False)
      # added relationship between the posts table and the users table so that
      # when you actually need all the posts of a user there's no need from now on 
      # to go check the posts table and query it for Posts.user_id==currentUser.id
      # inorder to get all posts of a certain user but rather by declaring this relationship
      # you just do the currentUser.posts and sqlAlchemy internally does the joins
      # and retrievs you all of the users posts!
      posts=relationship('Post',backref='user')
      # a many to many relationship
      followers = relationship(
        'User',
        secondary=connections,  # The middle table
        primaryjoin=(connections.c.followed_id == id),  # "I am the follwed guyy"
        secondaryjoin=(connections.c.follower_id == id),  # "They are my followers"
        backref='following'  # reverse property
    )
      voted_posts = relationship(
        'Post',
        secondary='votes',  # The middle table
        primaryjoin=(Votes.user_id == id),  # User.id links to Votes.user_id
        secondaryjoin=(Votes.post_id == Post.id),  # Votes.post_id links to Post.id
        backref='voters'  # allows posts to access users who voted on them
    )
      total_comments=relationship('Comments',backref='user')
      sent_posts = relationship("SharedPost", foreign_keys=[SharedPost.from_user_id],back_populates="from_user")
      received_posts = relationship("SharedPost", foreign_keys=[SharedPost.to_user_id],back_populates="to_user")
class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True),server_default=func.now())
    is_read = Column(Boolean,default=False)