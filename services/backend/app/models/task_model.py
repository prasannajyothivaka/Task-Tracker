from typing import Optional
from datetime import datetime, date
from sqlmodel import SQLModel, Field, Column, VARCHAR
import os
from dotenv import load_dotenv

load_dotenv()

def get_current_time():
    return datetime.now()

class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    __table_args__ = {"schema": os.getenv("schema_name")}

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(sa_column=Column("title", VARCHAR(150), nullable=False))
    description: Optional[str] = Field(sa_column=Column("description", VARCHAR(500), nullable=True))
    project_id: int = Field(foreign_key=os.getenv("schema_name")+".projects.id")
    assigned_to: Optional[int] = Field(foreign_key=os.getenv("schema_name")+".auth_user.id")
    start_date: date = Field(default_factory=date.today)
    due_date: Optional[date] = Field(default=None)
    status: str = Field(default="pending")
    priority: str = Field(default="medium")
    created_on: datetime = Field(default=get_current_time())
    created_by: Optional[int] = Field(foreign_key=os.getenv("schema_name")+".auth_user.id")
    updated_on: datetime = Field(default=get_current_time())
    updated_by: Optional[int] = Field(foreign_key=os.getenv("schema_name")+".auth_user.id")
    is_active: bool = Field(default=True)
