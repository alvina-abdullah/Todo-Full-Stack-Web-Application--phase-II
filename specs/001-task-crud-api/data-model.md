# Data Model: Core Task Management & API

**Feature**: 001-task-crud-api
**Date**: 2026-02-08
**Phase**: Phase 1 - Design

## Overview

This document defines the data entities, relationships, and validation rules for the Core Task Management & API feature. The data model enforces user ownership and supports all CRUD operations defined in the specification.

## Entities

### Task

**Purpose**: Represents a single todo item owned by a user.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique identifier for the task |
| title | String | Required, Max 200 chars, Non-empty | Task title/summary |
| description | String | Optional, Max 2000 chars | Detailed task description |
| completed | Boolean | Required, Default: false | Completion status |
| user_id | Integer | Required, Foreign Key → User.id | Owner of the task |
| created_at | DateTime | Required, Auto-set on creation | Timestamp when task was created |
| updated_at | DateTime | Required, Auto-update on modification | Timestamp of last modification |

**Indexes**:
- Primary index on `id`
- Index on `user_id` (for efficient user-filtered queries)
- Composite index on `(user_id, created_at)` (for sorted user task lists)

**Relationships**:
- **Belongs to User**: `Task.user_id` references `User.id`
  - Cascade behavior: When user is deleted, all their tasks are deleted (CASCADE)
  - Constraint: user_id must reference an existing user (FOREIGN KEY)

### User (Reference Only)

**Purpose**: Represents a user account. Full user management is handled in a separate feature (Spec 2).

**Fields** (minimal for this feature):

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique identifier for the user |

**Note**: For this feature, we only need to reference user_id. The full User model with email, password, etc. will be defined in the authentication feature (Spec 2).

## Validation Rules

### Task Creation

- **title**:
  - MUST NOT be empty or whitespace-only
  - MUST NOT exceed 200 characters
  - Trim leading/trailing whitespace before validation

- **description**:
  - MAY be null or empty
  - MUST NOT exceed 2000 characters if provided

- **completed**:
  - Defaults to `false` if not provided
  - MUST be boolean value

- **user_id**:
  - MUST be provided
  - MUST reference an existing user (enforced by foreign key)

### Task Update

- **title** (if provided):
  - Same rules as creation
  - If not provided in PATCH, existing value retained

- **description** (if provided):
  - Same rules as creation
  - Can be set to null/empty to clear description
  - If not provided in PATCH, existing value retained

- **completed** (if provided):
  - MUST be boolean value
  - If not provided in PATCH, existing value retained

### Task Retrieval

- **Ownership Check**:
  - User can ONLY retrieve tasks where `task.user_id == requesting_user_id`
  - Attempting to access another user's task returns 403 Forbidden or 404 Not Found

### Task Deletion

- **Ownership Check**:
  - User can ONLY delete tasks where `task.user_id == requesting_user_id`
  - Attempting to delete another user's task returns 403 Forbidden or 404 Not Found

## State Transitions

### Task Completion Status

```
[Incomplete] ←→ [Complete]
```

**Transitions**:
- `Incomplete → Complete`: User marks task as done
- `Complete → Incomplete`: User reopens task

**Rules**:
- No restrictions on transitions
- Can toggle between states freely
- Transition is immediate (no intermediate states)

## Database Schema (SQLModel)

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    """Task model representing a todo item."""

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200, min_length=1)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False)
    user_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Indexes defined in Alembic migration
    # - Index on user_id
    # - Composite index on (user_id, created_at)
```

## Query Patterns

### List User's Tasks

```sql
SELECT * FROM tasks
WHERE user_id = :user_id
ORDER BY created_at DESC;
```

**Performance**: O(log n) with index on user_id

### Get Specific Task with Ownership Check

```sql
SELECT * FROM tasks
WHERE id = :task_id AND user_id = :user_id;
```

**Performance**: O(1) with primary key and user_id index

### Create Task

```sql
INSERT INTO tasks (title, description, completed, user_id, created_at, updated_at)
VALUES (:title, :description, :completed, :user_id, NOW(), NOW())
RETURNING *;
```

### Update Task with Ownership Check

```sql
UPDATE tasks
SET title = :title,
    description = :description,
    completed = :completed,
    updated_at = NOW()
WHERE id = :task_id AND user_id = :user_id
RETURNING *;
```

### Delete Task with Ownership Check

```sql
DELETE FROM tasks
WHERE id = :task_id AND user_id = :user_id
RETURNING id;
```

## Data Integrity Constraints

### Database Level

1. **Primary Key**: Ensures unique task IDs
2. **Foreign Key**: Ensures user_id references valid user
3. **NOT NULL**: Ensures required fields are always present
4. **CHECK Constraints**:
   - `title` length > 0 and <= 200
   - `description` length <= 2000 if not null

### Application Level

1. **Validation**: Pydantic schemas validate input before database operations
2. **Ownership Enforcement**: Service layer filters all queries by user_id
3. **Trim Whitespace**: Remove leading/trailing whitespace from title/description
4. **Timestamp Management**: Automatically set created_at and updated_at

## Migration Strategy

### Initial Migration (001_create_tasks_table)

```sql
-- Create tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL CHECK (LENGTH(title) > 0),
    description VARCHAR(2000),
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);

-- Note: Foreign key to users table will be added when User model is created in Spec 2
-- For now, user_id is just an integer field
```

### Future Migration (when User model is added)

```sql
-- Add foreign key constraint
ALTER TABLE tasks
ADD CONSTRAINT fk_tasks_user_id
FOREIGN KEY (user_id) REFERENCES users(id)
ON DELETE CASCADE;
```

## Data Access Patterns

### Service Layer Responsibilities

1. **Ownership Validation**: Always filter queries by user_id
2. **Input Sanitization**: Trim whitespace, validate lengths
3. **Error Handling**: Convert database errors to domain exceptions
4. **Transaction Management**: Use database transactions for consistency

### Repository Pattern (Optional)

For this feature, we'll use direct SQLModel queries in the service layer. A repository pattern could be added later if needed for additional abstraction.

## Testing Considerations

### Test Data Setup

```python
# Create test users
user1_id = 1
user2_id = 2

# Create test tasks
task1 = Task(title="User 1 Task", user_id=user1_id)
task2 = Task(title="User 2 Task", user_id=user2_id)
```

### Test Scenarios

1. **User Isolation**: Verify user1 cannot access task2
2. **Validation**: Test empty title, oversized fields
3. **Concurrent Updates**: Test last-write-wins behavior
4. **Cascade Delete**: Verify tasks deleted when user deleted (future)

## Performance Considerations

### Expected Load

- 100+ concurrent users
- Thousands of tasks per user
- <500ms response time target

### Optimizations

1. **Indexes**: user_id and composite (user_id, created_at) indexes
2. **Connection Pooling**: Reuse database connections
3. **Async Queries**: Non-blocking database operations
4. **Pagination**: Limit result set size for large task lists (future enhancement)

### Monitoring

- Track query execution times
- Monitor index usage
- Alert on slow queries (>500ms)

## Summary

The data model provides a simple, efficient structure for task management with strong user ownership enforcement. The design supports all functional requirements from the specification while maintaining data integrity and performance under load.
