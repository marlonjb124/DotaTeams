# REST API Refactoring Design Document

## 1. Overview

This document outlines the refactoring of the current API to follow REST conventions more closely and implement API versioning with a "v1" prefix. The current API has several endpoints that don't follow REST best practices, and there's no versioning strategy in place.

### Current Issues
- Inconsistent endpoint naming (mix of PascalCase and snake_case)
- Non-RESTful endpoint patterns (e.g., `/CreateTournament` instead of `POST /tournaments`)
- Lack of API versioning
- Inconsistent response formats
- Non-standard HTTP status codes usage

### Refactoring Goals
- Implement RESTful API design principles
- Add API versioning with `/v1` prefix
- Standardize endpoint naming conventions
- Improve resource-based URL structure
- Maintain backward compatibility during transition
- Improve API documentation and developer experience

### Success Metrics
- All endpoints follow REST conventions
- Consistent error response format
- Proper HTTP status code usage
- Improved API documentation
- Successful testing of all endpoints
- Zero breaking changes for existing clients during transition

### Implementation Approach
- Create new v1 API endpoints in parallel with existing endpoints
- Update routing structure to follow REST conventions
- Maintain existing endpoints during transition period
- Update documentation and examples
- Implement comprehensive testing

## 2. Architecture

The refactored API will follow these architectural principles:
- RESTful resource-based design
- Proper HTTP methods usage (GET, POST, PUT, PATCH, DELETE)
- Standard HTTP status codes
- Consistent JSON response format
- API versioning with `/v1` prefix
- Proper resource relationships and nested routes where appropriate

### New URL Structure
All endpoints will be prefixed with `/api/v1` to indicate version 1 of the API.

### REST Principles Applied
- Use nouns instead of verbs in endpoint paths
- Use plural nouns for collections (e.g., `/users` not `/user`)
- Use HTTP methods for CRUD operations
- Use proper status codes (2xx for success, 4xx for client errors, 5xx for server errors)
- Use nested URLs for relationships (e.g., `/teams/{team_id}/members`)
- Use query parameters for filtering, sorting, and pagination

### HTTP Method Usage
- GET: Retrieve resources
- POST: Create resources
- PUT: Replace/update entire resources
- PATCH: Partially update resources
- DELETE: Remove resources

### API Versioning Strategy
- All new endpoints will be under `/api/v1/`
- Existing endpoints will remain functional during transition period
- Future versions will follow `/api/v2/`, `/api/v3/` pattern

## 3. API Endpoints Reference

### 3.1 User Endpoints

| Current Endpoint | New Endpoint | Method | Description | Status Codes |
|------------------|--------------|--------|-------------|---------------|
| `/Users/` | `/api/v1/users` | POST | Create a new user | 201, 400, 409 |
| `/Users/token` | `/api/v1/auth/login` | POST | User login and token generation | 200, 401 |
| `/Users/me` | `/api/v1/users/me` | GET | Get current user information | 200, 401 |
| `/Users/refresh` | `/api/v1/auth/refresh` | POST | Refresh access token | 200, 401 |

### 3.2 Team Endpoints

| Current Endpoint | New Endpoint | Method | Description | Status Codes |
|------------------|--------------|--------|-------------|---------------|
| `/Teams/` | `/api/v1/teams` | POST | Create a new team | 201, 400, 401, 403, 409 |
| `/Teams/{team_id}` | `/api/v1/teams/{team_id}` | DELETE | Delete a team | 200, 401, 403, 404 |
| `/Teams/Invite_user` | `/api/v1/teams/{team_id}/invitations` | POST | Invite a user to a team | 201, 400, 401, 403, 404, 409 |
| `/Teams/Acept_invitacion/{token}` | `/api/v1/teams/invitations/{token}/accept` | POST | Accept team invitation | 200, 400, 404 |
| `/Teams/{id_team}/Member/{tarjet_member_id}` | `/api/v1/teams/{team_id}/members/{member_id}` | DELETE | Remove member from team | 200, 401, 403, 404 |
| `/Teams/` | `/api/v1/teams` | GET | Get all teams | 200 |
| `/Teams/` | `/api/v1/teams/{team_id}` | PATCH | Update team information | 200, 400, 401, 403, 404 |

### 3.3 Tournament Endpoints

