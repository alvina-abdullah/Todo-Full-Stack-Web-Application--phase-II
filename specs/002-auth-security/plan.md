# Implementation Plan: Authentication & Security

**Branch**: `main` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-auth-security/spec.md`

## Summary

Implement secure authentication using Better Auth on the Next.js frontend with JWT-based authorization on the FastAPI backend. Better Auth will handle user signup/signin and issue JWT tokens. The backend will verify JWT tokens on every request, extract user identity, and enforce strict data isolation. This replaces the temporary user_id query parameter with proper authentication.

## Technical Context

**Language/Version**:
- Frontend: TypeScript 5.x, Next.js 16+ (App Router)
- Backend: Python 3.11+

**Primary Dependencies**:
- Frontend: Better Auth (latest), Next.js 16+, React 19+
- Backend: FastAPI, PyJWT, python-jose[cryptography]

**Storage**:
- Neon Serverless PostgreSQL (existing)
- Better Auth will create users table via migrations

**Testing**:
- Frontend: Jest, React Testing Library
- Backend: pytest, pytest-asyncio, httpx
- Integration: End-to-end auth flow testing

**Target Platform**:
- Frontend: Vercel/Node.js server
- Backend: Linux server (containerized)

**Project Type**: Web application (full-stack)

**Performance Goals**:
- JWT verification <50ms per request
- Signup/signin flows complete in <30 seconds
- Support 1000 concurrent authenticated users

**Constraints**:
- Stateless authentication only (no server-side sessions)
- BETTER_AUTH_SECRET must be shared between frontend and backend
- JWT tokens must include user_id and email in payload
- All existing task endpoints must be protected

**Scale/Scope**:
- Multi-user application with strict data isolation
- Thousands of users with individual task lists
- JWT tokens valid for 24 hours (configurable)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Accuracy ✅
- **Requirement**: Enforce user ownership on all operations
- **Implementation**:
  - JWT tokens contain verified user_id
  - All database queries filter by authenticated user_id from token
  - Remove temporary user_id query parameter
- **Status**: PASS - JWT-based identity extraction ensures accurate user identification

### II. Security ✅
- **Requirement**: JWT validation on all protected endpoints
- **Implementation**:
  - Better Auth issues signed JWT tokens using BETTER_AUTH_SECRET
  - FastAPI middleware verifies JWT signature on every request
  - Invalid/missing/expired tokens return 401 Unauthorized
  - User data isolation enforced at query level
- **Status**: PASS - Comprehensive authentication and authorization

### III. Reproducibility ✅
- **Requirement**: Environment variables, migrations, locked dependencies
- **Implementation**:
  - BETTER_AUTH_SECRET in .env files (frontend and backend)
  - Better Auth migrations for users table
  - Updated requirements.txt with PyJWT dependencies
  - Updated package.json with Better Auth
- **Status**: PASS - Standard practices maintained

### IV. Clarity ✅
- **Requirement**: Clear error messages, meaningful names
- **Implementation**:
  - Descriptive error messages for auth failures
  - Clear HTTP status codes (401 for auth, 403 for authorization)
  - Well-documented JWT verification logic
  - Consistent naming conventions
- **Status**: PASS - Design follows conventions

### V. Responsiveness ✅
- **Requirement**: <50ms JWT verification overhead
- **Implementation**:
  - Efficient JWT decoding and verification
  - No database lookups for token verification (stateless)
  - Async operations throughout
- **Status**: PASS - Stateless JWT verification is fast

### API Standards ✅
- **Requirement**: RESTful conventions, proper HTTP status codes
- **Implementation**:
  - 401 Unauthorized for missing/invalid/expired tokens
  - 403 Forbidden for valid token but insufficient permissions
  - Authorization header: "Bearer {token}"
  - Existing RESTful endpoints maintained
- **Status**: PASS - Standards-compliant authentication

**Overall Gate Status**: ✅ PASS

## Project Structure

### Documentation (this feature)

```text
specs/002-auth-security/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── auth-flow.md     # Authentication flow documentation
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── lib/
│   │   ├── auth.ts              # Better Auth configuration
│   │   └── api-client.ts        # API client with JWT injection
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── signin/
│   │   │   │   └── page.tsx     # Sign in page
│   │   │   └── signup/
│   │   │       └── page.tsx     # Sign up page
│   │   └── api/
│   │       └── auth/
│   │           └── [...all]/    # Better Auth API routes
│   │               └── route.ts
│   └── middleware.ts            # Auth middleware for protected routes
├── .env.local                   # BETTER_AUTH_SECRET
└── package.json                 # Better Auth dependency

