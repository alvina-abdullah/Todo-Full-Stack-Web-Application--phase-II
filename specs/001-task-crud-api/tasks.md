# Tasks: Core Task Management & API

**Feature**: 001-task-crud-api
**Input**: Design documents from `/specs/001-task-crud-api/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/openapi.yaml

**Tests**: Tests are not explicitly requested in the specification, so test tasks are not included. Integration testing will be performed manually using the quickstart guide examples.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend API**: `backend/src/`, `backend/tests/`
- Paths shown below follow the structure defined in plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend directory structure per plan.md (backend/src/{models,api,services,schemas,database}, backend/tests/)
- [x] T002 Create requirements.txt with pinned dependencies (fastapi==0.109.0, sqlmodel==0.0.14, uvicorn[standard]==0.27.0, pydantic==2.5.3, asyncpg==0.29.0, alembic==1.13.1, python-dotenv==1.0.0, pytest==7.4.4, pytest-asyncio==0.23.3, httpx==0.26.0)
- [x] T003 Create .env.example file with DATABASE_URL, ENVIRONMENT, LOG_LEVEL variables in backend/
- [x] T004 Create .gitignore file to exclude venv/, .env, __pycache__/, *.pyc, .pytest_cache/ in backend/
- [x] T005 Initialize Alembic configuration in backend/ (alembic init src/database/migrations)
- [x] T006 Create README.md in backend/ with setup instructions from quickstart.md

**Acceptance**: Project structure matches plan.md, dependencies documented, environment template created

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure needed by all user stories

- [x] T007 [P] Create base SQLModel class in backend/src/models/base.py with common fields (id, created_at, updated_at)
- [x] T008 [P] Create database connection module in backend/src/database/connection.py with async engine, session factory, and connection pooling configuration
- [x] T009 [P] Create custom exception classes in backend/src/api/exceptions.py (TaskNotFoundError, TaskAccessDeniedError, ValidationError)
- [x] T010 [P] Create global exception handlers in backend/src/api/exception_handlers.py mapping exceptions to HTTP responses
- [x] T011 [P] Create dependency injection functions in backend/src/api/dependencies.py (get_session for AsyncSession, get_current_user_id for user_id query parameter)
- [x] T012 Create FastAPI application in backend/src/main.py with CORS, exception handlers, lifespan events, and API router registration
- [x] T013 Create initial Alembic migration for tasks table in backend/src/database/migrations/ with indexes on user_id and (user_id, created_at)

**Acceptance**: Database connection works, exception handling configured, FastAPI app starts successfully

**Dependencies**: None - foundational tasks can run in parallel

---

## Phase 3: User Story 1 - Create and Store Tasks (Priority: P1)

**Story Goal**: Users can create new tasks with title and description that persist to database

**Independent Test**: Create task via POST /api/v1/tasks?user_id=1, verify 201 response with task ID, then GET /api/v1/tasks?user_id=1 to confirm task persists

### Implementation Tasks

- [x] T014 [P] [US1] Create Task SQLModel in backend/src/models/task.py with fields (id, title, description, completed, user_id, created_at, updated_at) and validation constraints
- [x] T015 [P] [US1] Create TaskCreate Pydantic schema in backend/src/schemas/task.py with title (required, 1-200 chars) and description (optional, max 2000 chars)
- [x] T016 [P] [US1] Create TaskResponse Pydantic schema in backend/src/schemas/task.py with all task fields including timestamps
- [x] T017 [US1] Create TaskService class in backend/src/services/task_service.py with create_task method (async, accepts session, user_id, TaskCreate, returns Task)
- [x] T018 [US1] Implement create_task method with validation (trim whitespace, check title non-empty), database insert, and return created task
- [x] T019 [US1] Create POST /api/v1/tasks endpoint in backend/src/api/tasks.py using Depends(get_session) and Depends(get_current_user_id), call task_service.create_task, return 201 with TaskResponse
- [x] T020 [US1] Add error handling to POST endpoint for validation errors (400) and database errors (500)
- [x] T021 [US1] Apply Alembic migration to create tasks table in database (alembic upgrade head)

**Acceptance Criteria**:
- ✅ POST /api/v1/tasks?user_id=1 with {"title": "Buy groceries", "description": "Milk, eggs"} returns 201 with task object
- ✅ Created task has unique ID, user_id=1, completed=false, and timestamps
- ✅ Empty title returns 400 error
- ✅ Task persists in database (verified by querying database directly)

**Dependencies**: Requires Phase 2 (foundational infrastructure)

---

## Phase 4: User Story 2 - View My Tasks (Priority: P1)

**Story Goal**: Users can view all their tasks and retrieve specific tasks, with data isolation enforced

**Independent Test**: Create tasks for user 1 and user 2, verify GET /api/v1/tasks?user_id=1 only returns user 1's tasks, verify GET /api/v1/tasks/X?user_id=2 returns 403/404 for user 1's task

### Implementation Tasks

- [x] T022 [P] [US2] Implement list_tasks method in backend/src/services/task_service.py (async, accepts session, user_id, returns List[Task] filtered by user_id, ordered by created_at DESC)
- [x] T023 [P] [US2] Implement get_task method in backend/src/services/task_service.py (async, accepts session, task_id, user_id, returns Task or raises TaskNotFoundError/TaskAccessDeniedError)
- [x] T024 [US2] Create GET /api/v1/tasks endpoint in backend/src/api/tasks.py to list all user's tasks, return 200 with List[TaskResponse]
- [x] T025 [US2] Create GET /api/v1/tasks/{task_id} endpoint in backend/src/api/tasks.py to get specific task, return 200 with TaskResponse, 404 if not found, 403 if access denied
- [x] T026 [US2] Add user isolation validation in get_task method (check task.user_id == requesting_user_id, raise TaskAccessDeniedError if mismatch)

**Acceptance Criteria**:
- ✅ GET /api/v1/tasks?user_id=1 returns only tasks where user_id=1
- ✅ GET /api/v1/tasks?user_id=2 returns only tasks where user_id=2 (different from user 1's tasks)
- ✅ GET /api/v1/tasks/{id}?user_id=1 returns task details if task belongs to user 1
- ✅ GET /api/v1/tasks/{id}?user_id=1 returns 403/404 if task belongs to user 2
- ✅ Empty task list returns 200 with empty array []

**Dependencies**: Requires Phase 3 (US1) - need tasks to exist before viewing them

---

## Phase 5: User Story 3 - Update Task Details (Priority: P2)

**Story Goal**: Users can modify task title, description, and completion status with full or partial updates

**Independent Test**: Create task, use PUT to replace all fields, verify changes persist; create another task, use PATCH to update only completed status, verify other fields unchanged

### Implementation Tasks

- [x] T027 [P] [US3] Create TaskReplace Pydantic schema in backend/src/schemas/task.py with title (required), description (optional), completed (required)
- [x] T028 [P] [US3] Create TaskUpdate Pydantic schema in backend/src/schemas/task.py with all fields optional (title, description, completed)
- [x] T029 [P] [US3] Implement replace_task method in backend/src/services/task_service.py (async, accepts session, task_id, user_id, TaskReplace, returns updated Task)
- [x] T030 [P] [US3] Implement update_task method in backend/src/services/task_service.py (async, accepts session, task_id, user_id, TaskUpdate, returns updated Task, only updates provided fields)
- [x] T031 [US3] Add ownership validation to replace_task and update_task methods (verify task.user_id == user_id before updating)
- [x] T032 [US3] Create PUT /api/v1/tasks/{task_id} endpoint in backend/src/api/tasks.py for full replacement, return 200 with TaskResponse, 404 if not found, 403 if access denied
- [x] T033 [US3] Create PATCH /api/v1/tasks/{task_id} endpoint in backend/src/api/tasks.py for partial update, return 200 with TaskResponse, 404 if not found, 403 if access denied
- [x] T034 [US3] Update updated_at timestamp automatically on task modifications in both replace and update methods

**Acceptance Criteria**:
- ✅ PUT /api/v1/tasks/{id}?user_id=1 with full task data replaces all fields
- ✅ PATCH /api/v1/tasks/{id}?user_id=1 with {"completed": true} updates only completed field
- ✅ PATCH /api/v1/tasks/{id}?user_id=1 with {"title": "New title"} updates only title
- ✅ PUT/PATCH on another user's task returns 403/404
- ✅ updated_at timestamp changes after update
- ✅ Invalid data (empty title, too long description) returns 400

**Dependencies**: Requires Phase 4 (US2) - need to retrieve tasks to verify updates

---

## Phase 6: User Story 4 - Delete Tasks (Priority: P2)

**Story Goal**: Users can permanently delete tasks they own

**Independent Test**: Create task, delete it via DELETE endpoint, verify 204 response, then GET same task returns 404

### Implementation Tasks

- [x] T035 [P] [US4] Implement delete_task method in backend/src/services/task_service.py (async, accepts session, task_id, user_id, returns None or raises exceptions)
- [x] T036 [US4] Add ownership validation to delete_task method (verify task.user_id == user_id before deleting, raise TaskAccessDeniedError if mismatch)
- [x] T037 [US4] Create DELETE /api/v1/tasks/{task_id} endpoint in backend/src/api/tasks.py, return 204 No Content on success, 404 if not found, 403 if access denied
- [x] T038 [US4] Handle edge case of deleting already deleted task (return 404)

**Acceptance Criteria**:
- ✅ DELETE /api/v1/tasks/{id}?user_id=1 returns 204 and removes task from database
- ✅ GET /api/v1/tasks/{id}?user_id=1 after deletion returns 404
- ✅ DELETE on another user's task returns 403/404
- ✅ DELETE on non-existent task returns 404
- ✅ Deleted task no longer appears in GET /api/v1/tasks list

**Dependencies**: Requires Phase 4 (US2) - need to verify task is deleted

---

## Phase 7: User Story 5 - Partial Task Updates (Priority: P3)

**Story Goal**: Already implemented in Phase 5 (US3) via PATCH endpoint

**Note**: The PATCH /api/v1/tasks/{task_id} endpoint implemented in T033 provides partial update functionality. No additional tasks needed.

**Acceptance Criteria**:
- ✅ PATCH endpoint allows updating individual fields without providing all fields (verified in Phase 5)

**Dependencies**: Completed in Phase 5 (US3)

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final refinements and production readiness

- [x] T039 [P] Add API documentation strings to all endpoints in backend/src/api/tasks.py for auto-generated OpenAPI docs
- [x] T040 [P] Add logging to service layer methods in backend/src/services/task_service.py (log operations, errors, user_id for audit)
- [x] T041 [P] Create comprehensive .env.example with comments explaining each variable in backend/
- [x] T042 [P] Update README.md in backend/ with complete setup instructions, API usage examples, and troubleshooting guide
- [ ] T043 Verify all endpoints return correct HTTP status codes per constitution (200, 201, 204, 400, 403, 404, 500)
- [ ] T044 Run manual integration tests following quickstart.md examples to verify all user stories work end-to-end
- [ ] T045 Verify user isolation by creating tasks for multiple users and confirming data separation
- [ ] T046 Test edge cases: empty title, oversized fields, concurrent updates, database connection failures
- [ ] T047 Performance test: Verify API response times <500ms for CRUD operations under normal load

**Acceptance**: All endpoints documented, logging in place, manual tests pass, performance targets met

**Dependencies**: Requires all user story phases (3-6) complete

---

## Dependencies & Execution Order

### Story Completion Order

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational)
    ↓
Phase 3 (US1: Create Tasks) ← MVP Scope
    ↓
Phase 4 (US2: View Tasks) ← MVP Scope
    ↓
Phase 5 (US3: Update Tasks)
    ↓
Phase 6 (US4: Delete Tasks)
    ↓
Phase 7 (US5: Partial Updates) [Already complete in Phase 5]
    ↓
Phase 8 (Polish)
```

