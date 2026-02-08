<!--
Sync Impact Report:
- Version change: Template → 1.0.0 (Initial constitution)
- Principles defined: 5 core principles established
- Added sections: Technical Standards & Constraints, Quality & Testing Requirements
- Templates requiring updates:
  ✅ constitution.md (this file)
  ⚠ plan-template.md (pending review for alignment)
  ⚠ spec-template.md (pending review for alignment)
  ⚠ tasks-template.md (pending review for alignment)
- Follow-up TODOs: Review dependent templates for consistency with new principles
-->

# Todo Full-Stack Web Application (Phase II) Constitution

## Core Principles

### I. Accuracy

All backend operations MUST correctly handle data and enforce user ownership. Every API endpoint MUST validate that the authenticated user has permission to access or modify the requested resource. Data integrity MUST be maintained through proper validation, error handling, and transactional operations where necessary.

**Rationale**: User data isolation is critical for multi-user applications. Incorrect data handling or ownership enforcement can lead to data leaks, unauthorized access, and loss of user trust.

### II. Security

Authentication and authorization MUST prevent unauthorized access. All API endpoints (except public authentication endpoints) MUST validate JWT tokens before processing requests. Passwords MUST be hashed using industry-standard algorithms. Sensitive data MUST never be logged or exposed in error messages.

**Rationale**: Security is non-negotiable in web applications handling user data. A single security vulnerability can compromise the entire system and all user data.

**Requirements**:
- JWT tokens MUST be validated on every protected API request
- Invalid or missing tokens MUST return 401 Unauthorized
- User sessions MUST expire after a reasonable timeout
- Secrets and API keys MUST be stored in environment variables, never in code

### III. Reproducibility

The application MUST behave consistently across all environments (development, staging, production). Configuration MUST be externalized through environment variables. Database migrations MUST be versioned and reproducible. Dependencies MUST be locked to specific versions.

**Rationale**: Inconsistent behavior across environments leads to "works on my machine" problems, difficult debugging, and production incidents.

**Requirements**:
- Environment-specific configuration via `.env` files
- Database schema changes via migration scripts only
- Dependency versions locked in `package.json` / `requirements.txt`
- No hardcoded environment-specific values in code

### IV. Clarity

Code, API responses, and UI behavior MUST be clear and maintainable. Code MUST follow established conventions for the technology stack. API responses MUST use appropriate HTTP status codes and include meaningful error messages. UI components MUST have clear, descriptive names and single responsibilities.

**Rationale**: Maintainability is essential for long-term project success. Clear code reduces bugs, speeds up development, and makes onboarding easier.

**Requirements**:
- Follow Python PEP 8 style guide for FastAPI backend
- Follow TypeScript/React best practices for Next.js frontend
- Use meaningful variable and function names
- Keep functions small and focused (single responsibility)
- Document complex business logic with comments

### V. Responsiveness

Frontend MUST provide a smooth and responsive user experience. UI MUST respond to user actions immediately with loading states where appropriate. The application MUST be usable on mobile, tablet, and desktop devices. API calls MUST not block the UI.

**Rationale**: User experience directly impacts adoption and satisfaction. Slow or unresponsive interfaces frustrate users and reduce productivity.

**Requirements**:
- Implement loading states for async operations
- Use responsive design patterns (mobile-first approach)
- Optimize API response times (target < 500ms for CRUD operations)
- Handle errors gracefully with user-friendly messages

## Technical Standards & Constraints

### Technology Stack (NON-NEGOTIABLE)

The following technology stack MUST be used for all implementation:

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | Next.js (App Router) | 16+ |
| Backend | Python FastAPI | Latest stable |
| ORM | SQLModel | Latest stable |
| Database | Neon Serverless PostgreSQL | Latest |
| Authentication | Better Auth | Latest stable |

**Rationale**: This stack was chosen for Phase II to provide a modern, performant, and scalable foundation. Deviations require architectural review and approval.

### API Standards

All API endpoints MUST follow RESTful conventions:

- **GET**: Retrieve resources (idempotent, no side effects)
- **POST**: Create new resources
- **PUT**: Replace entire resource
- **PATCH**: Partial update of resource
- **DELETE**: Remove resource

