# Research: Core Task Management & API

**Feature**: 001-task-crud-api
**Date**: 2026-02-08
**Phase**: Phase 0 - Research & Technology Decisions

## Overview

This document captures research findings and technology decisions for implementing the Core Task Management & API feature. All decisions align with the project constitution and support the functional requirements defined in spec.md.

## 1. Neon PostgreSQL Connection Best Practices

### Research Question
How to optimally configure database connections for Neon Serverless PostgreSQL with FastAPI?

### Findings

**Connection Pooling**:
- Neon PostgreSQL is serverless and auto-scales, but has connection limits per project
- Recommended: Use SQLAlchemy's async connection pool with conservative limits
- Configuration: `pool_size=5, max_overflow=10` for development, adjust based on load testing
- Neon supports connection pooling natively via connection string parameters

**Connection String Format**:
```
postgresql+asyncpg://user:password@host/database?sslmode=require
```

**Best Practices**:
- Always use SSL (`sslmode=require`) for security
- Set reasonable connection timeouts (30 seconds)
- Implement connection retry logic with exponential backoff
- Use environment variables for connection credentials
- Close connections properly in FastAPI lifespan events

### Decision

**Chosen Approach**: Use SQLAlchemy async engine with asyncpg driver and connection pooling.

**Configuration**:
```python
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL logging in development
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,   # Recycle connections after 1 hour
)
```

**Rationale**:
- Aligns with FastAPI async patterns
- Provides connection reuse for performance
- Pool pre-ping prevents stale connection errors
- Conservative pool size prevents hitting Neon limits

**Alternatives Considered**:
- Sync SQLAlchemy: Rejected - doesn't leverage FastAPI async capabilities
- No pooling: Rejected - poor performance, connection overhead
- Larger pool size: Rejected - may hit Neon connection limits under load

## 2. SQLModel with Async FastAPI

### Research Question
What's the best pattern for using SQLModel with async FastAPI endpoints?

### Findings

**Async Session Management**:
- SQLModel supports async operations via SQLAlchemy 2.0
- Use `AsyncSession` for database operations
- Dependency injection pattern for session management
- Context manager ensures proper session cleanup

**Query Patterns**:
```python
# Async query example
async with AsyncSession(engine) as session:
    statement = select(Task).where(Task.user_id == user_id)
    result = await session.execute(statement)
    tasks = result.scalars().all()
```

**User Isolation Pattern**:
- Always filter queries by user_id
- Use service layer to encapsulate filtering logic
- Validate ownership before updates/deletes

### Decision

**Chosen Approach**: Async SQLModel with dependency injection for session management.

**Implementation Pattern**:
```python
# Dependency for database session
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        yield session

# Dependency for user ID (temporary until auth integration)
async def get_current_user_id(user_id: int = Query(...)) -> int:
    return user_id

# Endpoint example
@router.get("/tasks")
async def list_tasks(
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id)
):
    return await task_service.list_tasks(session, user_id)
```

**Rationale**:
- Clean separation of concerns
- Easy to replace user_id dependency with JWT extraction later
- Proper session lifecycle management
- Testable with dependency overrides

**Alternatives Considered**:
- Sync SQLModel: Rejected - limits scalability
- Global session: Rejected - not thread-safe, poor for async
- Manual session management: Rejected - error-prone, boilerplate

## 3. Database Migrations with Alembic

### Research Question
How to implement versioned, reproducible database migrations?

### Findings

**Alembic Integration**:
- Standard migration tool for SQLAlchemy/SQLModel
- Supports auto-generation of migrations from model changes
- Version control friendly (migration files are Python scripts)
- Supports upgrade and downgrade operations

**Migration Workflow**:
1. Define/modify SQLModel models
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Review generated migration script
4. Apply migration: `alembic upgrade head`
5. Rollback if needed: `alembic downgrade -1`

**Best Practices**:
- Always review auto-generated migrations
- Test migrations on development database first
- Include both upgrade and downgrade operations
- Use descriptive migration messages
- Commit migration files to version control

### Decision

**Chosen Approach**: Alembic for all database schema changes.

**Configuration**:
- Alembic config file: `alembic.ini`
- Migrations directory: `backend/src/database/migrations/`
- Auto-generate migrations from SQLModel changes
- Require manual review before applying

**Rationale**:
- Meets constitution requirement for reproducibility
- Version-controlled schema changes
- Standard tool in Python ecosystem
- Supports rollback for safety

**Alternatives Considered**:
- SQLModel.metadata.create_all(): Rejected - not versioned, not reproducible
- Manual SQL scripts: Rejected - error-prone, no automatic rollback
- Django migrations: Rejected - not applicable for FastAPI

## 4. Error Handling and Response Structure

### Research Question
What's the best pattern for consistent error handling and responses?

### Findings

**FastAPI Exception Handlers**:
- Custom exception classes for domain errors
- Global exception handlers for consistent responses
- HTTP status code mapping
- Structured error response format

**Error Response Structure**:
```json
{
  "detail": "Human-readable error message",
  "error_code": "TASK_NOT_FOUND",
  "field_errors": {  // Optional, for validation errors
    "title": ["Title cannot be empty"]
  }
}
```

