from typing import Optional
from datetime import datetime, date
import os
from sqlmodel import Field, SQLModel, Column, VARCHAR

from dotenv import load_dotenv

load_dotenv()

def get_current_time():
    return datetime.now()

class Project(SQLModel, table=True):
    """
        Creating database structure for Project table
    """
    __tablename__ = "projects"
    __table_args__ = {"schema": os.getenv("schema_name")}

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column("name", VARCHAR(150), nullable=False, unique=True))
    description: Optional[str] = Field(sa_column=Column("description", VARCHAR(500), nullable=True))
    start_date: Optional[date] = Field(default=date.today)
    end_date: Optional[date] = Field(default=date.today)
    status: str = Field(default="active")  # active / inactive / completed
    owner_id: Optional[int] = Field(
        default=None, foreign_key=os.getenv('schema_name')+'.'+"auth_user.id"
    )
    created_on: datetime = Field(default=get_current_time())
    created_by: Optional[int] = Field(
        default=None, foreign_key=os.getenv('schema_name')+'.'+"auth_user.id")
    updated_on: datetime = Field(default=get_current_time())
    updated_by: Optional[int] = Field(
        default=None, foreign_key=os.getenv('schema_name')+'.'+"auth_user.id")
    is_active: bool = Field(default=True)