backend/
├── src/
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── jwt.py               # JWT verification utilities
│   │   └── dependencies.py      # get_current_user dependency
│   ├── api/
│   │   ├── tasks.py             # Updated with JWT auth (remove user_id param)
│   │   └── dependencies.py      # Updated get_current_user_id
│   └── main.py                  # Updated with auth middleware
├── .env                         # BETTER_AUTH_SECRET
└── requirements.txt             # PyJWT, python-jose

database/
└── migrations/                  # Better Auth creates users table
```

**Structure Decision**: Full-stack web application with separate frontend and backend directories. Frontend uses Next.js App Router structure. Backend maintains existing FastAPI structure with new auth module.

## Architecture Decisions

### ADR-001: Better Auth for Frontend Authentication

**Context**: Need secure, production-ready authentication for Next.js frontend.

**Decision**: Use Better Auth library instead of custom authentication.

**Rationale**:
- Production-tested authentication library
- Built-in JWT support
- Handles password hashing, validation, session management
- Next.js App Router compatible
- Reduces security risks from custom implementation

**Alternatives Considered**:
- NextAuth.js: More complex, session-based by default
- Custom implementation: Higher security risk, more development time
- Clerk/Auth0: Third-party services, additional cost

**Consequences**:
- Dependency on Better Auth library
- Must follow Better Auth conventions
- Simplified development and reduced security risks

### ADR-002: JWT Tokens for Stateless Authorization

**Context**: Backend needs to verify user identity on every request.

**Decision**: Use JWT tokens signed with shared secret (BETTER_AUTH_SECRET).

**Rationale**:
- Stateless: No server-side session storage required
- Scalable: No session database lookups
- Standard: Industry-standard authorization mechanism
- Fast: Token verification is cryptographic operation only

**Alternatives Considered**:
- Session-based auth: Requires session storage, database lookups
- API keys: Less secure, no expiration
- OAuth2: Overkill for internal API

**Consequences**:
- BETTER_AUTH_SECRET must be kept secure and synchronized
- Token expiration requires re-authentication
- Cannot revoke individual tokens (stateless trade-off)

### ADR-003: Shared Secret Between Frontend and Backend

**Context**: Backend must verify JWT tokens issued by Better Auth.

**Decision**: Use shared BETTER_AUTH_SECRET for signing and verification.

**Rationale**:
- Simplest approach for monolithic deployment
- Better Auth signs tokens, FastAPI verifies with same secret
- No public/private key infrastructure needed
- Sufficient security for internal API

**Alternatives Considered**:
- Public/private key pairs: More complex, unnecessary for this use case
- Separate secrets: Would break JWT verification
- Token introspection endpoint: Adds latency and complexity

**Consequences**:
- Secret must be securely stored in both environments
- Secret rotation requires coordinated deployment
- Compromise of secret affects entire system

## Phase 0: Research

### Research Areas

1. **Better Auth JWT Configuration**
   - How to configure Better Auth to issue JWT tokens
   - JWT payload customization (user_id, email)
   - Token expiration configuration
   - Session storage options

2. **PyJWT Best Practices**
   - JWT verification in FastAPI
   - Error handling for expired/invalid tokens
   - Performance optimization
   - Security considerations

3. **FastAPI Dependency Injection for Auth**
   - Creating reusable auth dependencies
   - Extracting user identity from JWT
   - Applying auth to all endpoints
   - Error response formatting

4. **Better Auth Database Migrations**
   - Users table schema
   - Integration with existing Neon database
   - Migration execution process

5. **Frontend Token Management**
   - Better Auth session handling
   - Automatic token inclusion in API requests
   - Token refresh strategies
   - Logout implementation

6. **Security Best Practices**
   - HTTPS enforcement
   - CORS configuration
   - Token storage (httpOnly cookies vs localStorage)
   - XSS prevention

7. **Testing Strategies**
   - Testing authenticated endpoints
   - Mocking JWT tokens in tests
   - Integration testing auth flows
   - Security testing (invalid tokens, expired tokens)

**Output**: research.md with findings and decisions for each area

## Phase 1: Design

### Data Model

**User Entity** (created by Better Auth):
- id: Primary key (UUID or integer)
- email: Unique, indexed
- password_hash: Bcrypt hashed
- created_at: Timestamp
- updated_at: Timestamp

**Task Entity** (existing, no changes):
- id: Primary key
- title: String
- description: String (optional)
- completed: Boolean
- user_id: Foreign key to User (existing)
- created_at: Timestamp
- updated_at: Timestamp

**JWT Token Payload**:
- user_id: Integer (identifies user)
- email: String (user's email)
- exp: Expiration timestamp
- iat: Issued at timestamp

### API Contract Changes

**Authentication Endpoints** (provided by Better Auth):
- POST /api/auth/signup - Create new user account
- POST /api/auth/signin - Authenticate and receive JWT token
- POST /api/auth/signout - Clear session

**Modified Task Endpoints** (remove user_id query parameter):
- GET /api/v1/tasks - List tasks (user from JWT)
- GET /api/v1/tasks/{id} - Get task (user from JWT)
- POST /api/v1/tasks - Create task (user from JWT)
- PUT /api/v1/tasks/{id} - Replace task (user from JWT)
- PATCH /api/v1/tasks/{id} - Update task (user from JWT)
- DELETE /api/v1/tasks/{id} - Delete task (user from JWT)

**New Response Codes**:
- 401 Unauthorized: Missing, invalid, or expired JWT token
- 403 Forbidden: Valid token but insufficient permissions (kept for consistency)

### Integration Points

1. **Frontend → Better Auth**
   - Signup/signin forms call Better Auth
   - Better Auth issues JWT token
   - Token stored in Better Auth session

2. **Frontend → Backend API**
   - API client retrieves JWT from Better Auth session
   - Includes token in Authorization header
   - Handles 401 responses by redirecting to signin

3. **Backend JWT Verification**
   - Middleware extracts Authorization header
   - Verifies JWT signature using BETTER_AUTH_SECRET
   - Decodes payload and extracts user_id
   - Injects user_id into request context

4. **Backend → Database**
   - All task queries filter by user_id from JWT
   - User isolation enforced at query level

**Output**: data-model.md, contracts/auth-flow.md, quickstart.md

## Implementation Phases

### Phase 1: Better Auth Setup (Frontend)
- Install Better Auth package
- Configure Better Auth with JWT plugin
- Set up BETTER_AUTH_SECRET environment variable
- Create Better Auth API routes
- Implement signup/signin pages

### Phase 2: JWT Verification (Backend)
- Install PyJWT and python-jose
- Create JWT verification utilities
- Implement get_current_user dependency
- Add BETTER_AUTH_SECRET to backend .env
- Create authentication middleware

### Phase 3: Protect Task Endpoints
- Update all task endpoints to use get_current_user
- Remove user_id query parameter
- Update service layer to use authenticated user_id
- Add 401 error handling

### Phase 4: Frontend API Client
- Create centralized API client
- Implement automatic JWT token injection
- Handle 401 responses (redirect to signin)
- Update all API calls to use new client

### Phase 5: Testing & Validation
- Test signup/signin flows
- Test JWT token issuance
- Test protected endpoints with valid tokens
- Test 401 responses for invalid tokens
- Test user data isolation
- Security testing (cross-user access attempts)

## Testing Strategy

### Unit Tests
- JWT verification logic
- Token payload extraction
- Error handling for invalid tokens

### Integration Tests
- Complete signup flow
- Complete signin flow
- Protected endpoint access with valid token
- Protected endpoint rejection without token
- User data isolation (User A cannot access User B's tasks)

### Security Tests
- Expired token rejection
- Invalid signature rejection
- Malformed token rejection
- Cross-user access attempts
- Token tampering detection

### Manual Testing
- End-to-end user flows
- Token expiration behavior
- Logout functionality
- Error message clarity

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| BETTER_AUTH_SECRET mismatch | Document setup process, validate in tests |
| Token expiration UX issues | Set reasonable expiration (24h), document refresh strategy |
| Better Auth compatibility | Verify Next.js 16+ compatibility before starting |
| Performance degradation | Benchmark JWT verification, optimize if needed |
| Security vulnerabilities | Follow security best practices, security testing |

## Success Criteria

- ✅ Users can sign up and sign in successfully
- ✅ Better Auth issues valid JWT tokens
- ✅ Backend verifies JWT tokens on all requests
- ✅ Invalid/missing tokens return 401
- ✅ User identity correctly extracted from JWT
- ✅ All task operations enforce user isolation
- ✅ Zero cross-user data access
- ✅ JWT verification adds <50ms latency

## Next Steps

1. Execute Phase 0 research (create research.md)
2. Execute Phase 1 design (create data-model.md, contracts/, quickstart.md)
3. Run `/sp.tasks` to generate task breakdown
4. Implement according to task plan
