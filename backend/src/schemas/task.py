"""Pydantic schemas for task request/response validation."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate and trim title."""
        if v:
            v = v.strip()
            if not v:
                raise ValueError("Title cannot be empty or whitespace only")
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Trim description if provided."""
        if v:
            v = v.strip()
            if not v:
                return None
        return v


class TaskReplace(BaseModel):
    """Schema for replacing a task (PUT)."""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")
    completed: bool = Field(..., description="Task completion status")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate and trim title."""
        if v:
            v = v.strip()
            if not v:
                raise ValueError("Title cannot be empty or whitespace only")
        return v


class TaskUpdate(BaseModel):
    """Schema for partially updating a task (PATCH)."""

    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")
    completed: Optional[bool] = Field(None, description="Task completion status")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate and trim title if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Title cannot be empty or whitespace only")
        return v


class TaskResponse(BaseModel):
    """Schema for task response."""

    id: int
    title: str
    description: Optional[str]
    completed: bool
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
