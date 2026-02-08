# Quickstart Guide: Authentication & Security

**Feature**: 002-auth-security
**Date**: 2026-02-08
**Purpose**: Setup and testing instructions for authentication implementation

## Prerequisites

Before starting, ensure you have:

- ✅ Feature 001 (Task CRUD API) completed and working
- ✅ Node.js 18+ installed
- ✅ Python 3.11+ installed
- ✅ Neon PostgreSQL database configured
- ✅ Backend virtual environment set up
- ✅ Frontend Next.js project initialized

## Environment Setup

### 1. Generate Shared Secret

Generate a strong random secret for JWT signing:

```bash
# Generate 32-byte random secret
openssl rand -base64 32
```

Copy the output (e.g., `dGhpc2lzYXNlY3JldGtleWZvcmp3dHRva2Vucw==`)

### 2. Configure Backend Environment

Edit `backend/.env`:

```env
# Existing configuration
DATABASE_URL=postgresql+asyncpg://user:pass@host/db

# Add authentication configuration
BETTER_AUTH_SECRET=dGhpc2lzYXNlY3JldGtleWZvcmp3dHRva2Vucw==

# Add frontend URL for CORS
FRONTEND_URL=http://localhost:3000
```

### 3. Configure Frontend Environment

Create `frontend/.env.local`:

```env
# Better Auth configuration
BETTER_AUTH_SECRET=dGhpc2lzYXNlY3JldGtleWZvcmp3dHRva2Vucw==

# Database connection (same as backend)
DATABASE_URL=postgresql://user:pass@host/db

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8001
```

**Important**: Use the **same** BETTER_AUTH_SECRET in both frontend and backend!

### 4. Install Dependencies

**Backend**:
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install python-jose[cryptography] passlib[bcrypt]
pip freeze > requirements.txt
```

**Frontend**:
```bash
cd frontend
npm install better-auth
```

## Implementation Steps

### Step 1: Backend JWT Verification

**Create JWT utilities** (`backend/src/auth/jwt.py`):

```python
import os
from jose import jwt, JWTError
from fastapi import HTTPException, status

SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
ALGORITHM = "HS256"

def verify_token(token: str) -> dict:
    """Verify JWT token and return payload."""
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

**Create auth dependency** (`backend/src/auth/dependencies.py`):

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .jwt import verify_token

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """Extract and verify JWT token, return user_id."""
    token = credentials.credentials
    payload = verify_token(token)
    return payload["userId"]
```

**Update task endpoints** (`backend/src/api/tasks.py`):

```python
# Remove old import
# from .dependencies import get_current_user_id

# Add new import
from ..auth.dependencies import get_current_user

# Update all endpoints - example:
@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user)  # Changed from get_current_user_id
) -> List[TaskResponse]:
    """List all tasks for authenticated user."""
    tasks = await TaskService.list_tasks(session, user_id)
    return [TaskResponse.model_validate(task) for task in tasks]
```

**Update CORS** (`backend/src/main.py`):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### Step 2: Frontend Better Auth Setup

**Create Better Auth configuration** (`frontend/src/lib/auth.ts`):

```typescript
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET!,
  database: {
    provider: "postgres",
    url: process.env.DATABASE_URL!,
  },
  session: {
    expiresIn: 60 * 60 * 24, // 24 hours
    updateAge: 60 * 60 * 24,
  },
})
```

**Create Better Auth API route** (`frontend/src/app/api/auth/[...all]/route.ts`):

```typescript
import { auth } from "@/lib/auth"

export const { GET, POST } = auth.handler
```

**Create API client** (`frontend/src/lib/api-client.ts`):

```typescript
import { auth } from "./auth"

export async function apiClient(endpoint: string, options: RequestInit = {}) {
  const session = await auth.api.getSession()

  if (!session) {
    throw new Error("Not authenticated")
  }

  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}${endpoint}`,
    {
      ...options,
      headers: {
        ...options.headers,
        Authorization: `Bearer ${session.token}`,
        "Content-Type": "application/json",
      },
    }
  )

  if (response.status === 401) {
    window.location.href = "/signin"
    throw new Error("Authentication required")
  }

  return response
}
```

