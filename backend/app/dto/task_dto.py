"""
    Schemas for Task operations
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date


class AddTask(SQLModel):
    """
    DTO for creating a new task
    """
    title: str = Field(..., alias="title")
    description: Optional[str] = Field(None, alias="description")
    project_id: int = Field(..., alias="project_id")   # FK to Project table

    assigned_to: Optional[int] = Field(None, alias="assigned_to")  

    start_date: date = Field(default_factory=date.today, alias="start_date")
    due_date: Optional[date] = Field(None, alias="due_date")

    status: str = Field(default="pending", alias="status", description="pending / in_progress / completed")
    priority: str = Field(default="medium", alias="priority", description="low / medium / high")


class UpdateTaskStatus(SQLModel):
    """
    DTO for updating task status (for assigned user)
    """
    status: str = Field(..., alias="status", description="pending / in_progress / completed")
