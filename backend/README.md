# Task Management API - Backend

RESTful API for managing tasks with user ownership and data isolation.

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

Edit `.env` with your database credentials:

```
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database?sslmode=require
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 4. Initialize Database

```bash
# Initialize Alembic (first time only)
alembic init src/database/migrations

# Create initial migration
alembic revision --autogenerate -m "Create tasks table"

# Apply migrations
alembic upgrade head
```

### 5. Start Development Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000

**Auto-generated documentation**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Usage Examples

### Create a Task

```bash
curl -X POST "http://localhost:8000/api/v1/tasks?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread"}'
```

### List All Tasks

```bash
curl -X GET "http://localhost:8000/api/v1/tasks?user_id=1"
```

### Get Specific Task

```bash
curl -X GET "http://localhost:8000/api/v1/tasks/1?user_id=1"
```

### Update Task (Partial)

```bash
curl -X PATCH "http://localhost:8000/api/v1/tasks/1?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

### Delete Task

```bash
curl -X DELETE "http://localhost:8000/api/v1/tasks/1?user_id=1"
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