**Create signin page** (`frontend/src/app/(auth)/signin/page.tsx`):

```typescript
"use client"

import { useState } from "react"
import { auth } from "@/lib/auth"
import { useRouter } from "next/navigation"

export default function SignInPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const router = useRouter()

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError("")

    try {
      await auth.api.signIn.email({
        email,
        password,
      })
      router.push("/tasks")
    } catch (err) {
      setError("Invalid email or password")
    }
  }

  return (
    <div>
      <h1>Sign In</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          required
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          required
        />
        <button type="submit">Sign In</button>
        {error && <p>{error}</p>}
      </form>
    </div>
  )
}
```

**Create signup page** (`frontend/src/app/(auth)/signup/page.tsx`):

```typescript
"use client"

import { useState } from "react"
import { auth } from "@/lib/auth"
import { useRouter } from "next/navigation"

export default function SignUpPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const router = useRouter()

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError("")

    if (password.length < 8) {
      setError("Password must be at least 8 characters")
      return
    }

    try {
      await auth.api.signUp.email({
        email,
        password,
      })
      router.push("/tasks")
    } catch (err) {
      setError("Email already exists or invalid")
    }
  }

  return (
    <div>
      <h1>Sign Up</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          required
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password (min 8 characters)"
          required
        />
        <button type="submit">Sign Up</button>
        {error && <p>{error}</p>}
      </form>
    </div>
  )
}
```

### Step 3: Database Migration

Better Auth will automatically create the users table on first run. To verify:

```bash
# Start the Next.js frontend
cd frontend
npm run dev

# Visit http://localhost:3000/api/auth/session
# This triggers Better Auth initialization

# Check database for users table
psql $DATABASE_URL -c "\dt users"
```

Expected output:
```
         List of relations
 Schema |  Name  | Type  |  Owner
--------+--------+-------+---------
 public | users  | table | neondb_owner
```

## Testing

### Test 1: User Signup

**Steps**:
1. Start backend: `cd backend && uvicorn src.main:app --reload --port 8001`
2. Start frontend: `cd frontend && npm run dev`
3. Visit http://localhost:3000/signup
4. Enter email: `test@example.com`
5. Enter password: `password123`
6. Click "Sign Up"

**Expected Result**:
- ✅ User created in database
- ✅ JWT token issued
- ✅ Redirected to /tasks
- ✅ Can see tasks page

**Verify in database**:
```sql
SELECT id, email, created_at FROM users WHERE email = 'test@example.com';
```

### Test 2: User Signin

**Steps**:
1. Visit http://localhost:3000/signin
2. Enter email: `test@example.com`
3. Enter password: `password123`
4. Click "Sign In"

**Expected Result**:
- ✅ JWT token issued
- ✅ Redirected to /tasks
- ✅ Can access protected pages

### Test 3: Protected API Access

**Test with valid token**:

```bash
# 1. Sign in and get token from browser DevTools
# Application > Cookies > better-auth.session

# 2. Test API with token
curl -X GET "http://localhost:8001/api/v1/tasks" \
  -H "Authorization: Bearer <token>"
```

**Expected Result**: 200 OK with tasks list

**Test without token**:

```bash
curl -X GET "http://localhost:8001/api/v1/tasks"
```

**Expected Result**: 401 Unauthorized

### Test 4: User Data Isolation

**Steps**:
1. Create User A: `user-a@example.com`
2. Sign in as User A
3. Create task: "User A's task"
4. Sign out
5. Create User B: `user-b@example.com`
6. Sign in as User B
7. Try to view tasks

**Expected Result**:
- ✅ User B sees empty task list
- ✅ User B cannot see User A's task
- ✅ Each user has isolated data

**Verify with API**:

```bash
# Get User A's token and create task
curl -X POST "http://localhost:8001/api/v1/tasks" \
  -H "Authorization: Bearer <user-a-token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "User A task"}'

# Try to access with User B's token
curl -X GET "http://localhost:8001/api/v1/tasks" \
  -H "Authorization: Bearer <user-b-token>"
```

