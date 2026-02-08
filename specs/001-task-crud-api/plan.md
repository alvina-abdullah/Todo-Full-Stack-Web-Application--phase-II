# Implementation Plan: Core Task Management & API

**Branch**: `001-task-crud-api` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-task-crud-api/spec.md`

## Summary

Implement a RESTful API for task management with full CRUD operations (Create, Read, Update, Delete) and user data isolation. The API will persist tasks to Neon Serverless PostgreSQL using SQLModel ORM and enforce that users can only access their own tasks. Authentication integration is deferred to a separate feature (Spec 2), with user ID passed as a parameter for testing.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI (latest stable), SQLModel (latest stable), Pydantic v2, asyncpg
**Storage**: Neon Serverless PostgreSQL (cloud-hosted PostgreSQL)
**Testing**: pytest, pytest-asyncio, httpx (for API testing)
**Target Platform**: Linux server (containerized deployment)
**Project Type**: Web application (backend API only)
**Performance Goals**: <500ms for CRUD operations, support 100 concurrent users
**Constraints**: <500ms p95 latency for API responses, user data isolation enforced at query level
**Scale/Scope**: Initial deployment for 100+ users, thousands of tasks per user

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Accuracy ✅
- **Requirement**: Enforce user ownership on all operations
- **Implementation**: All database queries will filter by user_id; ownership validation in service layer
- **Status**: PASS - Design includes user_id foreign key and query filtering

### II. Security ⚠️
- **Requirement**: JWT validation on all protected endpoints
- **Implementation**: Authentication deferred to Spec 2; user_id passed as parameter for testing
- **Status**: DEFERRED - Will be integrated when authentication feature is complete
- **Mitigation**: Document that endpoints are not production-ready without authentication

### III. Reproducibility ✅
- **Requirement**: Environment variables, migrations, locked dependencies
- **Implementation**:
  - Database URL in .env file
  - Alembic migrations for schema changes
  - requirements.txt with pinned versions
- **Status**: PASS - Standard practices will be followed

### IV. Clarity ✅
- **Requirement**: PEP 8, meaningful names, clear error messages
- **Implementation**:
  - Follow PEP 8 style guide
  - Use descriptive function/variable names
  - Return structured error responses with clear messages
  - Proper HTTP status codes per constitution
- **Status**: PASS - Design follows conventions

### V. Responsiveness ✅
- **Requirement**: <500ms for CRUD operations
- **Implementation**:
  - Async FastAPI endpoints
  - Database connection pooling
  - Efficient SQLModel queries with proper indexing
- **Status**: PASS - Architecture supports performance requirements

### API Standards ✅
- **Requirement**: RESTful conventions, proper HTTP status codes
- **Implementation**:
  - GET /tasks - List all user's tasks (200)
  - GET /tasks/{id} - Get specific task (200, 404, 403)
  - POST /tasks - Create task (201, 400)
  - PUT /tasks/{id} - Replace task (200, 404, 403, 400)
  - PATCH /tasks/{id} - Partial update (200, 404, 403, 400)
  - DELETE /tasks/{id} - Delete task (204, 404, 403)
- **Status**: PASS - Endpoints follow RESTful conventions

**Overall Gate Status**: ✅ PASS (with Security deferred to Spec 2 as documented)

## Project Structure

### Documentation (this feature)

```text
specs/001-task-crud-api/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── openapi.yaml    # API contract
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py          # Task SQLModel
│   │   └── base.py          # Base model with common fields
│   ├── api/
│   │   ├── __init__.py
│   │   ├── tasks.py         # Task CRUD endpoints
│   │   └── dependencies.py  # Dependency injection (DB session, user_id)
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py  # Business logic for task operations
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py    # Database connection and session management
│   │   └── migrations/      # Alembic migration scripts
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── task.py          # Pydantic schemas for request/response
│   └── main.py              # FastAPI application entry point
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_task_api.py     # API endpoint tests
│   ├── test_task_service.py # Service layer tests
│   └── test_models.py       # Model validation tests
├── alembic.ini              # Alembic configuration
├── requirements.txt         # Python dependencies
├── .env.example             # Example environment variables
└── README.md                # Setup and usage instructions
```

**Structure Decision**: Backend-only structure selected as this feature focuses solely on API implementation. Frontend will be added in a separate feature. The structure follows FastAPI best practices with clear separation of concerns: models (data), api (routes), services (business logic), schemas (validation).

## Complexity Tracking

No constitutional violations requiring justification.

## Phase 0: Research & Technology Decisions

### Research Tasks

1. **Neon PostgreSQL Connection Best Practices**
   - Research: Optimal connection pooling configuration for serverless PostgreSQL
   - Research: Handling connection limits and timeouts
   - Research: Environment variable configuration

2. **SQLModel with Async FastAPI**
   - Research: Async session management patterns
   - Research: Query optimization for user-filtered queries
   - Research: Migration strategy with Alembic

3. **Error Handling Patterns**
   - Research: FastAPI exception handlers
   - Research: Structured error response format
   - Research: HTTP status code mapping for different error types

4. **Testing Strategy**
   - Research: Test database setup (in-memory vs. test instance)
   - Research: Fixture patterns for API testing
   - Research: Mocking user authentication for tests

### Decisions to Document in research.md

- Database connection pooling configuration
- Async vs sync SQLModel usage
- Error response structure
- Test database approach
- User ID injection pattern (temporary until auth integration)

## Phase 1: Design Artifacts

### Data Model (data-model.md)

**Entities**:
- Task: Core entity with user ownership

**Relationships**:
- Task belongs to User (foreign key)

**Validation Rules**:
- Title: required, non-empty, max 200 characters
- Description: optional, max 2000 characters
- Completed: boolean, default false
- User ID: required, UUID or integer

### API Contracts (contracts/openapi.yaml)

**Endpoints**:
1. `GET /api/v1/tasks` - List user's tasks
2. `GET /api/v1/tasks/{task_id}` - Get specific task
3. `POST /api/v1/tasks` - Create new task
4. `PUT /api/v1/tasks/{task_id}` - Replace task
5. `PATCH /api/v1/tasks/{task_id}` - Partial update
6. `DELETE /api/v1/tasks/{task_id}` - Delete task

**Request/Response Schemas**:
- TaskCreate: {title, description?}
- TaskUpdate: {title?, description?, completed?}
- TaskResponse: {id, title, description, completed, user_id, created_at, updated_at}
- ErrorResponse: {detail, error_code?}

### Quickstart (quickstart.md)

**Setup Steps**:
1. Install Python 3.11+
2. Create virtual environment
3. Install dependencies from requirements.txt
4. Configure .env with DATABASE_URL
5. Run migrations: `alembic upgrade head`
6. Start server: `uvicorn src.main:app --reload`

**Testing**:
1. Run tests: `pytest`
2. Test coverage: `pytest --cov=src`

**API Usage Examples**:
- Create task: `POST /api/v1/tasks?user_id=1`
- List tasks: `GET /api/v1/tasks?user_id=1`

## Phase 2: Task Breakdown

*This section will be filled by the `/sp.tasks` command*

Tasks will be organized by user story priority:
- P1: Create and Store Tasks
- P1: View My Tasks
- P2: Update Task Details
- P2: Delete Tasks
- P3: Partial Task Updates

## Architectural Decisions

### ADR-001: User ID Injection Pattern

**Context**: Authentication is deferred to Spec 2, but we need to test user isolation now.

**Decision**: Pass user_id as a query parameter in all endpoints for testing. Add dependency injection point that will be replaced with JWT token extraction later.

**Consequences**:
- ✅ Allows testing of user isolation logic
- ✅ Clear integration point for authentication
- ⚠️ Endpoints not production-ready without authentication
- ⚠️ Must document security limitation

**Alternatives Considered**:
- Hardcode user_id: Rejected - prevents multi-user testing
- Skip user isolation: Rejected - violates constitution principle I (Accuracy)

### ADR-002: Async SQLModel with FastAPI

**Context**: FastAPI is async-first, but SQLModel can be used sync or async.

**Decision**: Use async SQLModel with asyncpg driver for PostgreSQL.

**Consequences**:
- ✅ Better performance under concurrent load
- ✅ Aligns with FastAPI async patterns
- ⚠️ Slightly more complex session management
- ⚠️ Requires async test fixtures

**Alternatives Considered**:
- Sync SQLModel: Rejected - limits scalability and doesn't leverage FastAPI's async capabilities

### ADR-003: Alembic for Migrations

**Context**: Need versioned, reproducible database schema changes per constitution principle III.

**Decision**: Use Alembic for database migrations.

**Consequences**:
- ✅ Version-controlled schema changes
- ✅ Reproducible across environments
- ✅ Standard tool in Python ecosystem
- ⚠️ Requires migration script creation for schema changes

**Alternatives Considered**:
- SQLModel create_all(): Rejected - not versioned, not reproducible
- Manual SQL scripts: Rejected - error-prone, no rollback support

## Risk Analysis

### Technical Risks

1. **Neon PostgreSQL Connection Limits**
   - Risk: Serverless PostgreSQL may have connection limits
   - Mitigation: Implement connection pooling with appropriate limits
   - Contingency: Use connection retry logic with exponential backoff

2. **User Isolation Bugs**
   - Risk: Query filtering errors could leak data between users
   - Mitigation: Comprehensive integration tests with multiple users
   - Contingency: Code review focused on query filtering logic

3. **Performance Under Load**
   - Risk: May not meet <500ms target under concurrent load
   - Mitigation: Database indexing on user_id and id columns
   - Contingency: Query optimization and caching if needed

### Integration Risks

1. **Authentication Integration (Spec 2)**
   - Risk: User ID injection pattern may not align with JWT structure
   - Mitigation: Design dependency injection to be easily replaceable
   - Contingency: Refactor dependency injection if needed

## Success Metrics

- All 15 functional requirements from spec implemented and tested
- 100% of user isolation tests pass (no cross-user data access)
- API response times <500ms for 95th percentile
- Test coverage >80% for service and API layers
- All edge cases from spec handled with appropriate errors
- Zero data loss or corruption in concurrent operation tests

## Next Steps

1. ✅ Complete Phase 0: Create research.md
2. ✅ Complete Phase 1: Create data-model.md, contracts/, quickstart.md
3. ⏭️ Run `/sp.tasks` to generate task breakdown
4. ⏭️ Run `/sp.implement` to execute tasks
5. ⏭️ Integration testing with multiple users
6. ⏭️ Performance testing under load
7. ⏭️ Documentation review and updates
