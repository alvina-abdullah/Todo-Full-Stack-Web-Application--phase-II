# Todo App - Frontend

Next.js 16+ frontend application with Better Auth authentication and JWT token management.

## Prerequisites

- Node.js 18 or higher
- npm or yarn
- Backend API running on port 8001

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment Variables

Create a `.env.local` file in the frontend directory:

```bash
cp .env.local.example .env.local
```

Edit `.env.local` with your configuration:

```env
# Better Auth secret for JWT token signing
# IMPORTANT: Must match backend/.env BETTER_AUTH_SECRET
BETTER_AUTH_SECRET='your-secret-generated-with-openssl-rand-base64-32'

# Database connection for Better Auth (Neon PostgreSQL)
DATABASE_URL='postgresql://user:password@host.neon.tech/database?sslmode=require'

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8001
```

**Important Notes:**
- `BETTER_AUTH_SECRET` must match the backend secret exactly
- Use `postgresql://` (not `postgresql+asyncpg://`) for Better Auth
- The database URL should point to the same Neon PostgreSQL database as the backend

### 3. Start Development Server

```bash
npm run dev
```

The app will be available at: http://localhost:3000

## Authentication with Better Auth

This application uses [Better Auth](https://www.better-auth.com/) for authentication, which provides:

- Email/password authentication
- JWT token generation and management
- Secure session handling with httpOnly cookies
- Automatic token refresh

### Authentication Flow

1. **Sign Up** (`/signup`):
   - User enters email and password
   - Better Auth creates user account in database
   - JWT token issued and stored in httpOnly cookie
   - User redirected to `/tasks`

2. **Sign In** (`/signin`):
   - User enters credentials
   - Better Auth verifies credentials
   - JWT token issued and stored in httpOnly cookie
   - User redirected to `/tasks`

3. **Protected Routes** (`/tasks`, `/profile`):
   - Middleware checks for valid session
   - Unauthenticated users redirected to `/signin`
   - API requests automatically include JWT token

4. **Sign Out**:
   - Better Auth clears session and token
   - User redirected to `/signin`

### Better Auth Configuration

Better Auth is configured in `src/lib/auth.ts`:

```typescript
export const auth = betterAuth({
  database: pool,                    // PostgreSQL connection
  secret: process.env.BETTER_AUTH_SECRET,
  emailAndPassword: { enabled: true },
  basePath: "/api/auth",
  baseURL: process.env.NEXT_PUBLIC_API_URL,
})
```

### API Client

The `src/lib/api-client.ts` module provides authenticated API requests:

```typescript
import { apiGet, apiPost, apiPatch, apiDelete } from '@/lib/api-client'

// Automatically includes JWT token in Authorization header
const response = await apiGet('/api/v1/tasks')
const tasks = await response.json()
```

Features:
- Automatic JWT token extraction from Better Auth session
- Authorization header injection (`Bearer <token>`)
- 401 response handling (redirects to `/signin`)
- Error handling for authentication failures

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── signup/         # Sign up page
│   │   │   └── signin/         # Sign in page
│   │   ├── tasks/              # Tasks page (protected)
│   │   ├── api/
│   │   │   └── auth/[...all]/  # Better Auth API routes
│   │   ├── layout.tsx          # Root layout
│   │   └── page.tsx            # Home page
│   ├── lib/
│   │   ├── auth.ts             # Better Auth configuration
│   │   ├── api-client.ts       # Authenticated API client
│   │   └── auth-utils.ts       # Auth helper functions
│   └── middleware.ts           # Route protection middleware
├── .env.local                  # Environment variables (not in git)
├── .env.local.example          # Example environment variables
├── package.json                # Dependencies
└── README.md                   # This file
```

## Available Routes

### Public Routes
- `/` - Home page
- `/signup` - User registration
- `/signin` - User authentication

### Protected Routes (require authentication)
- `/tasks` - Task management (CRUD operations)

### API Routes
- `/api/auth/*` - Better Auth endpoints (handled automatically)

## Development

### Running Tests

```bash
npm test
```

### Building for Production

```bash
npm run build
npm start
```

### Environment Variables

**Development:**
- `BETTER_AUTH_SECRET` - JWT signing secret (must match backend)
- `DATABASE_URL` - PostgreSQL connection string
- `NEXT_PUBLIC_API_URL` - Backend API URL (http://localhost:8001)

**Production:**
- Use HTTPS for all URLs
- Ensure `BETTER_AUTH_SECRET` is securely generated and stored
- Configure proper CORS on backend
- Use environment-specific database URLs

## Security Considerations

1. **JWT Tokens**: Stored in httpOnly cookies (not accessible via JavaScript)
2. **HTTPS**: Always use HTTPS in production
3. **Secret Management**: Never commit `.env.local` to version control
4. **CORS**: Backend only accepts requests from configured frontend URL
5. **Token Expiration**: Tokens expire after 7 days by default

## Troubleshooting

### "Not authenticated" error
- Ensure you're signed in
- Check that JWT token is present in cookies
- Verify `BETTER_AUTH_SECRET` matches backend

### API requests fail with 401
- Token may be expired - sign in again
- Check backend is running on correct port
- Verify `NEXT_PUBLIC_API_URL` is correct

### Better Auth database errors
- Ensure database tables exist (run `backend/create_auth_tables.py`)
- Verify `DATABASE_URL` is correct
- Check database connection and permissions

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Better Auth Documentation](https://www.better-auth.com/docs)
- [Backend API Documentation](../backend/README.md)
