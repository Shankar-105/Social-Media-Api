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
### 6. Get Posts I Voted On

| Detail | Value |
|--------|-------|
| **Endpoint** | `GET /me/votedOnPosts` |
| **Auth** | 🔐 Bearer Token |
| **Description** | Lists all posts you have voted (liked or disliked) on. |

**Response — `200 OK`:**
```json
{
  "john_doe you have voted on posts": [
    {
      "post title": "Amazing sunset",
      "post id": "3",
      "post owner": "jane_doe"
    }
  ]
}
```

---

### 7. Get My Vote Stats

| Detail | Value |
|--------|-------|
| **Endpoint** | `GET /me/voteStats` |
| **Auth** | 🔐 Bearer Token |
| **Description** | See how many posts you've liked vs disliked. |

**Response — `200 OK`:**
```json
{
  "liked_posts_count": 15,
  "disliked_posts_count": 3
}
```

---

### 8. Get My Liked Posts

| Detail | Value |
|--------|-------|
| **Endpoint** | `GET /me/likedPosts` |
| **Auth** | 🔐 Bearer Token |
| **Description** | Lists all posts you have liked. |

**Response — `200 OK`:**
```json
{
  "john_doe your liked posts includes": [
    { "post id": 3, "post owner": "jane_doe" },
    { "post id": 7, "post owner": "alice" }
  ]
}
```

---

### 9. Get My Disliked Posts

| Detail | Value |
|--------|-------|
| **Endpoint** | `GET /me/dislikedPosts` |
| **Auth** | 🔐 Bearer Token |
| **Description** | Lists all posts you have disliked. |

**Response — `200 OK`:**
```json
{
  "john_doe your disliked posts includes": [
    { "post id": 5, "post owner": "bob" }
  ]
}
```

---

### 10. Get Posts I Commented On

| Detail | Value |
|--------|-------|
| **Endpoint** | `GET /me/commented-on` |
| **Auth** | 🔐 Bearer Token |
| **Description** | Lists all unique posts you've commented on. |

**Response — `200 OK`:**
```json
{
  "john_doe you have commented on posts": [
    {
      "post title": "Check this out",
      "post id": "4",
      "post owner": "alice"
    }
  ]
}
```

---

### 11. Get My Comment Stats

| Detail | Value |
|--------|-------|
| **Endpoint** | `GET /me/comment-stats` |
| **Auth** | 🔐 Bearer Token |
| **Description** | Get the total number of comments you've made and unique posts commented on. |

**Response — `200 OK`:**
```json
{
  "total_comments": 42,
  "unique_posts_commented": 18
}
```

---

## 👥 Users

### 1. Get All Users

| Detail | Value |
|--------|-------|
| **Endpoint** | `GET /users/getAllUsers` |
| **Auth** | 🌐 None |
| **Description** | Retrieve a list of all registered users. |

**Response — `201 Created`:**
```json
[
  {
    "id": 1,
    "username": "john_doe",
    "created_at": "2026-02-09T10:30:00.000Z"
  },
  {
    "id": 2,
    "username": "jane_doe",
    "created_at": "2026-02-09T11:00:00.000Z"
  }
]
```

---

### 2. Get User Profile

| Detail | Value |
|--------|-------|
| **Endpoint** | `GET /users/{user_id}/profile` |
| **Auth** | 🔐 Bearer Token |
| **Description** | View another user's profile. Includes `is_following` status. |

**Response — `200 OK`:**
```json
{
  "id": 2,
  "username": "jane_doe",
  "nickname": "Jane",
  "bio": "Photographer 📸",
  "profile_picture": "jane_avatar.png",
  "posts_count": 10,
  "followers_count": 50,
  "following_count": 30,
  "is_following": true,
  "created_at": "2026-02-09T11:00:00.000Z"
}
```

---

### 3. Get User Profile Picture

| Detail | Value |
|--------|-------|
| **Endpoint** | `GET /users/{user_id}/profile/pic` |
| **Auth** | 🔐 Bearer Token |
| **Description** | Get the profile picture URL of a specific user. |