| Current Endpoint | New Endpoint | Method | Description | Status Codes |
|------------------|--------------|--------|-------------|---------------|
| `/Tournaments/CreateTournament` | `/api/v1/tournaments` | POST | Create a new tournament | 201, 400, 401, 403 |
| `/Tournaments/add_Team_Tournament/{tournament_id}` | `/api/v1/tournaments/{tournament_id}/teams` | POST | Add team to tournament | 201, 400, 401, 403, 404, 409 |
| `/Tournaments/` | `/api/v1/tournaments/{tournament_id}` | DELETE | Delete a tournament | 200, 401, 403, 404 |
| `/Tournaments/` | `/api/v1/tournaments` | GET | Get all tournaments | 200 |
| `/Tournaments/` | `/api/v1/tournaments/{tournament_id}` | PATCH | Update tournament information | 200, 400, 401, 403, 404 |

### 3.4 Profile Endpoints

| Current Endpoint | New Endpoint | Method | Description | Status Codes |
|------------------|--------------|--------|-------------|---------------|
| `/Profile/updateProfile` | `/api/v1/profiles/me` | PUT | Update current user profile | 200, 400, 401 |

## 4. Data Models & ORM Mapping

The data models will remain unchanged as part of this refactoring. Only the API endpoints and routing will be modified.

### Model Relationships
- Users have one Profile (One-to-One)
- Users belong to many Teams through UserTeam (Many-to-Many)
- Users have many Roles through UserRol (Many-to-Many)
- Teams are created by Users (One-to-Many)
- Teams participate in many Tournaments through TournamentTeam (Many-to-Many)
- Tournaments are created by Users (One-to-Many)
- Teams can invite Users through Invitations (One-to-Many)

## 5. Business Logic Layer

The business logic layer will remain largely unchanged. The controllers will be updated to work with the new routing structure, but the core functionality will remain the same.

### Key Changes
- Router paths will be updated to follow REST conventions
- API prefix `/api/v1` will be added to all endpoints
- Controller methods will be mapped to new endpoint paths
- Authentication and authorization logic will remain unchanged

### Controller Updates
- `userController.py` - Update route mappings
- `teamController.py` - Update route mappings
- `profileController.py` - Update route mappings
- No changes to business logic implementation

### Router Updates
- `user.py` → Create new `v1/user.py` router
- `team.py` → Create new `v1/team.py` router
- `tournaments.py` → Create new `v1/tournaments.py` router
- `profile.py` → Create new `v1/profile.py` router
- Update `api.py` to include new v1 routers

### Implementation Steps
1. Create new directory structure for v1 API
2. Copy and modify existing routers to new v1 structure
3. Update endpoint paths to follow REST conventions
4. Add `/api/v1` prefix to all new endpoints
5. Update controller method calls as needed
6. Implement comprehensive testing
7. Update API documentation
8. Deploy and monitor during transition period

## 6. Middleware & Interceptors

Existing middleware components will be preserved:
- Rate limiting middleware (SlowAPI)
- CORS middleware
- Authentication middleware
- Exception handlers

### New Middleware Considerations
- Request logging for API v1
- API version negotiation
- Response formatting middleware for consistent JSON responses

### Existing Middleware Preservation
- Rate limiting middleware (SlowAPI) will apply to v1 endpoints
- CORS middleware will be updated to handle v1 routes
- Authentication middleware will work with new endpoint structure
- Exception handlers will be maintained for consistent error responses

## 7. Testing

Unit tests will need to be updated to reflect the new endpoint URLs:
- All endpoint URLs in tests will be updated with `/api/v1` prefix
- Test cases for new RESTful patterns will be added
- Authentication tests will be updated to use new auth endpoints

### Test Updates Required
- Update URL paths in all existing tests
- Add tests for new endpoint structures
- Verify status codes match REST conventions
- Test backward compatibility during transition period

### Testing Strategy
1. Create new test files for v1 API endpoints
2. Maintain existing tests temporarily for backward compatibility
3. Implement integration tests for critical user flows
4. Performance tests to ensure no degradation with new routing

### Backward Compatibility
- Existing endpoints will remain functional during transition period
- New v1 endpoints will run in parallel with existing endpoints
- Deprecation timeline will be established for old endpoints
- Documentation will clearly indicate which endpoints are deprecated

### Example Requests/Responses

#### User Registration
```
POST /api/v1/users
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe"
}
```

Response:
```
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2023-01-01T00:00:00Z"
}
```

#### Team Creation
```
POST /api/v1/teams
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Development Team",
  "description": "Team responsible for development"
}
```

Response:
```
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": 1,
  "name": "Development Team",
  "description": "Team responsible for development",
  "creator_id": 1,
  "created_at": "2023-01-01T00:00:00Z"
}
```