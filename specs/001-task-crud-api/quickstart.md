# Quickstart Guide: Core Task Management & API

**Feature**: 001-task-crud-api
**Date**: 2026-02-08
**Audience**: Developers setting up and testing the Task Management API

## Prerequisites

- Python 3.11 or higher
- PostgreSQL database (Neon Serverless PostgreSQL recommended)
- Git (for version control)
- Code editor (VS Code, PyCharm, etc.)

## Project Setup

### 1. Clone Repository and Navigate to Backend

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages** (requirements.txt):
```
fastapi==0.109.0
sqlmodel==0.0.14
uvicorn[standard]==0.27.0
pydantic==2.5.3
asyncpg==0.29.0
alembic==1.13.1
python-dotenv==1.0.0
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0
```

### 4. Configure Environment Variables

Create a `.env` file in the backend directory:

```bash
# .env
DATABASE_URL=postgresql+asyncpg://user:password@host/database?sslmode=require
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**For Neon PostgreSQL**:
1. Sign up at https://neon.tech
2. Create a new project
3. Copy the connection string
4. Replace the DATABASE_URL value above

**Example Neon connection string**:
```
postgresql+asyncpg://username:password@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

### 5. Initialize Database

```bash
# Initialize Alembic (first time only)
alembic init src/database/migrations

# Create initial migration
alembic revision --autogenerate -m "Create tasks table"

# Apply migrations
alembic upgrade head
```

### 6. Start Development Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000

**Auto-generated documentation**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Usage Examples

### Using cURL

#### Create a Task

```bash
curl -X POST "http://localhost:8000/api/v1/tasks?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  }'
```

**Response** (201 Created):
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "user_id": 1,
  "created_at": "2026-02-08T10:00:00Z",
  "updated_at": "2026-02-08T10:00:00Z"
}
```

#### List All Tasks

```bash
curl -X GET "http://localhost:8000/api/v1/tasks?user_id=1"
```

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "user_id": 1,
    "created_at": "2026-02-08T10:00:00Z",
    "updated_at": "2026-02-08T10:00:00Z"
  }
]
```

#### Get Specific Task

```bash
curl -X GET "http://localhost:8000/api/v1/tasks/1?user_id=1"
```

#### Update Task (Partial)

```bash
curl -X PATCH "http://localhost:8000/api/v1/tasks/1?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true
  }'
```

#### Update Task (Full Replace)

```bash
curl -X PUT "http://localhost:8000/api/v1/tasks/1?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries and cook dinner",
    "description": "Milk, eggs, bread, chicken",
    "completed": false
  }'
```

#### Delete Task

```bash
curl -X DELETE "http://localhost:8000/api/v1/tasks/1?user_id=1"
```

**Response** (204 No Content)

### Using Python (httpx)

```python
import httpx
import asyncio

async def test_api():
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Create task
        response = await client.post(
            "/api/v1/tasks",
            params={"user_id": 1},
            json={"title": "Buy groceries", "description": "Milk, eggs, bread"}
        )
        task = response.json()
        print(f"Created task: {task}")

        # List tasks
        response = await client.get("/api/v1/tasks", params={"user_id": 1})
        tasks = response.json()
        print(f"All tasks: {tasks}")

        # Update task
        response = await client.patch(
            f"/api/v1/tasks/{task['id']}",
            params={"user_id": 1},
            json={"completed": True}
        )
        updated_task = response.json()
        print(f"Updated task: {updated_task}")

asyncio.run(test_api())
```

### Using Swagger UI

1. Navigate to http://localhost:8000/docs
2. Click on any endpoint to expand it
3. Click "Try it out"
4. Fill in parameters and request body
5. Click "Execute"
6. View response below

## Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html
```

View coverage report: `htmlcov/index.html`

### Run Specific Test File

```bash
pytest tests/test_task_api.py
```

### Run Tests with Output

```bash
pytest -v -s
```

## Testing User Isolation

To verify that user isolation is working correctly:

```bash
# Create task for user 1
curl -X POST "http://localhost:8000/api/v1/tasks?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{"title": "User 1 Task"}'

# Create task for user 2
curl -X POST "http://localhost:8000/api/v1/tasks?user_id=2" \
  -H "Content-Type: application/json" \
  -d '{"title": "User 2 Task"}'

# List tasks for user 1 (should only see User 1 Task)
curl -X GET "http://localhost:8000/api/v1/tasks?user_id=1"

# List tasks for user 2 (should only see User 2 Task)
curl -X GET "http://localhost:8000/api/v1/tasks?user_id=2"

# Try to access user 2's task as user 1 (should fail with 403 or 404)
curl -X GET "http://localhost:8000/api/v1/tasks/2?user_id=1"
```

## Common Issues and Solutions

### Issue: Database Connection Error

**Error**: `asyncpg.exceptions.InvalidPasswordError`

**Solution**:
- Verify DATABASE_URL in .env file
- Check username and password are correct
- Ensure database exists
- For Neon: Verify connection string includes `?sslmode=require`

### Issue: Migration Fails

**Error**: `alembic.util.exc.CommandError: Target database is not up to date`

**Solution**:
```bash
# Check current migration status
alembic current

# View migration history
alembic history

# Upgrade to latest
alembic upgrade head
```

### Issue: Port Already in Use

**Error**: `OSError: [Errno 48] Address already in use`

**Solution**:
```bash
# Find process using port 8000
# On macOS/Linux:
lsof -i :8000

# On Windows:
netstat -ano | findstr :8000

# Kill the process or use a different port
uvicorn src.main:app --reload --port 8001
```

### Issue: Import Errors

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

## Development Workflow

### 1. Make Code Changes

Edit files in `backend/src/`

### 2. Run Tests

```bash
pytest
```

### 3. Check Code Style

```bash
# Install development tools
pip install black flake8 mypy

# Format code
black src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/
```

### 4. Create Migration (if models changed)

```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

### 5. Test Manually

Use Swagger UI or cURL to test endpoints

### 6. Commit Changes

```bash
git add .
git commit -m "Description of changes"
```

## Project Structure Reference

```
backend/
├── src/
│   ├── main.py              # FastAPI app entry point
│   ├── models/
│   │   ├── task.py          # Task SQLModel
│   │   └── base.py          # Base model
│   ├── api/
│   │   ├── tasks.py         # Task endpoints
│   │   └── dependencies.py  # Dependency injection
│   ├── services/
│   │   └── task_service.py  # Business logic
│   ├── schemas/
│   │   └── task.py          # Pydantic schemas
│   └── database/
│       ├── connection.py    # DB connection
│       └── migrations/      # Alembic migrations
├── tests/
│   ├── conftest.py          # Test fixtures
│   ├── test_task_api.py     # API tests
│   └── test_task_service.py # Service tests
├── .env                     # Environment variables (not in git)
├── .env.example             # Example env file
├── requirements.txt         # Python dependencies
├── alembic.ini             # Alembic config
└── README.md               # Project documentation
```

## Next Steps

1. **Implement Authentication** (Spec 2): Replace user_id query parameter with JWT token extraction
2. **Add Frontend** (Spec 3): Build Next.js UI to consume this API
3. **Add Features**: Implement task filtering, sorting, pagination
4. **Deploy**: Deploy to production environment

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Neon PostgreSQL Documentation](https://neon.tech/docs)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Pytest Documentation](https://docs.pytest.org/)

## Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review error messages in server logs
3. Consult the data-model.md and plan.md in specs/001-task-crud-api/
4. Check constitution.md for project standards
