"""
    Common Schema for mapping response
"""
from sqlmodel import SQLModel, Field

class Response(SQLModel):
    """
        function for constructing schema
    """
    message: str = Field(None, alias="message")
    status: str = Field(None, alias="status")
    data: str = Field(None, alias="data")