**Response — `200 OK`:**
```json
{
  "url": "http://localhost:8000/profilepics/jane_avatar.png",
  "type": "image"
}
```

---

### 4. Get User's Posts

| Detail | Value |
|--------|-------|
| **Endpoint** | `GET /users/{user_id}/posts` |
| **Auth** | 🔐 Bearer Token |
| **Description** | Retrieve a specific user's posts with pagination. |

**Query Parameters:**
| Param | Type | Default | Notes |
|-------|------|---------|-------|
| `limit` | int | `10` | 1–100 |
| `offset` | int | `0` | Skip N posts |

**Response — `200 OK`:** Same structure as `GET /me/posts`.

---

### 5. Get User's Followers

| Detail | Value |
|--------|-------|
| **Endpoint** | `GET /users/{user_id}/followers` |
| **Auth** | 🔐 Bearer Token |
| **Description** | List all followers of a specific user. |

**Response — `200 OK`:**
```json
[
  {
    "id": 1,
    "username": "john_doe",
    "nickname": "Johnny",
    "profile_pic": "john_avatar.png",
    "is_following": false
  }
]
```

---

### 6. Get User's Following

| Detail | Value |
|--------|-------|
| **Endpoint** | `GET /users/{user_id}/following` |
| **Auth** | 🔐 Bearer Token |
| **Description** | List all users a specific user is following. |

**Response — `200 OK`:** Same structure as followers list.

---

## 📝 Posts

### 1. Create Post

| Detail | Value |
|--------|-------|
| **Endpoint** | `POST /posts/createPost` |
| **Auth** | 🔐 Bearer Token |
| **Content-Type** | `multipart/form-data` |
| **Description** | Create a new post with text and optional media (image/video). |

**Form Fields:**
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `title` | string | ✅ | Post title |
| `content` | string | ✅ | Post body text |
| `media` | file | ❌ | JPEG, PNG, or MP4 only |

**cURL Example:**
```bash
curl -X POST http://localhost:8000/posts/createPost \
  -H "Authorization: Bearer <token>" \
  -F "title=My first post" \
  -F "content=Hello world!" \
  -F "media=@/path/to/photo.jpg"
```

**Response — `201 Created`:**
```json
{
  "id": 1,
  "title": "My first post",
  "content": "Hello world!",
  "media_url": "http://localhost:8000/posts_media/abc123.jpg",
  "media_type": "image",
  "likes": 0,
  "dislikes": 0,
  "views": 0,
  "comments_count": 0,
  "enable_comments": true,
  "hashtags": null,
  "created_at": "2026-02-09T12:00:00.000Z",
  "owner": {
    "id": 1,
    "username": "john_doe",
    "nickname": "Johnny",
    "profile_pic": null
  }
}
```

---

### 2. Get Post by ID

| Detail | Value |
|--------|-------|
| **Endpoint** | `GET /posts/getPost/{postId}` |
| **Auth** | 🔐 Bearer Token |
| **Description** | Get full details of a specific post. Increments the view counter on first view. |

**Response — `200 OK`:** Full `PostDetailResponse` (same structure as create post response, plus `is_liked` field).

---

### 3. Edit Post

| Detail | Value |
|--------|-------|
| **Endpoint** | `PUT /posts/editPost/{postId}` |
| **Auth** | 🔐 Bearer Token |
| **Content-Type** | `application/json` |
| **Description** | Update the title, content, or other fields of your post. Only the post owner can edit. |

**Request Body (all fields optional):**
```json
{
  "title": "Updated title",
  "content": "Updated content"
}
```

**Response — `200 OK`:** Full `PostDetailResponse` with updated data.

---

### 4. Delete Post

| Detail | Value |
|--------|-------|
| **Endpoint** | `DELETE /posts/deletePost/{postId}` |
| **Auth** | 🔐 Bearer Token |
| **Description** | Permanently delete your post and its associated media file. |

**Response — `200 OK`:**
```json
{
  "message": "Post 1 deleted successfully"
}
```

---