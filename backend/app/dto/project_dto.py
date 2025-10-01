"""
    Schema for adding a new project
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date

class AddProject(SQLModel):
    """
        DTO for creating a new project
    """
    name: str = Field(..., alias="name")
    description: Optional[str] = Field(None, alias="description")
    start_date: Optional[date] = Field(None, alias="start_date")
    end_date: Optional[date] = Field(None, alias="end_date")
    status: Optional[str] = Field("active", alias="status")  # e.g., active/inactive/completed
