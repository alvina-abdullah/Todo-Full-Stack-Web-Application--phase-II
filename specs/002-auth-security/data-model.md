# Data Model: Authentication & Security

**Feature**: 002-auth-security
**Date**: 2026-02-08
**Purpose**: Define data entities, relationships, and validation rules

## Entity Overview

This feature introduces the **User** entity and modifies how the existing **Task** entity relates to users through JWT-based authentication.

## Entities

### User

**Purpose**: Represents an authenticated user account in the system.

**Managed By**: Better Auth (frontend library handles creation, authentication, password hashing)

**Storage**: `users` table in Neon PostgreSQL database

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTO_INCREMENT | Unique user identifier |
| email | String (255) | UNIQUE, NOT NULL, INDEX | User's email address (used for signin) |
| password | String (255) | NOT NULL | Bcrypt hashed password (never stored in plaintext) |
| name | String (255) | NULLABLE | User's display name (optional) |
| created_at | Timestamp | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| updated_at | Timestamp | NOT NULL, DEFAULT NOW() | Last account update timestamp |

**Validation Rules**:
- Email must be valid email format (validated by Better Auth)
- Email must be unique across all users
- Password must be at least 8 characters (enforced by Better Auth)
- Password is automatically hashed with Bcrypt before storage

**Indexes**:
- Primary key index on `id`
- Unique index on `email` (for fast lookup during signin)

**Relationships**:
- One-to-Many with Task: One user can have many tasks
- Referenced by: `tasks.user_id` foreign key

**Lifecycle**:
- Created: When user signs up via Better Auth
- Updated: When user changes profile information (future feature)
- Deleted: Not implemented in this phase (future feature)

**Security Considerations**:
- Password never exposed in API responses
- Email used as unique identifier for authentication
- Bcrypt hashing prevents password recovery if database compromised

---

### Task (Existing Entity - Modified Usage)

**Purpose**: Represents a todo task belonging to a specific user.

**Storage**: `tasks` table in Neon PostgreSQL database (already exists)

**Attributes**: (No schema changes)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTO_INCREMENT | Unique task identifier |
| title | String (200) | NOT NULL, MIN_LENGTH 1 | Task title |
| description | String (2000) | NULLABLE | Task description (optional) |
| completed | Boolean | NOT NULL, DEFAULT FALSE | Task completion status |
| user_id | Integer | NOT NULL, FOREIGN KEY, INDEX | Owner of the task |
| created_at | Timestamp | NOT NULL, DEFAULT NOW() | Task creation timestamp |
| updated_at | Timestamp | NOT NULL, DEFAULT NOW() | Last task update timestamp |

**Changes from Previous Implementation**:
- **Before**: `user_id` passed as query parameter (temporary, insecure)
- **After**: `user_id` extracted from verified JWT token (secure, automatic)
- Schema remains unchanged - only how `user_id` is populated changes

**Validation Rules**: (Unchanged)
- Title must be 1-200 characters
- Description max 2000 characters
- user_id must reference valid user

**Indexes**: (Unchanged)
- Primary key index on `id`
- Index on `user_id` (for efficient user-specific queries)
- Composite index on `(user_id, created_at)` (for ordered user queries)

**Relationships**:
- Many-to-One with User: Each task belongs to exactly one user
- Foreign key: `user_id` references `users.id`

**Data Isolation**:
- All queries MUST filter by `user_id` from authenticated JWT token
- Users can only access, modify, or delete their own tasks
- Attempting to access another user's task returns 404 (not found in scope)

---

### JWT Token (Transient Entity)

**Purpose**: Represents an authentication credential issued by Better Auth and verified by FastAPI backend.

**Storage**: Not persisted in database (stateless authentication)

**Lifecycle**: Issued upon signin, expires after 24 hours, verified on each request

**Payload Structure**:

| Field | Type | Description |
|-------|------|-------------|
| userId | Integer | User's unique identifier (maps to users.id) |
| email | String | User's email address |
| exp | Integer (Unix timestamp) | Token expiration time |
| iat | Integer (Unix timestamp) | Token issued at time |

**Validation Rules**:
- Token must be signed with BETTER_AUTH_SECRET
- Token must not be expired (exp > current time)
- Token must contain userId and email claims
- Signature must be valid (prevents tampering)

**Security Properties**:
- Signed with HS256 algorithm
- Cannot be forged without BETTER_AUTH_SECRET
- Stateless (no server-side storage required)
- Self-contained (all user info in payload)

**Usage Flow**:
1. User signs in via Better Auth
2. Better Auth issues JWT token with user info
3. Frontend stores token in httpOnly cookie
4. Frontend includes token in Authorization header for API requests
5. Backend verifies token signature and extracts userId
6. Backend uses userId to filter database queries

---

## Entity Relationships

```
┌─────────────┐
│    User     │
│             │
│ id (PK)     │
│ email       │
│ password    │
│ name        │
│ created_at  │
│ updated_at  │
└──────┬──────┘
       │
       │ 1:N
       │
       ▼
┌─────────────┐
│    Task     │
│             │
│ id (PK)     │
│ title       │
│ description │
│ completed   │
│ user_id (FK)│◄─── References User.id
│ created_at  │
│ updated_at  │
└─────────────┘

JWT Token (transient)
┌─────────────┐
│  JWT Token  │
│             │
│ userId      │◄─── Maps to User.id
│ email       │
│ exp         │
│ iat         │
└─────────────┘
```

