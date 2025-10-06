from typing import Optional
from pydantic import BaseModel, EmailStr


from pydantic import BaseModel, EmailStr
from typing import Optional

class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]

class UserProfileUpdate(BaseModel):
    user_id: int
    name: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]
