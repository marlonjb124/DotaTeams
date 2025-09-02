# Equipos

Equipos is a backend service built with FastAPI for managing teams, users, tournaments, and related entities in a structured web application. The system supports role-based access control, team invitations, and tournament management, making it suitable for sports or competitive platforms.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
  - [User Management](#user-management)
  - [Team Management](#team-management)
  - [Tournament Management](#tournament-management)
- [Authentication & Authorization](#authentication--authorization)
- [Setup and Installation](#setup-and-installation)
  - [Prerequisites](#prerequisites)
  - [Installation Steps](#installation-steps)
- [Database Migrations](#database-migrations)
- [Deployment](#deployment)
- [Security Features](#security-features)
- [Known Issues and Considerations](#known-issues-and-considerations)

## Overview

Equipos is a comprehensive backend solution designed for managing team-based competitive platforms. It provides a robust foundation for applications that require user management, team creation and administration, tournament organization, and role-based access control.

## Key Features

- User management (registration, roles, authentication)
- Team creation and membership management
- Tournament organization and team participation
- Role-based access control (RBAC)
- Token-based authentication (JWT and refresh tokens)
- Database migrations via Alembic
- Team invitation system with token-based acceptance
- Refresh token management for persistent sessions

## Technology Stack

- **Backend Framework**: FastAPI (v0.115.11) with Uvicorn (v0.34.0) ASGI server
- **Database & ORM**: SQLAlchemy (v2.0.39) with PostgreSQL (psycopg2-binary v2.9.10)
- **Authentication & Security**: PyJWT (v2.10.1), bcrypt (v4.3.0)
- **Validation**: Pydantic (v2.10.6)
- **Rate Limiting**: SlowAPI (v0.1.9)
- **Deployment**: Vercel-ready with serverless configuration

## Project Structure

```
.
├── alembic/                  # Database migrations
│   ├── versions/             # Migration scripts
│   └── env.py                # Alembic configuration
├── app/                      # Main application code
│   ├── controllers/          # Business logic
│   ├── database/             # Database configuration
│   ├── models/               # SQLAlchemy models
│   ├── routers/              # API endpoints
│   ├── schemas/              # Pydantic schemas for validation
│   ├── utils/                # Utility functions
│   └── api.py                # Main FastAPI application
├── .env                      # Environment variables
├── alembic.ini               # Alembic configuration
├── main.py                   # Application entry point
├── migrate_lambda.py         # Lambda migration handler
└── vercel.json               # Vercel deployment configuration
```

## Database Schema

The project uses a PostgreSQL database with the following main entities:

### Core Entities

- **Users**: Registered users with email, password, and active status
- **Profiles**: User profile information
- **Roles**: User roles for access control (Super_admin, Admin, Team_gestor, Basic_user)
- **Teams**: User-created teams with descriptions
- **Tournaments**: Competitions that teams can participate in
- **Invitations**: Team invitations sent to users
- **Refresh Tokens**: Tokens for maintaining user sessions

### Relationships

- Users can create teams and tournaments
- Users can belong to multiple teams
- Teams can participate in multiple tournaments
- Users can have multiple roles
- Users can invite other users to teams

### Database Schema Diagram

```mermaid
erDiagram
    USERS ||--o{ TEAMS : creates
    USERS ||--o{ TOURNAMENTS : creates
    USERS ||--o{ PROFILES : has
    USERS ||--o{ REFRESH_TOKENS : has
    USERS }o--o{ TEAMS : members
    USERS }o--o{ ROLES : has
    TEAMS }o--o{ TOURNAMENTS : participates_in
    USERS ||--o{ INVITACIONES : sends
    TEAMS ||--o{ INVITACIONES : receives
```

## API Endpoints

### User Management

| Endpoint | Method | Description | Authentication |
|---------|--------|-------------|----------------|
| `/Users/` | POST | Register a new user | None |
| `/Users/token` | POST | User login and token generation | None |
| `/Users/me` | GET | Get current user information | Bearer Token |
| `/Users/refresh` | POST | Refresh access token | Refresh Token |
| `/Users/logout` | POST | Logout and revoke refresh token | Bearer Token |
| `/Users/Roles/` | GET | Get all roles | Admin Role |
| `/Users/Assign_role` | POST | Assign a role to a user | Admin Role |
| `/Users/{user_id}` | GET | Get specific user by ID | Authenticated User |
| `/Users/` | GET | Get all users | Authenticated User |

### Team Management

| Endpoint | Method | Description | Authentication |
|---------|--------|-------------|----------------|
| `/Teams/` | POST | Create a new team | Basic User Role |
| `/Teams/{team_id}` | DELETE | Delete a team | Team Creator |
| `/Teams/Invite_user` | POST | Invite a user to a team | Team Manager Role |
| `/Teams/Acept_invitacion/{token}` | POST | Accept a team invitation | Basic User Role |
| `/Teams/{id_team}/Member/{tarjet_member_id}` | DELETE | Remove a member from a team | Team Manager Role |
| `/Teams/` | GET | Get all teams | Authenticated User |
| `/Teams/` | PATCH | Update team information | Team Manager Role |

### Tournament Management

| Endpoint | Method | Description | Authentication |
|---------|--------|-------------|----------------|
| `/Tournaments/CreateTournament` | POST | Create a new tournament | Admin Role |
| `/Tournaments/add_Team_Tournament/{tournament_id}` | POST | Add a team to a tournament | Admin Role |
| `/Tournaments/` | DELETE | Delete a tournament | Admin Role |
| `/Tournaments/` | GET | Get all tournaments | Authenticated User |
| `/Tournaments/` | PATCH | Update tournament information | Admin Role |

## Authentication & Authorization

The system uses JWT tokens for authentication with role-based access control:

### User Roles

- **Super_admin**: Full system access
- **Admin**: Tournament management
- **Team_gestor**: Team management permissions
- **Basic_user**: Standard user permissions

### Token Security

- Access tokens with short expiration times
- Refresh tokens for session management
- Secure HTTP-only cookies for fingerprinting
- Token revocation for logout functionality

## Setup and Installation

### Prerequisites

- Python 3.9+
- PostgreSQL database
- Virtual environment tool (venv or conda)

### Installation Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Equipos
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables in `.env`:
   ```env
   DATABASE_URL="postgresql://user:password@host:port/database"
   Super_admin_email="admin@example.com"
   Super_admin_psw="Super_admin"
   LOCAL_DATABASE_URL="postgresql://postgres:postgres@localhost:5432/basedato"
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the development server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## Database Migrations

Alembic is used for database migrations:

- Migration scripts are stored in `alembic/versions/`
- Initial migration creates all tables and relationships
- Subsequent migrations add features like refresh tokens

To create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

To apply migrations:
```bash
alembic upgrade head
```

## Deployment

The application is configured for deployment on Vercel:

1. Push the code to a GitHub repository
2. Connect the repository to Vercel
3. Set environment variables in Vercel dashboard
4. Deploy the application

The `vercel.json` configuration specifies:
- Build configuration using `@vercel/python`
- Routing all requests to `app/api.py`
- Lambda size limit of 15mb

For database migrations on Vercel, use the `migrate_lambda.py` handler.

## Security Features

- Password hashing with bcrypt
- JWT token authentication
- Role-based access control
- Secure HTTP-only cookies
- Rate limiting with SlowAPI
- CORS middleware configuration
- Token revocation for secure logout

## Known Issues and Considerations

- The project is backend-only with no frontend included
- Some dependencies may be outdated
- Migration scripts may require manual review
- Deployment to Vercel may need adjustments for persistent database connections
- Error handling in some endpoints could be improved
- Some commented-out code and debug print statements exist in the codebase