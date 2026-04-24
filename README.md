# Wasel Palestine

A backend API for a smart mobility and checkpoint intelligence platform built for the West Bank. The system allows citizens to report road incidents, track checkpoint statuses, receive alerts, and estimate safe travel routes in real time.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Database Schema](#database-schema)
4. [API Design](#api-design)
5. [External Integrations](#external-integrations)
6. [Environment Variables](#environment-variables)
7. [Getting Started](#getting-started)

---

## System Overview

Wasel Palestine exposes a versioned REST API (`/api/v1`) built with FastAPI. It serves three types of clients: regular citizens, moderators, and administrators. The platform handles user authentication, checkpoint monitoring, incident reporting, community moderation, alert subscriptions, and route estimation.

All responses follow a unified envelope format:

```json
{
  "success": true,
  "message": "...",
  "data": {}
}
```

---

## Architecture

```
┌─────────┐
│ Client  │
└────┬────┘
     │ HTTPS
     ▼
┌──────────────────────────────────────────────────────────────┐
│  CORS Middleware                                             │
├──────────────────────────────────────────────────────────────┤
│  FastAPI + Uvicorn (:8000)                                   │
│                                                              │
│  Endpoints (app/api/v1/)          Services (app/services/)   │
│  ─────────────────────────────    ────────────────────────   │
│  /auth       → JWT · Argon2   →   AuthService                │
│  /users      → RBAC guards    →   UserService                │
│  /checkpoints                 →   CheckpointService          │
│  /incidents                   →   IncidentService            │
│  /reports                     →   ReportService              │
│  /moderation → Admin only     →   ReportService              │
│  /alerts                      →   AlertService               │
│  /routes     → async          →   RouteService ──────────┐   │
│  /health                                                 │   │
└──────────────────────┬───────────────────────────────────┼───┘
                       │                                   │
          ┌────────────┴──────────┐               ┌────────┴────────────┐
          │                       │               │  External APIs      │
          ▼                       ▼               │ ··················· │
 ┌─────────────────┐   ┌──────────────────┐       │  OpenRouteService   │
 │  PostgreSQL 16  │   │    Redis 7       │       │  OpenWeatherMap     │
 │  (SQLAlchemy +  │   │  (route result   │       │ ··················· │
 │   Alembic)      │   │   cache)         │       └─────────────────────┘
 └─────────────────┘   └──────────────────┘
```


**Stack:**

| Layer       | Technology              |
|-------------|-------------------------|
| Framework   | FastAPI 0.135           |
| Server      | Uvicorn                 |
| ORM         | SQLAlchemy 2.0          |
| Database    | PostgreSQL 16           |
| Cache       | Redis 7                 |
| Auth        | JWT (PyJWT + Argon2)    |
| Migrations  | Alembic                 |
| Validation  | Pydantic v2             |
| Container   | Docker + Docker Compose |

---

## Database Schema

<img width="799" height="883" alt="wasel_db_erd" src="https://github.com/user-attachments/assets/46718ee1-f5ec-4f8b-aa04-6f0fb72ce027" />

**Core tables:**

| Table                   | Description                                      |
|-------------------------|--------------------------------------------------|
| `users`                 | Accounts with roles: user, moderator, admin      |
| `refresh_tokens`        | Stored hashed refresh tokens per session         |
| `checkpoints`           | Physical checkpoint locations and current status |
| `checkpoint_status_history` | Audit log of every status change             |
| `incidents`             |User-reported field incidents with geo-coordinates|
| `reports`               | Community reports with abuse detection and voting|
| `report_votes`          | Upvote/downvote records per user per report      |
| `moderation_logs`       | Full audit trail of all moderator actions        |
| `alerts`                | System alerts triggered by verified incidents    |
| `alert_subscriptions`   | User subscriptions to geo-area alerts            |

---

## API Design

**Versioning:** All routes are prefixed with `/api/v1`.

**Authentication:** Bearer token (JWT). Access tokens expire in 30 minutes. Refresh tokens expire in 7 days and are stored as hashed values.

**Authorization levels:**

| Role       | Access                                                    |
|------------|-----------------------------------------------------------|
| Public     | List checkpoints, list incidents, list alerts, health     |
| User       | Authenticated endpoints: report, vote, subscribe, profile |
| Moderator  | All user access + approve/reject reports, update incidents|
| Admin      | Full access including user management and deletions       |

**Pagination:** All list endpoints accept `page` and `page_size` query parameters and return a consistent paginated envelope.

**Error responses:** All errors return `{ "success": false, "message": "...", "data": null }` with the appropriate HTTP status code.

**Design decisions:**

- Soft-delete is used for user deactivation — accounts are flagged inactive, not removed.
- Incident verification automatically triggers alert creation.
- Report submission includes automatic duplicate detection using haversine distance within a 0.5 km radius.
- The report abuse check limits users to 10 submissions per hour via a DB count query.
- Credibility scoring exists on user accounts (managed via report voting).

---

## External Integrations

**1. OpenRouteService**

Used for: route distance and duration estimation between two coordinates.
Endpoint called: `https://api.openrouteservice.org/v2/directions/driving-car`
Key: `OPENROUTESERVICE_API_KEY` in `.env`

**2. OpenWeatherMap**

Used for: fetching current weather conditions along a route.
Endpoint called: `https://api.openweathermap.org/data/2.5/weather`
Key: `OPENWEATHER_API_KEY` in `.env`

Both external calls are made inside `POST /api/v1/routes/estimate`. Results are cached in Redis to avoid redundant API calls for identical coordinate pairs.

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values before running the project.

| Variable                      | Description                              |
|-------------------------------|------------------------------------------|
| `DATABASE_URL`                | PostgreSQL connection string             |
| `POSTGRES_USER`               | PostgreSQL username                      |
| `POSTGRES_PASSWORD`           | PostgreSQL password                      |
| `POSTGRES_DB`                 | PostgreSQL database name                 |
| `SECRET_KEY`                  | JWT signing secret                       |
| `ALGORITHM`                   | JWT algorithm (default: HS256)           |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL (default: 30)           |
| `REFRESH_TOKEN_EXPIRE_DAYS`   | Refresh token TTL (default: 7)           |
| `REDIS_URL`                   | Redis connection string                  |
| `OPENWEATHER_API_KEY`         | OpenWeatherMap API key                   |
| `OPENROUTESERVICE_API_KEY`    | OpenRouteService API key                 |
| `APP_ENV`                     | Environment: development / production    |

---

## Getting Started

**Requirements:** Docker and Docker Compose.

```bash
git clone https://github.com/AlaaArmoush/wasel-palestine.git
cd wasel-palestine
cp .env.example .env
docker compose up --build
```

**Run migrations manually (if needed):**

```bash
docker exec -it wasel_api alembic upgrade head
```

The API will be available at `http://localhost:8000`.

Interactive docs: `http://localhost:8000/api/docs`


