# Task Management API - Backend

RESTful API for managing tasks with JWT-based authentication and user data isolation.

## Prerequisites

- Python 3.11 or higher
- PostgreSQL database (Neon Serverless PostgreSQL recommended)
- Git

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the backend directory:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database connection (Neon PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database?sslmode=require

# Application settings
ENVIRONMENT=development
LOG_LEVEL=INFO

# Authentication (IMPORTANT: Generate secure secret)
BETTER_AUTH_SECRET='your-secret-generated-with-openssl-rand-base64-32'

# CORS configuration
FRONTEND_URL=http://localhost:3000
```

**Generate BETTER_AUTH_SECRET:**
```bash
openssl rand -base64 32
```

**Important:** The `BETTER_AUTH_SECRET` must match the one in `frontend/.env.local` for JWT token verification to work.

### 4. Initialize Database

Create the Better Auth tables:

```bash
python create_auth_tables.py
```

This creates the following tables:
- `user` - User accounts
- `session` - User sessions
- `account` - Authentication credentials
- `verification` - Email verification tokens

### 5. Start Development Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

The API will be available at: http://localhost:8001

**Auto-generated documentation**:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Authentication

This API uses JWT (JSON Web Tokens) for authentication. All task endpoints require a valid JWT token in the Authorization header.

### Authentication Flow

1. **Sign Up**: User creates account via frontend (`POST /api/auth/sign-up`)
2. **Sign In**: User authenticates and receives JWT token (`POST /api/auth/sign-in`)
3. **API Requests**: Include JWT token in Authorization header
4. **Token Verification**: Backend verifies token on every request

### JWT Token Format

```
Authorization: Bearer <jwt-token>
```

The JWT token contains:
- `sub`: User ID
- `exp`: Expiration timestamp
- Other claims as needed

## API Usage Examples

### Authentication Required

All task endpoints require authentication. Include the JWT token in the Authorization header:

```bash
# Get JWT token from Better Auth (via frontend)
TOKEN="your-jwt-token-here"

# Create a Task
curl -X POST "http://localhost:8001/api/v1/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread"}'

# List All Tasks (only returns current user's tasks)
curl -X GET "http://localhost:8001/api/v1/tasks" \
  -H "Authorization: Bearer $TOKEN"

# Get Specific Task
curl -X GET "http://localhost:8001/api/v1/tasks/1" \
  -H "Authorization: Bearer $TOKEN"

# Update Task (Partial)
curl -X PATCH "http://localhost:8001/api/v1/tasks/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# Delete Task
curl -X DELETE "http://localhost:8001/api/v1/tasks/1" \
  -H "Authorization: Bearer $TOKEN"
```

### Error Responses

**401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Missing authentication token"
}
```

**401 Unauthorized** - Expired token:
```json
{
  "detail": "Token expired"
}
```

**404 Not Found** - Task doesn't exist or belongs to another user:
```json
{
  "detail": "Task with ID 1 not found"
}
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

## Project Structure

```
backend/
├── src/
│   ├── models/          # SQLModel definitions
│   ├── api/             # FastAPI routes
│   ├── services/        # Business logic
│   ├── schemas/         # Pydantic schemas
│   ├── database/        # Connection and migrations
│   └── main.py          # App entry point
├── tests/               # Pytest test suite
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment variables
└── README.md            # This file
```

## Development

See the quickstart guide in `specs/001-task-crud-api/quickstart.md` for detailed development instructions.
