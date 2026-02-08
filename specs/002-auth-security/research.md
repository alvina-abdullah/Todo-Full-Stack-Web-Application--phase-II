# Research: Authentication & Security

**Feature**: 002-auth-security
**Date**: 2026-02-08
**Purpose**: Resolve technical unknowns and establish implementation approach

## Research Area 1: Better Auth JWT Configuration

### Decision: Use Better Auth with JWT Plugin

**Research Findings**:
- Better Auth supports JWT tokens through its core functionality
- Configuration via `auth.ts` file in Next.js project
- JWT tokens automatically issued upon successful authentication
- Token payload customizable through Better Auth configuration

**Configuration Approach**:
```typescript
// lib/auth.ts
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET,
  database: {
    // Neon PostgreSQL connection
    provider: "postgres",
    url: process.env.DATABASE_URL
  },
  session: {
    expiresIn: 60 * 60 * 24, // 24 hours
    updateAge: 60 * 60 * 24, // Update every 24 hours
  },
  jwt: {
    enabled: true,
    expiresIn: 60 * 60 * 24, // 24 hours
  }
})
```

**JWT Payload Structure**:
- Better Auth automatically includes: `userId`, `email`, `exp`, `iat`
- Custom claims can be added via session callbacks
- Payload is signed with BETTER_AUTH_SECRET

**Rationale**: Better Auth provides production-ready JWT support with minimal configuration.

**Alternatives Considered**:
- Custom JWT implementation: More work, higher security risk
- NextAuth.js: More complex, session-based by default

---

## Research Area 2: PyJWT Best Practices

### Decision: Use python-jose for JWT Verification

**Research Findings**:
- `python-jose[cryptography]` is the recommended library for FastAPI
- Provides JWT decoding, verification, and error handling
- Better performance than pure PyJWT
- Well-documented FastAPI integration patterns

**Implementation Pattern**:
```python
from jose import jwt, JWTError
from fastapi import HTTPException, status

SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
ALGORITHM = "HS256"

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("userId")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
```

**Error Handling**:
- `ExpiredSignatureError`: Token has expired
- `JWTError`: Invalid signature or malformed token
- Missing claims: Invalid token structure

**Performance Considerations**:
- JWT verification is cryptographic operation (~1-5ms)
- No database lookups required (stateless)
- Can cache decoded token in request context

**Rationale**: python-jose is the FastAPI-recommended library with excellent performance and error handling.

**Alternatives Considered**:
- PyJWT: Works but less FastAPI-specific documentation
- authlib: More features than needed

---

## Research Area 3: FastAPI Dependency Injection for Auth

### Decision: Create Reusable get_current_user Dependency

**Research Findings**:
- FastAPI dependencies are the standard pattern for authentication
- Dependencies can be reused across all endpoints
- Automatic error handling and response formatting
- Type-safe user identity extraction

**Implementation Pattern**:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """Extract and verify JWT token, return user_id."""
    token = credentials.credentials
    payload = verify_token(token)
    return payload["userId"]
```

**Usage in Endpoints**:
```python
@router.get("/tasks")
async def list_tasks(
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user)
):
    # user_id is automatically extracted from JWT
    tasks = await TaskService.list_tasks(session, user_id)
    return tasks
```

**Benefits**:
- Automatic Authorization header extraction
- Consistent error responses (401 for auth failures)
- Type-safe user_id injection
- Easy to test (can mock dependency)

**Rationale**: FastAPI dependencies provide clean, reusable authentication with automatic error handling.

**Alternatives Considered**:
- Middleware: Less granular control, harder to test
- Manual header extraction: Repetitive, error-prone

---

## Research Area 4: Better Auth Database Migrations

### Decision: Let Better Auth Manage Users Table

**Research Findings**:
- Better Auth automatically creates users table on first run
- Uses existing database connection (Neon PostgreSQL)
- Schema includes: id, email, password (hashed), createdAt, updatedAt
- Compatible with existing Alembic migrations for tasks table

**Users Table Schema** (created by Better Auth):
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,  -- Bcrypt hashed
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
```

**Integration with Existing Database**:
- Better Auth connects to same Neon database
- No conflicts with existing tasks table
- Foreign key relationship: tasks.user_id → users.id (already exists)

**Migration Strategy**:
1. Configure Better Auth with DATABASE_URL
2. Run Next.js app (Better Auth auto-creates tables)
3. Verify users table exists
4. Existing tasks table user_id column already compatible

**Rationale**: Better Auth's automatic migration is simpler and less error-prone than manual schema management.

**Alternatives Considered**:
- Manual SQL migrations: More control but more work
- Alembic migrations for users: Duplicates Better Auth's work

---

## Research Area 5: Frontend Token Management

### Decision: Use Better Auth Session with Automatic Token Injection

**Research Findings**:
- Better Auth provides `useSession()` hook for React
- Tokens stored in httpOnly cookies (secure by default)
- Automatic token refresh before expiration
- Built-in session management

**Implementation Pattern**:

**API Client with Token Injection**:
```typescript
// lib/api-client.ts
import { auth } from "./auth"

export async function apiClient(endpoint: string, options: RequestInit = {}) {
  const session = await auth.api.getSession()

  if (!session) {
    throw new Error("Not authenticated")
  }

  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
    ...options,
    headers: {
      ...options.headers,
      "Authorization": `Bearer ${session.token}`,
      "Content-Type": "application/json",
    },
  })

  if (response.status === 401) {
    // Token expired or invalid, redirect to signin
    window.location.href = "/signin"
    throw new Error("Authentication required")
  }

  return response
}
```

