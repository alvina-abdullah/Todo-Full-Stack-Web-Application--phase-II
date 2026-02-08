# Authentication Flow Documentation

**Feature**: 002-auth-security
**Date**: 2026-02-08
**Purpose**: Document authentication and authorization flows

## Overview

This document describes the complete authentication and authorization flows for the Todo application, including user signup, signin, JWT token issuance, token verification, and protected API access.

## Authentication Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Browser   │         │   Next.js    │         │   FastAPI   │
│  (Frontend) │         │  + Better    │         │   Backend   │
│             │         │    Auth      │         │             │
└──────┬──────┘         └──────┬───────┘         └──────┬──────┘
       │                       │                        │
       │                       │                        │
       │                  ┌────▼────┐                   │
       │                  │  Neon   │                   │
       │                  │  Postgres│                  │
       │                  │ Database │                  │
       │                  └─────────┘                   │
```

## Flow 1: User Signup

**Purpose**: Create new user account and issue JWT token

**Actors**: New user, Better Auth, Database

**Steps**:

1. **User submits signup form**
   - Input: email, password
   - Frontend validates: email format, password length ≥ 8

2. **Frontend sends signup request**
   ```http
   POST /api/auth/signup
   Content-Type: application/json

   {
     "email": "user@example.com",
     "password": "securepassword123"
   }
   ```

3. **Better Auth validates input**
   - Check email format
   - Check password length (min 8 characters)
   - Check email uniqueness in database

4. **Better Auth creates user**
   - Hash password with Bcrypt (cost factor 10)
   - Insert user into `users` table
   ```sql
   INSERT INTO users (email, password, created_at, updated_at)
   VALUES ('user@example.com', '$2b$10$...', NOW(), NOW())
   RETURNING id, email, created_at;
   ```

5. **Better Auth issues JWT token**
   - Create JWT payload:
   ```json
   {
     "userId": 1,
     "email": "user@example.com",
     "iat": 1707408000,
     "exp": 1707494400
   }
   ```
   - Sign with BETTER_AUTH_SECRET using HS256
   - Return token to frontend

6. **Frontend stores token**
   - Better Auth stores in httpOnly cookie
   - Cookie attributes: Secure, SameSite=Lax, HttpOnly

7. **Response to user**
   ```http
   HTTP/1.1 201 Created
   Set-Cookie: better-auth.session=<token>; HttpOnly; Secure; SameSite=Lax

   {
     "user": {
       "id": 1,
       "email": "user@example.com",
       "createdAt": "2026-02-08T12:00:00Z"
     }
   }
   ```

**Success Criteria**:
- User account created in database
- JWT token issued and stored
- User redirected to application

**Error Scenarios**:
- Email already exists → 400 Bad Request
- Invalid email format → 400 Bad Request
- Password too short → 400 Bad Request
- Database error → 500 Internal Server Error

---

## Flow 2: User Signin

**Purpose**: Authenticate existing user and issue JWT token

**Actors**: Existing user, Better Auth, Database

**Steps**:

1. **User submits signin form**
   - Input: email, password
   - Frontend validates: non-empty fields

2. **Frontend sends signin request**
   ```http
   POST /api/auth/signin
   Content-Type: application/json

   {
     "email": "user@example.com",
     "password": "securepassword123"
   }
   ```

3. **Better Auth looks up user**
   ```sql
   SELECT id, email, password, created_at
   FROM users
   WHERE email = 'user@example.com';
   ```

4. **Better Auth verifies password**
   - Compare submitted password with stored Bcrypt hash
   - Use constant-time comparison (prevents timing attacks)

5. **Better Auth issues JWT token** (if password valid)
   - Create JWT payload with userId and email
   - Sign with BETTER_AUTH_SECRET
   - Return token to frontend

6. **Frontend stores token**
   - Better Auth stores in httpOnly cookie
   - Same cookie attributes as signup

7. **Response to user**
   ```http
   HTTP/1.1 200 OK
   Set-Cookie: better-auth.session=<token>; HttpOnly; Secure; SameSite=Lax

   {
     "user": {
       "id": 1,
       "email": "user@example.com"
     }
   }
   ```

**Success Criteria**:
- User authenticated successfully
- JWT token issued and stored
- User redirected to application

**Error Scenarios**:
- Email not found → 401 Unauthorized
- Invalid password → 401 Unauthorized
- Account locked → 403 Forbidden (future feature)
- Database error → 500 Internal Server Error

---

## Flow 3: Protected API Request

**Purpose**: Access protected endpoint with JWT authentication

**Actors**: Authenticated user, Frontend, FastAPI Backend, Database

**Steps**:

1. **User initiates action** (e.g., view tasks)
   - Frontend needs to call backend API

2. **Frontend retrieves JWT token**
   ```typescript
   const session = await auth.api.getSession()
   const token = session.token
   ```

3. **Frontend sends API request with token**
   ```http
   GET /api/v1/tasks
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