HTTP status codes MUST be used correctly:
- **200 OK**: Successful GET, PUT, PATCH
- **201 Created**: Successful POST
- **204 No Content**: Successful DELETE
- **400 Bad Request**: Invalid input data
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Authenticated but not authorized
- **404 Not Found**: Resource does not exist
- **500 Internal Server Error**: Unexpected server error

### Authentication Flow

1. User submits credentials to Better Auth endpoint (Next.js API route)
2. Better Auth validates credentials and issues JWT token
3. Frontend stores token securely and includes it in all API requests via `Authorization: Bearer <token>` header
4. FastAPI backend validates JWT signature and extracts user information
5. Backend enforces user ownership by filtering queries based on authenticated user ID

### Database Operations

- All database models MUST be defined using SQLModel
- Migrations MUST be created for all schema changes
- Queries MUST use parameterized statements (SQLModel handles this automatically)
- Transactions MUST be used for operations that modify multiple records
- Database connection pooling MUST be configured for production

### Code Organization

**Backend (FastAPI):**
```
backend/
├── api/          # API route handlers
├── models/       # SQLModel definitions
├── auth/         # JWT validation middleware
├── database/     # Database connection and configuration
└── main.py       # Application entry point
```

**Frontend (Next.js):**
```
frontend/
├── app/          # App Router pages and layouts
├── components/   # Reusable UI components
└── lib/          # Utilities and API client
```

## Quality & Testing Requirements

### Feature Completeness

All 5 basic-level features MUST be implemented:
1. User authentication (signup/signin with Better Auth)
2. Create todos
3. Read/view todos (user's own only)
4. Update todos (edit text, toggle completion)
5. Delete todos

### Testing Requirements

- **Unit Tests**: Critical business logic functions MUST have unit tests
- **Integration Tests**: API endpoints MUST have integration tests verifying:
  - Correct responses for valid requests
  - Proper error handling for invalid requests
  - Authentication enforcement (401 for missing/invalid tokens)
  - User isolation (users cannot access other users' data)
- **End-to-End Tests**: Critical user flows MUST be tested:
  - User signup and signin
  - Create, view, update, delete todo
  - Multiple users with isolated data

### Success Criteria (Definition of Done)

A feature is considered complete when:
- ✅ All CRUD operations work correctly with persistent storage
- ✅ Authentication correctly issues JWT tokens and validates them for each user
- ✅ API requests without valid token receive 401 Unauthorized
- ✅ Frontend displays tasks correctly and allows all CRUD operations
- ✅ Task ownership enforced: users see only their own tasks
- ✅ Application passes end-to-end testing with multiple users and devices
- ✅ Code follows all principles and standards defined in this constitution
- ✅ No security vulnerabilities identified in code review

### Deployment Readiness

Before deployment, the application MUST:
- Have all environment variables documented
- Include database migration scripts
- Have health check endpoints configured
- Include error logging and monitoring setup
- Be tested on target deployment platform

## Governance

### Amendment Process

This constitution supersedes all other development practices and guidelines. Amendments to this constitution require:

1. **Proposal**: Document the proposed change with rationale
2. **Impact Analysis**: Identify affected code, templates, and workflows
3. **Review**: Technical review by project stakeholders
4. **Approval**: Explicit approval before implementation
5. **Migration**: Update all dependent artifacts and documentation
6. **Version Bump**: Increment version according to semantic versioning

### Version Semantics

- **MAJOR** (X.0.0): Backward-incompatible changes to core principles or governance
- **MINOR** (x.Y.0): New principles added or existing principles materially expanded
- **PATCH** (x.y.Z): Clarifications, wording improvements, non-semantic refinements

### Compliance

- All code reviews MUST verify compliance with this constitution
- All specifications MUST align with principles and constraints defined here
- All implementation plans MUST reference relevant constitutional principles
- Deviations from this constitution MUST be explicitly justified and documented

### Enforcement

- Pull requests that violate constitutional principles MUST be rejected
- Security violations are blocking and MUST be fixed immediately
- Code that does not meet clarity standards SHOULD be refactored before merge
- Performance issues that impact responsiveness SHOULD be addressed promptly

### Living Document

This constitution is a living document. As the project evolves, principles may be refined, added, or (rarely) removed. All changes MUST follow the amendment process and maintain backward compatibility where possible.

**Version**: 1.0.0 | **Ratified**: 2026-02-08 | **Last Amended**: 2026-02-08