**Expected**: User B sees empty array `[]`

### Test 5: Token Expiration

**Steps**:
1. Sign in and get token
2. Wait 24 hours (or modify JWT expiration to 1 minute for testing)
3. Try to access protected endpoint

**Expected Result**:
- ✅ 401 Unauthorized with "Token expired" message
- ✅ Frontend redirects to signin page

**Quick test** (modify expiration temporarily):

```python
# In jwt.py, change expiration for testing
payload = {
    "userId": user_id,
    "exp": datetime.utcnow() + timedelta(minutes=1)  # 1 minute
}
```

### Test 6: Invalid Token

**Test with tampered token**:

```bash
# Modify a character in the token
curl -X GET "http://localhost:8001/api/v1/tasks" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.TAMPERED.signature"
```

**Expected Result**: 401 Unauthorized with "Invalid token"

**Test with wrong secret**:

```python
# Temporarily change BETTER_AUTH_SECRET in backend
# Try to access with token issued by frontend
```

**Expected Result**: 401 Unauthorized with "Token signature verification failed"

## Troubleshooting

### Issue: "Invalid token" on all requests

**Cause**: BETTER_AUTH_SECRET mismatch between frontend and backend

**Solution**:
1. Verify both .env files have identical BETTER_AUTH_SECRET
2. Restart both frontend and backend
3. Sign in again to get new token

### Issue: "Module not found: python-jose"

**Cause**: Dependencies not installed

**Solution**:
```bash
cd backend
source venv/bin/activate
pip install python-jose[cryptography]
```

### Issue: "Database connection failed"

**Cause**: DATABASE_URL not configured in frontend

**Solution**:
1. Add DATABASE_URL to frontend/.env.local
2. Use same URL as backend
3. Restart frontend

### Issue: Users table not created

**Cause**: Better Auth not initialized

**Solution**:
1. Visit http://localhost:3000/api/auth/session
2. Check database: `psql $DATABASE_URL -c "\dt users"`
3. If still missing, check DATABASE_URL in frontend .env

### Issue: CORS errors in browser

**Cause**: CORS not configured correctly

**Solution**:
1. Verify FRONTEND_URL in backend .env
2. Check CORS middleware in main.py
3. Ensure allow_credentials=True

## Security Checklist

Before deploying to production:

- [ ] BETTER_AUTH_SECRET is strong (32+ random characters)
- [ ] BETTER_AUTH_SECRET is stored securely (not in git)
- [ ] HTTPS enabled for all requests
- [ ] CORS configured with specific origin (not "*")
- [ ] httpOnly cookies enabled (Better Auth default)
- [ ] Password minimum length enforced (8+ characters)
- [ ] Database connection uses SSL (Neon default)
- [ ] Environment variables not exposed to client
- [ ] Token expiration set appropriately (24 hours)
- [ ] Error messages don't leak sensitive information

## Performance Benchmarks

Expected performance after implementation:

- JWT verification: <5ms per request
- Signup flow: <500ms total
- Signin flow: <300ms total
- Protected API request: <50ms overhead
- Database query with user filter: <100ms

**Benchmark command**:

```bash
# Test JWT verification performance
ab -n 1000 -c 10 -H "Authorization: Bearer <token>" \
  http://localhost:8001/api/v1/tasks
```

## Next Steps

After completing authentication:

1. ✅ All task endpoints protected
2. ✅ User data isolation enforced
3. ✅ Temporary user_id parameter removed
4. ⏭️ Run `/sp.tasks` to generate task breakdown
5. ⏭️ Implement according to task plan
6. ⏭️ Deploy to production with HTTPS

## Additional Resources

- [Better Auth Documentation](https://better-auth.com)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT.io](https://jwt.io) - JWT debugger
- [python-jose Documentation](https://python-jose.readthedocs.io/)

## Support

If you encounter issues:

1. Check troubleshooting section above
2. Verify environment variables are set correctly
3. Check logs for detailed error messages
4. Ensure all dependencies are installed
5. Verify database connection works
