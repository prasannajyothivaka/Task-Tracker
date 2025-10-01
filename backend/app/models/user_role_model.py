"""
    Table Structure for UserRole table
"""
from typing import Optional
import os
from sqlmodel import Field, SQLModel
from dotenv import load_dotenv

load_dotenv()


#Relationship between User, Role
class UserRole(SQLModel, table=True):
    """
        Creating database Structure for UserRole table
    """
    __tablename__ = 'user_role'
    __table_args__ = {'schema': os.getenv('schema_name')}


    id: Optional[int] = Field(default=None, primary_key=True)
    role_id: Optional[int] = Field(
        default=None, foreign_key=os.getenv('schema_name')+'.'+"roles.id")
    user_id: Optional[int] = Field(
        default=None, foreign_key=os.getenv('schema_name')+'.'+"auth_user.id")