4. **Backend extracts Authorization header**
   ```python
   # FastAPI dependency
   credentials: HTTPAuthorizationCredentials = Depends(security)
   token = credentials.credentials
   ```

5. **Backend verifies JWT token**
   ```python
   try:
       payload = jwt.decode(
           token,
           BETTER_AUTH_SECRET,
           algorithms=["HS256"]
       )
       user_id = payload["userId"]
   except jwt.ExpiredSignatureError:
       raise HTTPException(401, "Token expired")
   except jwt.JWTError:
       raise HTTPException(401, "Invalid token")
   ```

6. **Backend extracts user identity**
   - userId from JWT payload
   - No database lookup required (stateless)

7. **Backend queries database with user filter**
   ```sql
   SELECT id, title, description, completed, created_at, updated_at
   FROM tasks
   WHERE user_id = 1
   ORDER BY created_at DESC;
   ```

8. **Backend returns filtered results**
   ```http
   HTTP/1.1 200 OK
   Content-Type: application/json

   [
     {
       "id": 1,
       "title": "Buy groceries",
       "description": "Milk, eggs, bread",
       "completed": false,
       "userId": 1,
       "createdAt": "2026-02-08T12:00:00Z",
       "updatedAt": "2026-02-08T12:00:00Z"
     }
   ]
   ```

**Success Criteria**:
- Token verified successfully
- User identity extracted
- Data filtered by authenticated user
- Response returned

**Error Scenarios**:
- Missing Authorization header → 401 Unauthorized
- Invalid token signature → 401 Unauthorized
- Expired token → 401 Unauthorized
- Malformed token → 401 Unauthorized

---

## Flow 4: Token Expiration and Refresh

**Purpose**: Handle expired tokens gracefully

**Actors**: User, Frontend, Better Auth

**Steps**:

1. **Token expires** (after 24 hours)
   - exp claim in JWT payload exceeded

2. **User makes API request**
   - Frontend includes expired token

3. **Backend rejects request**
   ```http
   HTTP/1.1 401 Unauthorized
   Content-Type: application/json

   {
     "detail": "Token expired"
   }
   ```

4. **Frontend detects 401 response**
   ```typescript
   if (response.status === 401) {
     // Redirect to signin
     window.location.href = "/signin"
   }
   ```

5. **User redirected to signin page**
   - Must re-authenticate to get new token

**Future Enhancement**: Automatic token refresh
- Better Auth can refresh tokens before expiration
- Requires refresh token implementation
- Out of scope for this phase

---

## Flow 5: User Signout

**Purpose**: Clear authentication session

**Actors**: User, Frontend, Better Auth

**Steps**:

1. **User clicks signout button**
   - Frontend calls Better Auth signout

2. **Better Auth clears session**
   ```typescript
   await auth.api.signOut()
   ```

3. **Cookie cleared**
   ```http
   Set-Cookie: better-auth.session=; Max-Age=0; HttpOnly; Secure
   ```

4. **User redirected to signin page**
   ```typescript
   router.push("/signin")
   ```

**Success Criteria**:
- Session cookie cleared
- User redirected to signin
- Subsequent API requests fail with 401

---

## Flow 6: Cross-User Access Attempt (Security)

**Purpose**: Prevent users from accessing other users' data

**Actors**: User A, User B, Backend, Database

**Steps**:

1. **User A creates task**
   - Task ID: 1, user_id: 1

2. **User B attempts to access User A's task**
   ```http
   GET /api/v1/tasks/1
   Authorization: Bearer <User B's token>
   ```

3. **Backend verifies User B's token**
   - Extracts userId: 2

4. **Backend queries with user filter**
   ```sql
   SELECT * FROM tasks
   WHERE id = 1 AND user_id = 2;
   ```

5. **Query returns no results**
   - Task 1 belongs to user 1, not user 2

6. **Backend returns 404 Not Found**
   ```http
   HTTP/1.1 404 Not Found
   Content-Type: application/json

   {
     "detail": "Task with id 1 not found"
   }
   ```

**Security Properties**:
- User B cannot determine if task 1 exists
- No information leakage about other users' data
- Consistent 404 response (not 403)

---

## API Endpoint Changes

### Before Authentication (Temporary)