**HTTP Status Code Mapping**:
- 400 Bad Request: Validation errors, invalid input
- 401 Unauthorized: Missing/invalid authentication (future)
- 403 Forbidden: User doesn't own resource
- 404 Not Found: Resource doesn't exist
- 500 Internal Server Error: Unexpected errors

### Decision

**Chosen Approach**: Custom exception classes with global exception handlers.

**Implementation**:
```python
# Custom exceptions
class TaskNotFoundError(Exception):
    pass

class TaskAccessDeniedError(Exception):
    pass

# Exception handlers
@app.exception_handler(TaskNotFoundError)
async def task_not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc), "error_code": "TASK_NOT_FOUND"}
    )
```

**Rationale**:
- Consistent error responses across all endpoints
- Clear separation between error types
- Easy to add new error types
- Aligns with constitution requirement for clear error messages

**Alternatives Considered**:
- HTTPException only: Rejected - less type-safe, harder to test
- No structured errors: Rejected - violates constitution clarity principle
- Error codes only: Rejected - not user-friendly

## 5. Testing Strategy

### Research Question
How to effectively test the API with user isolation and database operations?

### Findings

**Test Database Approaches**:
1. In-memory SQLite: Fast but doesn't match PostgreSQL behavior
2. Test PostgreSQL instance: Accurate but slower, requires setup
3. Docker PostgreSQL: Good balance, reproducible

**Testing Patterns**:
- Use pytest fixtures for database setup/teardown
- Create test database per test session
- Use transactions that rollback after each test
- Mock external dependencies (auth will be mocked initially)

**Test Organization**:
- Unit tests: Service layer logic, model validation
- Integration tests: API endpoints with database
- Contract tests: API response schemas match OpenAPI spec

### Decision

**Chosen Approach**: Docker PostgreSQL for integration tests, pytest fixtures for setup.

**Test Configuration**:
```python
# conftest.py
@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture
async def session(test_engine):
    async with AsyncSession(test_engine) as session:
        yield session
        await session.rollback()  # Rollback after each test
```

**Test Coverage Goals**:
- >80% coverage for service and API layers
- 100% coverage for user isolation logic
- All edge cases from spec tested

**Rationale**:
- Docker PostgreSQL matches production environment
- Transaction rollback keeps tests isolated
- Fixtures reduce boilerplate
- Comprehensive coverage ensures quality

**Alternatives Considered**:
- SQLite: Rejected - behavior differences from PostgreSQL
- Shared test database: Rejected - tests not isolated
- No integration tests: Rejected - insufficient coverage

## 6. User ID Injection Pattern (Temporary)

### Research Question
How to test user isolation before authentication is implemented?

### Findings

**Temporary Approach**:
- Pass user_id as query parameter
- Use FastAPI dependency injection
- Design for easy replacement with JWT extraction

**Integration Point**:
```python
# Current (temporary)
async def get_current_user_id(user_id: int = Query(...)) -> int:
    return user_id

# Future (with JWT)
async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    payload = jwt.decode(token, SECRET_KEY)
    return payload["user_id"]
```

### Decision

**Chosen Approach**: Query parameter with dependency injection, designed for easy replacement.

**Implementation**:
- All endpoints use `Depends(get_current_user_id)`
- Service layer receives user_id as parameter
- Clear documentation that this is temporary
- Integration tests use multiple user IDs to verify isolation

**Rationale**:
- Allows testing user isolation immediately
- Clear integration point for authentication
- Minimal refactoring needed when auth is added
- Aligns with constitution accuracy principle

**Alternatives Considered**:
- Hardcode user_id: Rejected - can't test multi-user scenarios
- Skip user isolation: Rejected - violates constitution
- Wait for auth: Rejected - delays critical feature testing

## 7. API Versioning

### Research Question
Should we version the API from the start?

### Findings

**Versioning Strategies**:
- URL path versioning: `/api/v1/tasks`
- Header versioning: `Accept: application/vnd.api.v1+json`
- No versioning initially: Add when breaking changes needed

**Best Practices**:
- Start with v1 in URL path
- Allows future breaking changes without affecting existing clients
- Clear and explicit

### Decision

**Chosen Approach**: URL path versioning with `/api/v1/` prefix.

**Rationale**:
- Explicit and discoverable
- Standard practice in REST APIs
- Allows future v2 without breaking v1
- Minimal overhead

**Alternatives Considered**:
- No versioning: Rejected - harder to add later
- Header versioning: Rejected - less discoverable
- Query parameter versioning: Rejected - non-standard

## Summary of Key Decisions

| Decision Area | Chosen Approach | Key Rationale |
|---------------|----------------|---------------|
| Database Connection | Async SQLAlchemy with connection pooling | Performance, aligns with FastAPI async |
| Session Management | Dependency injection with AsyncSession | Clean, testable, proper lifecycle |
| Migrations | Alembic with auto-generation | Versioned, reproducible, standard tool |
| Error Handling | Custom exceptions with global handlers | Consistent, clear, type-safe |
| Testing | Docker PostgreSQL with pytest fixtures | Accurate, isolated, comprehensive |
| User ID (temp) | Query parameter with dependency injection | Testable now, easy to replace later |
| API Versioning | URL path `/api/v1/` | Explicit, standard, future-proof |

## Open Questions

None - all research questions resolved.

## Next Steps

Proceed to Phase 1: Create data-model.md, contracts/, and quickstart.md based on these research findings.
