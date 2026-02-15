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
