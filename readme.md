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
## 🚦 Getting Started — Be Up in 5 Minutes!

### 1. Clone the repository

```bash
git clone https://github.com/Shankar-105/Social-Media-Api.git
cd Social-Media-Api
```

### 2. Create & Activate a Virtual Environment

| OS      | Command                                                    |
|---------|------------------------------------------------------------|
| **Windows**     | `python -m venv venv && venv\Scripts\activate`    |
| **macOS/Linux** | `python3 -m venv venv && source venv/bin/activate`|

### 3. Install All Python Dependencies

> 💡 **Now it's time to install the dependencies for the api need to work. To install all the depedencies with one command you will already have the requirements.txt from the clone , So just do!**

```bash
pip install -r requirements.txt
```
> **_And all the required dependencies will be installed all at a once_**
---

> ⚠️ **Alert for the Windows Users:**  
If you encounter a build error with `psycopg2-binary` (**the postgres driver**) like:  
`error: Microsoft Visual C++ 14.0 or greater is required...`  
You need to install the C++ Build Tools from Visual Studio:

- Download & install the [Build Tools for Visual Studio](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- Install the “C++ build tools” workload (default options are fine , Search the internet if still confused).
- After install, in a **new terminal**, run:
    ```bash
    python -m pip install --upgrade pip setuptools wheel
    python -m pip install -r requirements.txt
    ```
---

### 4. Database Integration & Driver
- Now your done with getting into the venv and installing all the dependencies required and now it's time for the db integration.
- You’ll need a database installed inorder to store the data and the api to work. (Like PostgreSQL , MySql etc).

- you need to know your **Host Name/address ,Port (the database port like 5432 for postgresql) , the password and the username**
- after your clear with all these things create a database in it for example `social_media`

- **Link your database credentials in the <kbd>app/db.py</kbd> and <kbd>.env</kbd>! (mentioned below)**

- Sqlalchemy supports many databases but for each database it requires it's own specific driver to be installed with it. If you use PostgreSQL, the required driver (`psycopg2-binary`) is already included and installed above in the requirements.txt.

- **Other databases?**  
    - **MySQL:**  
      ```bash
      pip install pymysql
      ```
    - **SQLite:**  
      _Driver built-in, just change connection string accordingly._
    - Make sure to update your <kbd>app/db.py</kbd> to point at the correct DB.

---

### 5. Environment Variables Setup (.env)

> Copy this to your `.env` and fill in values.  
> **Required keys:** (match your local DB settings)

```ini
DATABASE_HOST="your-hostname"
DATABASE_PORT=5432 # postgres port
DATABASE_PASSWORD="your-db-password"
DATABASE_USER="your-db-username"
DATABASE_NAME="your-database-name" # like the social_media i have suggested above

SECRET_KEY="your-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_TIME=30

EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_specific_email_password
EMAIL_FROM=your_email@gmail.com
EMAIL_PORT=587
EMAIL_SERVER=smtp.gmail.com

BASE_URL="http://127.0.0.1:8000"
MEDIA_FOLDER="posts_media"
MAX_EDIT_TIME=15
```
_Note: These are auto-imported via Pydantic Settings and used in config/db throughout the backend._

---

### 6. Prepare Local Folders

```bash
mkdir profilepics posts_media chat-media
```

> These folders auto-store profile pictures, post media, and chat files locally. They'll be auto-created if missing.

---

### 7. Run the Server!

```bash
uvicorn app.main:app --reload
```
Server will be live at [http://127.0.0.1:8000](http://127.0.0.1:8000)

---
### 8. (Recommended) Database Migration Setup  
**Use Alembic for SQL migrations.**

```bash
pip install alembic
alembic init alembic
```
Edit `alembic.ini` and `alembic/env.py` to match your database configuration (refer internet for easy walkthroughs if beginner).

- Generate a migration:
    ```bash
    alembic revision --autogenerate -m "Initial migration"
    alembic upgrade head
    ```

---