### Parallel Execution Opportunities

**Phase 2 (Foundational)**: Tasks T007-T011 can run in parallel (different files, no dependencies)

**Phase 3 (US1)**: Tasks T014-T016 can run in parallel (models and schemas are independent)

**Phase 4 (US2)**: Tasks T022-T023 can run in parallel (different service methods)

**Phase 5 (US3)**: Tasks T027-T030 can run in parallel (schemas and service methods are independent)

**Phase 6 (US4)**: Task T035 can run in parallel with other phases if needed

**Phase 8 (Polish)**: Tasks T039-T042 can run in parallel (documentation tasks)

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**Recommended MVP**: Phase 1 + Phase 2 + Phase 3 (US1) + Phase 4 (US2)

This delivers:
- ✅ Users can create tasks
- ✅ Users can view their tasks
- ✅ Data isolation enforced
- ✅ Persistent storage working

**Rationale**: US1 and US2 together provide the core value proposition - users can capture and review tasks. This is independently testable and deployable.

### Incremental Delivery

1. **Sprint 1**: Phases 1-4 (Setup + Foundational + US1 + US2) → MVP Release
2. **Sprint 2**: Phase 5 (US3: Update) → Add task editing capability
3. **Sprint 3**: Phase 6 (US4: Delete) → Add task deletion capability
4. **Sprint 4**: Phase 8 (Polish) → Production hardening