## Database Schema

### Users Table (Created by Better Auth)

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_users_email ON users(email);
```

### Tasks Table (Already Exists - No Changes)

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL CHECK (LENGTH(title) >= 1),
    description VARCHAR(2000),
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    user_id INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);
```

## Data Flow

### User Signup Flow

1. User submits signup form (email, password)
2. Better Auth validates input (email format, password length)
3. Better Auth hashes password with Bcrypt
4. Better Auth inserts new user into `users` table
5. Better Auth issues JWT token with userId and email
6. Frontend stores token in httpOnly cookie

### User Signin Flow

1. User submits signin form (email, password)
2. Better Auth looks up user by email
3. Better Auth verifies password against stored hash
4. If valid, Better Auth issues JWT token with userId and email
5. Frontend stores token in httpOnly cookie

### Authenticated API Request Flow

1. Frontend retrieves JWT token from Better Auth session
2. Frontend includes token in Authorization header: `Bearer {token}`
3. Backend extracts token from Authorization header
4. Backend verifies token signature using BETTER_AUTH_SECRET
5. Backend decodes token payload and extracts userId
6. Backend uses userId to filter database queries
7. Backend returns only data belonging to authenticated user

### Task Creation with Authentication

1. User creates task via frontend form
2. Frontend sends POST request with JWT token in header
3. Backend verifies JWT and extracts userId
4. Backend creates task with user_id from JWT (not from request body)
5. Task is associated with authenticated user automatically
6. Backend returns created task

## Data Validation

### User Entity Validation

**Email Validation**:
- Format: Must match email regex pattern
- Uniqueness: Must not already exist in database
- Required: Cannot be null or empty

**Password Validation**:
- Length: Minimum 8 characters
- Hashing: Automatically hashed with Bcrypt (cost factor 10)
- Storage: Never stored in plaintext

### Task Entity Validation (Unchanged)

**Title Validation**:
- Length: 1-200 characters
- Required: Cannot be null or empty
- Trimming: Whitespace trimmed before storage

**Description Validation**:
- Length: Maximum 2000 characters
- Optional: Can be null or empty

**User ID Validation**:
- Source: Must come from verified JWT token (not user input)
- Existence: Must reference valid user in users table
- Immutable: Cannot be changed after task creation

### JWT Token Validation

**Signature Validation**:
- Algorithm: HS256
- Secret: BETTER_AUTH_SECRET
- Verification: Signature must match payload + secret

**Expiration Validation**:
- Current time must be less than exp claim
- Expired tokens rejected with 401 Unauthorized

**Payload Validation**:
- userId claim must be present and integer
- email claim must be present and string
- Claims must not be tampered with (signature verification)

## Data Migration

### Migration Strategy

**No database migration required** for existing data:
- Users table created by Better Auth on first run
- Tasks table already exists with user_id column
- Existing tasks can remain (will be orphaned until users created)
- Or: Create initial users and update existing tasks' user_id

**Recommended Approach**:
1. Deploy Better Auth and create users table
2. Create test users via signup
3. Update existing tasks to assign to test users (if any exist)
4. Or: Start fresh with no existing tasks

## Data Integrity

### Referential Integrity

- Foreign key constraint: `tasks.user_id` REFERENCES `users.id`
- Cascade behavior: Not defined (user deletion not implemented)
- Orphaned tasks: Prevented by foreign key constraint

### Data Isolation

- Query-level filtering: All task queries filter by authenticated user_id
- No cross-user access: Users cannot see other users' tasks
- Enforcement: Backend automatically applies user_id filter from JWT

### Consistency

- Timestamps: Automatically managed by database
- Password hashing: Automatically managed by Better Auth
- User ID assignment: Automatically extracted from JWT token

## Performance Considerations

### Indexes

- `users.email`: Unique index for fast signin lookups
- `tasks.user_id`: Index for efficient user-specific queries
- `tasks.(user_id, created_at)`: Composite index for ordered queries

### Query Optimization

- User lookup by email: O(log n) with index
- Task queries by user_id: O(log n) with index
- JWT verification: O(1) cryptographic operation (no database lookup)

### Scalability

- Stateless JWT: No session storage required
- Connection pooling: Efficient database connection reuse
- Async operations: Non-blocking I/O for concurrent requests

## Security Considerations

### Password Security

- Bcrypt hashing: Industry-standard, slow by design (prevents brute force)
- Salt: Automatically included in Bcrypt hash
- Cost factor: 10 (configurable, balances security and performance)

### Token Security

- Signed tokens: Cannot be forged without secret
- Short expiration: 24 hours (limits damage if stolen)
- httpOnly cookies: Not accessible to JavaScript (XSS protection)

### Data Isolation

- Query filtering: Enforced at database query level
- No user input: user_id from JWT, not request parameters
- Foreign key constraints: Prevent invalid user_id values

## Future Considerations

### Potential Enhancements

- User profile fields (avatar, bio, preferences)
- Email verification (confirm email ownership)
- Password reset flow (forgot password)
- Account deletion (soft delete with data retention)
- User roles (admin, moderator, user)
- Audit logging (track user actions)

### Schema Evolution

- Add fields to users table as needed
- Maintain backward compatibility with existing tasks
- Use database migrations (Alembic) for schema changes
- Version API contracts for breaking changes