**Usage in Components**:
```typescript
// app/tasks/page.tsx
import { apiClient } from "@/lib/api-client"

async function getTasks() {
  const response = await apiClient("/api/v1/tasks")
  return response.json()
}
```

**Session Management**:
- Better Auth handles token storage (httpOnly cookies)
- Automatic token refresh before expiration
- `useSession()` hook provides session state
- Logout clears session and redirects

**Rationale**: Better Auth's built-in session management is secure and handles edge cases automatically.

**Alternatives Considered**:
- localStorage: Vulnerable to XSS attacks
- Manual cookie management: Complex, error-prone
- Session storage: Lost on tab close

---

## Research Area 6: Security Best Practices

### Decision: Implement Defense-in-Depth Security

**Research Findings**:
- Multiple security layers reduce risk
- HTTPS, CORS, httpOnly cookies, JWT verification all important
- XSS prevention through React's built-in escaping
- CSRF protection through SameSite cookies

**Security Measures**:

**1. HTTPS Enforcement**:
- Production deployment must use HTTPS
- Prevents token interception
- Configured at deployment level (Vercel, etc.)

**2. CORS Configuration**:
```python
# backend/src/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL")],  # Specific origin, not "*"
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

**3. Token Storage**:
- httpOnly cookies (Better Auth default)
- Not accessible to JavaScript (XSS protection)
- SameSite=Lax (CSRF protection)

**4. JWT Security**:
- Strong secret (32+ random characters)
- Short expiration (24 hours)
- Signature verification on every request
- No sensitive data in payload

**5. Password Security**:
- Bcrypt hashing (Better Auth default)
- Minimum 8 characters enforced
- Email validation

**6. Input Validation**:
- Pydantic validation on backend
- React form validation on frontend
- SQL injection prevention (SQLModel parameterized queries)

**Rationale**: Multiple security layers provide comprehensive protection against common attacks.

**Alternatives Considered**:
- Single security measure: Insufficient protection
- Complex security: Overkill for this application

---

## Research Area 7: Testing Strategies

### Decision: Multi-Layer Testing Approach

**Research Findings**:
- Unit tests for JWT verification logic
- Integration tests for auth flows
- Security tests for attack scenarios
- Manual testing for UX validation

**Testing Approach**:

**1. Backend Unit Tests**:
```python
# tests/test_jwt.py
def test_verify_valid_token():
    token = create_test_token(user_id=1)
    payload = verify_token(token)
    assert payload["userId"] == 1

def test_verify_expired_token():
    token = create_expired_token()
    with pytest.raises(HTTPException) as exc:
        verify_token(token)
    assert exc.value.status_code == 401

def test_verify_invalid_signature():
    token = create_token_with_wrong_secret()
    with pytest.raises(HTTPException) as exc:
        verify_token(token)
    assert exc.value.status_code == 401
```

**2. Integration Tests**:
```python
# tests/test_auth_integration.py
async def test_protected_endpoint_with_valid_token(client):
    # Create user and get token
    token = await create_user_and_signin()

    # Access protected endpoint
    response = await client.get(
        "/api/v1/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

async def test_protected_endpoint_without_token(client):
    response = await client.get("/api/v1/tasks")
    assert response.status_code == 401
```

**3. Security Tests**:
```python
# tests/test_security.py
async def test_user_cannot_access_other_users_tasks(client):
    # Create two users
    token1 = await create_user_and_signin("user1@example.com")
    token2 = await create_user_and_signin("user2@example.com")

    # User 1 creates task
    task = await create_task(client, token1, "User 1 task")

    # User 2 tries to access User 1's task
    response = await client.get(
        f"/api/v1/tasks/{task['id']}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert response.status_code == 404  # Not found in User 2's scope
```

**4. Frontend Tests**:
```typescript
// __tests__/auth.test.tsx
test("redirects to signin when not authenticated", async () => {
  render(<TasksPage />)
  await waitFor(() => {
    expect(window.location.href).toContain("/signin")
  })
})

test("includes JWT token in API requests", async () => {
  const mockFetch = jest.fn()
  global.fetch = mockFetch

  await apiClient("/api/v1/tasks")

  expect(mockFetch).toHaveBeenCalledWith(
    expect.any(String),
    expect.objectContaining({
      headers: expect.objectContaining({
        "Authorization": expect.stringMatching(/^Bearer /)
      })
    })
  )
})
```

**Test Coverage Goals**:
- JWT verification: 100%
- Auth endpoints: 100%
- Protected endpoints: 100%
- Security scenarios: All critical paths

**Rationale**: Comprehensive testing ensures authentication works correctly and securely.

**Alternatives Considered**:
- Manual testing only: Insufficient for security-critical code
- Unit tests only: Misses integration issues

---

## Summary of Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| Frontend Auth | Better Auth with JWT | Production-ready, Next.js compatible |
| Backend JWT | python-jose | FastAPI-recommended, excellent performance |
| Auth Pattern | FastAPI dependencies | Clean, reusable, type-safe |
| Database | Better Auth auto-migration | Simpler, less error-prone |
| Token Storage | httpOnly cookies | Secure against XSS |
| Security | Defense-in-depth | Multiple layers of protection |
| Testing | Multi-layer approach | Comprehensive coverage |

## Implementation Readiness

All research areas resolved. Ready to proceed to Phase 1 (Design).

**Next Steps**:
1. Create data-model.md with detailed entity schemas
2. Create contracts/auth-flow.md with authentication flow documentation
3. Create quickstart.md with setup and testing instructions
4. Update agent context with new technologies