### Independent Testing Per Story

Each user story phase includes acceptance criteria that can be tested independently:

- **US1**: Test task creation and persistence
- **US2**: Test task retrieval and user isolation
- **US3**: Test task updates (full and partial)
- **US4**: Test task deletion
- **US5**: Already covered by US3

---

## Task Summary

**Total Tasks**: 47 tasks
- Phase 1 (Setup): 6 tasks
- Phase 2 (Foundational): 7 tasks
- Phase 3 (US1): 8 tasks
- Phase 4 (US2): 5 tasks
- Phase 5 (US3): 8 tasks
- Phase 6 (US4): 4 tasks
- Phase 7 (US5): 0 tasks (covered in US3)
- Phase 8 (Polish): 9 tasks

**Parallelizable Tasks**: 15 tasks marked with [P]

**User Story Distribution**:
- US1 (Create): 8 tasks
- US2 (View): 5 tasks
- US3 (Update): 8 tasks
- US4 (Delete): 4 tasks
- US5 (Partial Update): 0 tasks (already in US3)

**Estimated MVP**: 26 tasks (Phases 1-4)

---

## Validation Checklist

- [x] All tasks follow checklist format: `- [ ] [TaskID] [P?] [Story?] Description with file path`
- [x] Tasks organized by user story for independent implementation
- [x] Each user story has clear acceptance criteria
- [x] Dependencies documented showing story completion order
- [x] Parallel execution opportunities identified
- [x] MVP scope defined (US1 + US2)
- [x] File paths match structure in plan.md
- [x] No test tasks generated (not requested in spec)
- [x] All 5 user stories from spec.md covered
- [x] Tasks map to entities from data-model.md
- [x] Tasks map to endpoints from contracts/openapi.yaml