```http
GET /api/v1/tasks?user_id=1
POST /api/v1/tasks?user_id=1
```

**Issues**:
- user_id in query parameter (insecure)
- No verification of user identity
- Any user can access any user_id

### After Authentication (Secure)

```http
GET /api/v1/tasks
Authorization: Bearer <JWT token>

POST /api/v1/tasks
Authorization: Bearer <JWT token>
```

**Improvements**:
- user_id extracted from verified JWT token
- Token signature verified on every request
- Impossible to forge user identity

---

## Security Properties

### Authentication (Who are you?)

- **Mechanism**: Email + password → JWT token
- **Verification**: JWT signature verified with BETTER_AUTH_SECRET
- **Expiration**: Tokens expire after 24 hours
- **Storage**: httpOnly cookies (XSS protection)

### Authorization (What can you do?)

- **Mechanism**: user_id from JWT → database query filter
- **Enforcement**: All queries filter by authenticated user_id
- **Isolation**: Users can only access their own data
- **Consistency**: 404 for unauthorized access (no information leakage)

### Token Security

- **Signing**: HS256 algorithm with shared secret
- **Tampering**: Signature verification prevents payload modification
- **Expiration**: Short-lived tokens (24 hours)
- **Transmission**: HTTPS only (production)

### Password Security

- **Hashing**: Bcrypt with cost factor 10
- **Salt**: Automatically included in Bcrypt hash
- **Storage**: Never stored in plaintext
- **Verification**: Constant-time comparison

---

## Error Responses

### 401 Unauthorized

**Scenarios**:
- Missing Authorization header
- Invalid JWT signature
- Expired JWT token
- Malformed JWT token

**Response Format**:
```json
{
  "detail": "Missing authentication token"
}
```

### 403 Forbidden

**Scenarios**:
- Valid token but insufficient permissions (future feature)
- Account locked or disabled (future feature)

**Response Format**:
```json
{
  "detail": "Access denied"
}
```

### 404 Not Found

**Scenarios**:
- Resource doesn't exist in authenticated user's scope
- Prevents information leakage about other users' data

**Response Format**:
```json
{
  "detail": "Task with id 1 not found"
}
```

---

## Performance Characteristics

### JWT Verification

- **Time**: 1-5ms per request
- **Overhead**: Minimal (cryptographic operation)
- **Scalability**: Stateless (no database lookup)

### Database Queries

- **Filtering**: Indexed on user_id (fast)
- **Overhead**: None (queries already filtered)
- **Scalability**: Efficient with proper indexes

### Overall Impact

- **Latency**: <50ms added to API requests
- **Throughput**: No significant impact
- **Scalability**: Stateless authentication scales horizontally

---

## Testing Scenarios

### Positive Tests

1. Signup with valid credentials → 201 Created
2. Signin with valid credentials → 200 OK
3. Access protected endpoint with valid token → 200 OK
4. Create task with valid token → 201 Created
5. User can access their own tasks → 200 OK

### Negative Tests

1. Signup with existing email → 400 Bad Request
2. Signin with invalid password → 401 Unauthorized
3. Access protected endpoint without token → 401 Unauthorized
4. Access protected endpoint with expired token → 401 Unauthorized
5. Access protected endpoint with invalid signature → 401 Unauthorized
6. User A cannot access User B's tasks → 404 Not Found

### Security Tests

1. Token tampering detected → 401 Unauthorized
2. Expired token rejected → 401 Unauthorized
3. Cross-user access prevented → 404 Not Found
4. Password not exposed in responses → Verified
5. httpOnly cookie prevents JavaScript access → Verified

---

## Integration Points

### Frontend → Better Auth

- Signup/signin forms
- Session management
- Token storage (httpOnly cookies)
- Automatic token refresh (future)

### Frontend → Backend API

- Authorization header injection
- 401 response handling
- Automatic redirect to signin

### Backend → JWT Verification

- Token extraction from header
- Signature verification
- Payload decoding
- User identity extraction

### Backend → Database

- User-filtered queries
- Foreign key relationships
- Data isolation enforcement

---

## Future Enhancements

### Token Refresh

- Refresh tokens for long-lived sessions
- Automatic token renewal before expiration
- Reduces re-authentication frequency

### OAuth Providers

- Google, GitHub, Facebook login
- Social authentication integration
- Simplified signup process

### Two-Factor Authentication

- TOTP (Time-based One-Time Password)
- SMS verification
- Enhanced security for sensitive accounts

### Password Reset

- Forgot password flow
- Email verification
- Secure token-based reset

### Account Management

- Email change
- Password change
- Account deletion
- Profile management
