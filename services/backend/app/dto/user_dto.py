"""
    Schema for adding a new user
"""
from sqlmodel import SQLModel, Field

class AddUser(SQLModel):
    """
        function to map new user to country and tool schema
    """
    email: str = Field(None, alias="email")
    first_name: str = Field(None, alias="first_name")
    last_name: str = Field(None, alias="last_name")
    password: str = Field(None, alias="password")
    role_id: int = Field(default=3, alias="role_id")


class SSOLoginRequest(SQLModel):
    token: str
