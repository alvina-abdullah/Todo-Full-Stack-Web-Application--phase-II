---
id: 001
title: Update CLAUDE.md with project configuration
stage: general
date: 2026-02-08
surface: agent
model: claude-sonnet-4-5
feature: none
branch: main
user: PMLS
command: none
labels: ["project-setup", "configuration", "agents", "authentication", "tech-stack"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - CLAUDE.md
tests:
  - none
---

## Prompt

Update the claude.md file based on my project requirements. In this file:

Use Auth Agent for authentication
Use Frontend Agent for frontend development (e.g., Next.js)
Use DB Agent for database design and operations
Use Backend Agent for FastAPI development

Below are my project requirements:

Basic Level Functionality
Objective: Using Claude Code and Spec-Kit Plus transform the console app into a modern multi-user web application with persistent storage.
💡Development Approach: Use the Agentic Dev Stack workflow: Write spec → Generate plan → Break into tasks → Implement via Claude Code. No manual coding allowed. We will review the process, prompts, and iterations to judge each phase and project.

Requirements
- Implement all 5 Basic Level features as a web application
- Create RESTful API endpoints
- Build responsive frontend interface
- Store data in Neon Serverless PostgreSQL database
- Authentication – Implement user signup/signin using Better Auth

Technology Stack
- Frontend: Next.js 16+ (App Router)
- Backend: Python FastAPI
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Spec-Driven: Claude Code + Spec-Kit Plus
- Authentication: Better Auth

Better Auth can be configured to issue JWT (JSON Web Token) tokens when users log in. These tokens are self-contained credentials that include user information and can be verified by any service that knows the secret key.

How It Works:
1. User logs in on Frontend → Better Auth creates a session and issues a JWT token
2. Frontend makes API call → Includes the JWT token in the Authorization: Bearer <token> header
3. Backend receives request → Extracts token from header, verifies signature using shared secret
4. Backend identifies user → Decodes token to get user ID, email, etc. and matches it with the user ID in the URL
5. Backend filters data → Returns only tasks belonging to that user

## Response snapshot

Successfully updated CLAUDE.md with comprehensive project-specific configuration including:

1. **Agent Usage Strategy** - Detailed guidelines for when and how to use each agent:
   - Auth Agent (auth-agent) for authentication/authorization
   - Frontend Agent (frontend-builder) for Next.js UI development
   - Database Agent (database-skill) for schema and SQLModel
   - Backend Agent (fastapi-backend-developer) for API endpoints

2. **Technology Stack** - Complete stack table with purposes

3. **Authentication Architecture** - Detailed JWT flow with:
   - Visual flow diagram
   - Step-by-step authentication process
   - Security considerations

4. **Development Workflow** - 5-phase process:
   - Phase 1: Specification (/sp.specify)
   - Phase 2: Planning (/sp.plan)
   - Phase 3: Task Generation (/sp.tasks)
   - Phase 4: Implementation (/sp.implement)
   - Phase 5: Git Workflow (/sp.git.commit_pr)

5. **Agent Selection Guide** - Decision tree for choosing appropriate agents

6. **Multi-Agent Scenarios** - Examples of features requiring multiple agents in sequence

7. **Project Structure** - Complete directory layout for frontend, backend, specs, and history

8. **Environment Variables** - Configuration templates for both frontend and backend

9. **Success Criteria** - Phase completion checklists for tracking progress

10. **Best Practices** - Security, code quality, architecture, and testing guidelines

## Outcome

- ✅ Impact: Established comprehensive project configuration and agent usage guidelines for the Todo Full Stack Web Application Phase II project
- 🧪 Tests: None (documentation update)
- 📁 Files: Updated CLAUDE.md with ~500 lines of project-specific configuration
- 🔁 Next prompts: Initialize constitution (/sp.constitution) or create feature specification (/sp.specify) for the 5 basic features
- 🧠 Reflection: Successfully integrated project requirements with Spec-Kit Plus SDD framework. The agent usage strategy provides clear guidance on when to use each specialized agent, and the authentication architecture section clearly explains the Better Auth + JWT flow between Next.js frontend and FastAPI backend.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (documentation)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed with /sp.constitution to establish project principles, or /sp.specify to define the 5 basic features
