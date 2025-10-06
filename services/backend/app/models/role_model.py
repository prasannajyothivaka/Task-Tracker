"""
    Table Structure for Role table
"""
from typing import Optional
import os
from sqlmodel import Field, SQLModel, Column, VARCHAR
from dotenv import load_dotenv


load_dotenv()


class Role(SQLModel, table=True):
    """
        Creating database Structure for Role table
    """
    __tablename__='roles'
    __table_args__ = {'schema': os.getenv('schema_name')}


    id: Optional[int] = Field(default=None, primary_key=True)
    role_name: str = Field(sa_column=Column("role_name", VARCHAR(54), nullable=False))
