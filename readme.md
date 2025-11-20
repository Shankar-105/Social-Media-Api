# 🚀 SocialMediaApi
**Modern Social Media Backend + Real-time Chat – Scalable, Fast, and Beginner-Friendly**

A full-featured social media **backend API** with **real-time 1-on-1 chat**, built using FastAPI, SQLAlchemy, Alembic migrations, PostgreSQL, and JWT authentication.  
Supports file uploads, instant messaging via WebSockets, and everything you need for an impressive, social experience!

---

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.119+-green?logo=fastapi)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-yellow?logo=sqlalchemy)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue?logo=postgresql)
![WebSockets](https://img.shields.io/badge/WebSockets-Realtime-blue?logo=websocket)
![Authentication](https://img.shields.io/badge/Auth-JWT-orange?logo=jsonwebtokens)
![License](https://img.shields.io/badge/License-MIT-purple)

---

## 🌟 Features — What’s Inside?

### 🎉 Social API

- 📝 **User Registration & Login**
    - Secure password hashing (bcrypt)
    - JWT access tokens with expiry prevents attackers
    - Password reset via email OTP
    - Change password (OTP verification)
- 👤 **Profile System**
    - Bio, nickname
    - Profile picture upload/remove
    - Update username & info
- 🔗 **Follow / Unfollow**
    - Followers/following lists & counts
    - View lists
- 📰 **Posts**
    - Create, read, update, delete posts (text + **media**: images/videos)
    - File uploads for post media
    - Likes/dislikes with toggle logic
    - Post analytics (views counter)
    - Comment on posts (**full CRUD**)
    - Vote/like comments
    - Share posts into DMs
    - Home feed (from people you follow + pagination)
- 🔍 **Search**
    - Search users & posts
    - Hashtag support (#example)
- 📦 **Data Organization**
    - Local folders auto-created: `profilepics/`, `posts_media/`, `chat-media/`
- 🏅 **Analytics**
    - See your vote stats, comment stats, and post engagement

---

### 💬 Real-Time Chat System (WebSockets)

- 📨 **1-on-1 Direct Messages**
    - Instant delivery, offline queues
    - Send text, images, videos, audio, documents
- 🔥 **Live Features**
    - Typing indicators
    - Online/offline status (ping-pong heartbeat)
    - Read receipts
    - Message reactions (emoji)
    - Full chat history (including missed messages)
- 🔄 **Advanced Message Controls**
    - Reply to any message (and shared posts)
    - Quote messages
    - Edit messages (rate limited)
    - Delete for me / Delete for everyone (“unsend”)
    - Proper message ordering, filtering of deleted/edited messages
- ✅ **Robust Delivery**
    - Connection management (ping-pong, zombie detection)
    - All messages synced and stored
---