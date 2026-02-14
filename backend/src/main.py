"""FastAPI application entry point."""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database.connection import init_db, close_db
from .api.exception_handlers import (
    task_not_found_handler,
    task_access_denied_handler,
    validation_error_handler,
)
from .api.exceptions import TaskNotFoundError, TaskAccessDeniedError, ValidationError


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


# Create FastAPI application
app = FastAPI(
    title="Task Management API",
    description="RESTful API for managing tasks with user ownership and data isolation",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
# Get frontend URL from environment variable
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],  # Only allow requests from the frontend
    allow_credentials=True,  # Required for cookies and Authorization headers
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers including Authorization
)

# Register exception handlers
app.add_exception_handler(TaskNotFoundError, task_not_found_handler)
app.add_exception_handler(TaskAccessDeniedError, task_access_denied_handler)
app.add_exception_handler(ValidationError, validation_error_handler)

# Import and register routers
from .api.tasks import router as tasks_router
app.include_router(tasks_router, prefix="/api/v1", tags=["tasks"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Task Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
