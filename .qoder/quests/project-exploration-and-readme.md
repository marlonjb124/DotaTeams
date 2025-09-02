# Equipos Project

## Overview

Equipos is a backend service built with FastAPI for managing teams, users, tournaments, and related entities in a structured web application. The system supports role-based access control, team invitations, and tournament management, making it suitable for sports or competitive platforms.

## Key Features

- User management (registration, roles, authentication)
- Team creation and membership management
- Tournament organization and team participation
- Role-based access control (RBAC)
- Token-based authentication (JWT and refresh tokens)
- Database migrations via Alembic

## Technology Stack

- **Backend Framework**: FastAPI (v0.115.11) with Uvicorn (v0.34.0) ASGI server
- **Database & ORM**: SQLAlchemy (v2.0.39) with PostgreSQL (psycopg2-binary v2.9.10)
- **Authentication & Security**: PyJWT (v2.10.1), bcrypt (v4.3.0)
- **Validation**: Pydantic (v2.10.6)
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

- **Users**: Registered users with email, password, and active status
- **Profiles**: User profile information
- **Roles**: User roles for access control (Super_admin, Admin, Team_gestor, Basic_user)
- **Teams**: User-created teams with descriptions
- **Tournaments**: Competitions that teams can participate in
- **Invitations**: Team invitations sent to users
- **Refresh Tokens**: Tokens for maintaining user sessions

Relationships include:
- Users can create teams and tournaments
- Users can belong to multiple teams
- Teams can participate in multiple tournaments
- Users can have multiple roles
- Users can invite other users to teams

## API Endpoints

### User Management
- `POST /Users/` - Register a new user
- `POST /Users/token` - User login and token generation
- `GET /Users/me` - Get current user information
- `POST /Users/refresh` - Refresh access token

### Team Management
- `POST /Teams/` - Create a new team
- `DELETE /Teams/{team_id}` - Delete a team
- `POST /Teams/Invite_user` - Invite a user to a team
- `POST /Teams/Acept_invitacion/{token}` - Accept a team invitation
- `DELETE /Teams/{id_team}/Member/{tarjet_member_id}` - Remove a member from a team
- `GET /Teams/` - Get all teams
- `PATCH /Teams/` - Update team information

### Tournament Management
- `POST /Tournaments/CreateTournament` - Create a new tournament
- `POST /Tournaments/add_Team_Tournament/{tournament_id}` - Add a team to a tournament
- `DELETE /Tournaments/` - Delete a tournament
- `GET /Tournaments/` - Get all tournaments
- `PATCH /Tournaments/` - Update tournament information

## Authentication & Authorization

The system uses JWT tokens for authentication with role-based access control:

- **Super_admin**: Full system access
- **Admin**: Tournament management
- **Team_gestor**: Team management permissions
- **Basic_user**: Standard user permissions

Tokens are secured with:
- Access tokens with short expiration times
- Refresh tokens for session management
- Secure HTTP-only cookies for fingerprinting

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
   source venv/bin/activate  # On Windows: venv\Scripts\activate
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

## Development

### Code Structure

The application follows a layered architecture:
1. **API Layer** (`routers/`): FastAPI routers that define endpoints
2. **Business Logic Layer** (`controllers/`): Implementation of business rules
3. **Data Access Layer** (`models/`): SQLAlchemy models for database interaction
4. **Validation Layer** (`schemas/`): Pydantic schemas for request/response validation

### Database Migrations

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

## Security Features

- Password hashing with bcrypt
- JWT token authentication
- Role-based access control
- Secure HTTP-only cookies
- Rate limiting with SlowAPI
- CORS middleware configuration

## Known Issues and Considerations

- The project is backend-only with no frontend included
- Some dependencies may be outdated
- Migration scripts may require manual review
- Deployment to Vercel may need adjustments for persistent database connections│   ├── models/               # SQLAlchemy models
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

- **Users**: Registered users with email, password, and active status
- **Profiles**: User profile information
- **Roles**: User roles for access control (Super_admin, Admin, Team_gestor, Basic_user)
- **Teams**: User-created teams with descriptions
- **Tournaments**: Competitions that teams can participate in
- **Invitations**: Team invitations sent to users
- **Refresh Tokens**: Tokens for maintaining user sessions

Relationships include:
- Users can create teams and tournaments
- Users can belong to multiple teams
- Teams can participate in multiple tournaments
- Users can have multiple roles
- Users can invite other users to teams

## API Endpoints

### User Management
- `POST /Users/` - Register a new user
- `POST /Users/token` - User login and token generation
- `GET /Users/me` - Get current user information
- `POST /Users/refresh` - Refresh access token

### Team Management
- `POST /Teams/` - Create a new team
- `DELETE /Teams/{team_id}` - Delete a team
- `POST /Teams/Invite_user` - Invite a user to a team
- `POST /Teams/Acept_invitacion/{token}` - Accept a team invitation
- `DELETE /Teams/{id_team}/Member/{tarjet_member_id}` - Remove a member from a team
- `GET /Teams/` - Get all teams
- `PATCH /Teams/` - Update team information

### Tournament Management
- `POST /Tournaments/CreateTournament` - Create a new tournament
- `POST /Tournaments/add_Team_Tournament/{tournament_id}` - Add a team to a tournament
- `DELETE /Tournaments/` - Delete a tournament
- `GET /Tournaments/` - Get all tournaments
- `PATCH /Tournaments/` - Update tournament information

## Authentication & Authorization

The system uses JWT tokens for authentication with role-based access control:

- **Super_admin**: Full system access
- **Admin**: Tournament management
- **Team_gestor**: Team management permissions
- **Basic_user**: Standard user permissions

Tokens are secured with:
- Access tokens with short expiration times
- Refresh tokens for session management
- Secure HTTP-only cookies for fingerprinting

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
   source venv/bin/activate  # On Windows: venv\Scripts\activate
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

## Development

### Code Structure

The application follows a layered architecture:
1. **API Layer** (`routers/`): FastAPI routers that define endpoints
2. **Business Logic Layer** (`controllers/`): Implementation of business rules
3. **Data Access Layer** (`models/`): SQLAlchemy models for database interaction
4. **Validation Layer** (`schemas/`): Pydantic schemas for request/response validation

### Database Migrations

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

## Security Features

- Password hashing with bcrypt
- JWT token authentication
- Role-based access control
- Secure HTTP-only cookies
- Rate limiting with SlowAPI
- CORS middleware configuration

## Known Issues and Considerations

- The project is backend-only with no frontend included
- Some dependencies may be outdated
- Migration scripts may require manual review
- Deployment to Vercel may need adjustments for persistent database connections








































































































































































































