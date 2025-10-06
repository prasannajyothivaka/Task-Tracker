"""
    Table Structure for User table
"""
from typing import Optional
from datetime import datetime
import os
from sqlmodel import Field, SQLModel, Column, VARCHAR,INT, SmallInteger

from dotenv import load_dotenv

load_dotenv()

def get_current_time():
    """
    get_current_time
    """
    return datetime.now()

class User(SQLModel, table=True):
    """
        Creating database Structure for User table
    """
    __tablename__ = 'auth_user'
    __table_args__ = {'schema': os.getenv('schema_name')}

    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str = Field(sa_column=Column("first_name", VARCHAR(54), nullable=False))
    last_name: str = Field(sa_column=Column("last_name", VARCHAR(54), nullable=True))
    email: str = Field(sa_column=Column("email", VARCHAR(150), unique=True, nullable=False))
    password: str = Field(sa_column=Column("password", VARCHAR(256), nullable=True))
    last_login: datetime = Field(default=get_current_time())
    is_superuser: int = Field(sa_column=Column("is_superuser", INT, default=0))
    username: str = Field(sa_column=Column("username", VARCHAR(150), unique=True, nullable=False))
    is_staff: bool = Field(default=True)
    is_active: bool = Field(default=True)
    date_joined: datetime = Field(default=get_current_time())
    profile_pic: str = Field(sa_column=Column("profile_pic", VARCHAR(256), nullable=True))
    date_deleted: str = Field(default=None)
    is_sso_user: int = Field(sa_column=Column("is_sso_user", SmallInteger, default=0), description="1 = SSO User, 0 = Regular User")
