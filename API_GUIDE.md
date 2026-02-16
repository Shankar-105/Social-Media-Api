# 📖 API Guide — Complete Endpoint Reference

> **Your one-stop reference for every REST and WebSocket endpoint in the SocialMediaApi.**

---

## ⚠️ Before You Begin

Before calling **any** endpoint, make sure you have:

1. ✅ Completed the full **[SETUP.md](./SETUP.md)** — cloned the repo, configured `.env`, and prepared local folders.
2. ✅ Docker containers are **running** — `docker compose up -d` and verified via `http://localhost:8000/health`.
3. ✅ A tool to make HTTP requests — **[Postman](https://www.postman.com/)**, **[Insomnia](https://insomnia.rest/)**, **cURL**, **HTTPie**, or the built-in **Swagger UI** at `http://localhost:8000/docs`.

> 💡 **Tip:** FastAPI auto-generates interactive API docs. Visit **`http://localhost:8000/docs`** (Swagger UI) or **`http://localhost:8000/redoc`** (ReDoc) to explore and test endpoints right from your browser.

---

## 🔑 Authentication — How It Works

Most endpoints require a **JWT Bearer Token**. Here's the flow:

1. **Sign up** → `POST /user/signup`
2. **Log in** → `POST /login` → you receive an `accessToken`
3. **Use the token** in subsequent requests:
   - **Header:** `Authorization: Bearer <your_access_token>`
   - **Postman:** Go to the *Authorization* tab → select *Bearer Token* → paste your token.
   - **cURL:** `curl -H "Authorization: Bearer <token>" http://localhost:8000/me/profile`

> 🔒 Endpoints marked with 🔐 require authentication. Public endpoints are marked with 🌐.

---

## 📑 Table of Contents

| Section | Description |
|---------|-------------|
| [Health Check](#-health-check) | Verify the API is running |
| [Authentication](#-authentication) | Sign up & log in |
| [My Profile (me)](#-my-profile-me) | View/update your own profile, posts, stats |
| [Users](#-users) | View other users, their posts, followers |
| [Posts](#-posts) | Create, read, update, delete posts |
| [Comments](#-comments) | Comment on posts (CRUD) |
| [Votes / Likes](#-votes--likes) | Like/dislike posts and comments |
| [Connections](#-connections-followunfollow) | Follow, unfollow, remove followers |
| [Feed](#-feed) | Home feed & explore |
| [Search](#-search) | Search users & hashtags |
| [Password Management](#-password-management) | Change/reset password via OTP |
| [Chat — Share Posts](#-chat--share-posts) | Share posts into DMs |
| [Chat — Media Upload](#-chat--media-upload) | Upload images/videos/audio for chat |
| [Chat — Message Info & Reactions](#-chat--message-info--reactions) | Message details, reactions |
| [Chat — Delete & Clear](#-chat--delete--clear) | Delete messages, shares, clear chat |
| [Chat — Edit Messages](#-chat--edit-messages) | Check edit eligibility |
| [WebSocket — Real-Time Chat](#-websocket--real-time-chat) | Live messaging, typing, reactions |

---

## 💚 Health Check

| Detail | Value |
|--------|-------|
| **Endpoint** | `GET /health` |
| **Auth** | 🌐 None |
| **Description** | Quick check to see if the API server is alive. |

**Example — cURL:**
```bash
curl http://localhost:8000/health
```

**Response — `200 OK`:**
```json
{
  "message": "fine"
}
```

---
## 🔐 Authentication

### 1. Sign Up

| Detail | Value |
|--------|-------|
| **Endpoint** | `POST /user/signup` |
| **Auth** | 🌐 None |
| **Content-Type** | `application/json` |
| **Description** | Register a new user account. |

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "securePass123",
  "nickname": "Johnny",
  "email": "john@example.com"
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `username` | string | ✅ | 3–50 chars, must be unique |
| `password` | string | ✅ | 6–72 chars, stored hashed (bcrypt) |
| `nickname` | string | ❌ | Max 50 chars |
| `email` | string | ❌ | Valid email format |

**Response — `201 Created`:**
```json
{
  "id": 1,
  "username": "john_doe",
  "created_at": "2026-02-09T10:30:00.000Z"
}
```

---

### 2. Log In

| Detail | Value |
|--------|-------|
| **Endpoint** | `POST /login` |
| **Auth** | 🌐 None |
| **Content-Type** | `application/x-www-form-urlencoded` |
| **Description** | Authenticate and receive a JWT access token. |

**Request Body (form data):**
| Field | Type | Required |
|-------|------|----------|
| `username` | string | ✅ |
| `password` | string | ✅ |

**cURL Example:**
```bash
curl -X POST http://localhost:8000/login \
  -d "username=john_doe&password=securePass123"
```

**Response — `202 Accepted`:**
```json
{
  "id": 1,
  "username": "john_doe",
  "accessToken": "eyJhbGciOiJIUzI1NiIs...",
  "tokenType": "bearer"
}
```

> 📌 **Save the `accessToken`!** You'll need it as a Bearer token for all authenticated endpoints.

---

## 👤 My Profile (me)

All `/me/*` endpoints operate on the **currently authenticated user**.

### 1. Get My Profile

| Detail | Value |
|--------|-------|
| **Endpoint** | `GET /me/profile` |
| **Auth** | 🔐 Bearer Token |
| **Description** | Retrieve your complete profile information. |

**Response — `200 OK`:**
```json
{
  "id": 1,
  "username": "john_doe",
  "nickname": "Johnny",
  "bio": "Hello world!",
  "profile_picture": "john_doe_avatar.png",
  "posts_count": 5,
  "followers_count": 12,
  "following_count": 8,
  "created_at": "2026-02-09T10:30:00.000Z"
}
```

---

### 2. Get My Profile Picture

| Detail | Value |
|--------|-------|
| **Endpoint** | `GET /me/profile/pic` |
| **Auth** | 🔐 Bearer Token |
| **Description** | Get the URL of your current profile picture. |

**Response — `200 OK`:**
```json
{
  "url": "http://localhost:8000/profilepics/john_doe_avatar.png",
  "type": "image"
}
```

> Returns `404` if no profile picture is set.

---
### 3. Delete My Profile Picture

| Detail | Value |
|--------|-------|
| **Endpoint** | `DELETE /me/profilepic/delete` |
| **Auth** | 🔐 Bearer Token |
| **Description** | Remove your current profile picture. |

**Response — `200 OK`:**
```json
{
  "message": "Profile picture removed successfully"
}
```

---

### 4. Update My Info

| Detail | Value |
|--------|-------|
| **Endpoint** | `PATCH /me/updateInfo` |
| **Auth** | 🔐 Bearer Token |
| **Content-Type** | `multipart/form-data` |
| **Description** | Update username, bio, and/or profile picture. All fields are optional. |

**Form Fields:**
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `username` | string | ❌ | New username (must be unique) |
| `bio` | string | ❌ | Your bio text |
| `profile_picture` | file | ❌ | JPEG, PNG, or GIF only |

**cURL Example:**
```bash
curl -X PATCH http://localhost:8000/me/updateInfo \
  -H "Authorization: Bearer <token>" \
  -F "bio=I love coding!" \
  -F "profile_picture=@/path/to/avatar.png"
```

**Response — `200 OK`:** Returns the full updated `UserProfileResponse`.

---

### 5. Get My Posts

| Detail | Value |
|--------|-------|
| **Endpoint** | `GET /me/posts` |
| **Auth** | 🔐 Bearer Token |
| **Description** | Retrieve all your posts with pagination. |

**Query Parameters:**
| Param | Type | Default | Notes |
|-------|------|---------|-------|
| `limit` | int | `10` | 1–100 |
| `offset` | int | `0` | Skip N posts |

**Response — `200 OK`:**
```json
{
  "posts": [
    {
      "id": 1,
      "title": "My first post!",
      "media_url": "http://localhost:8000/posts_media/abc.jpg",
      "media_type": "image",
      "likes": 5,
      "comments_count": 2,
      "created_at": "2026-02-09T12:00:00.000Z",
      "is_liked": true
    }
  ],
  "pagination": {
    "total": 1,
    "limit": 10,
    "offset": 0,
    "has_more": false
  }
}
```

---