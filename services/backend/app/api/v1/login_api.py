from fastapi import Depends, APIRouter, status, Form, HTTPException
from jose import jwt

from app.api.v1.auth import authenticate_user
from app.database import get_session
from sqlmodel import Session
from app.services.login_service import (authenticated_user,get_user_data,get_user_id,
    get_email_async, create_access_token, token_create_user, get_user)
from datetime import timedelta
from app.repositories.user_role_repository import get_role
from app.dto.user_dto import SSOLoginRequest
from app.utility.exceptions_utility import token_exception

router = APIRouter()


class LoginPasswordRequestForm:
    def __init__(
        self,
        username: str = Form(...),
        password: str = Form(...),
        token: str = Form(default=None),
    ):
        self.username = username
        self.password = password
        self.token = token



@router.post("/login")
async def user_login(form_data: LoginPasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    if form_data.token:
        msal_token = authenticate_user(form_data.token)
        user = get_user(msal_token, session)
        user = user['user']
        
    else:
        
        user = authenticated_user(form_data.username, form_data.password, session)
    if not user:
        raise token_exception()
    token_expires = timedelta(minutes=120)
    token = create_access_token(username=user.username, user_id=user.id, expires_delta=token_expires)
    return {
        "status_code": status.HTTP_200_OK,
        "data": {
            "username": user.username,
            "token": token,
            "user_id": user.id,
            "role_id" : get_role(user.id),
            "first_name":user.first_name,
            "last_name":user.last_name
        },
    }

@router.post("/sso-login")
async def sso_login(payload: SSOLoginRequest, session: Session = Depends(get_session)):
    """
    Login endpoint for SSO.
    Accepts JSON with only a token field.
    """
    token = payload.token

    if not token:
        raise HTTPException(status_code=400, detail="Token is required")


    # Step 1: Validate the SSO token
    user =get_user_data(token)

    db_user = get_email_async(user['email'], session)


    if not db_user:

        user = token_create_user(user, session)  # <-- returns User model


    user_id=get_user_id(user['email'],session)


    # Step 3: Create backend JWT
    token_expires = timedelta(minutes=120)
    access_token = create_access_token(
        username=user['username'],
        user_id=user_id[0],
        expires_delta=token_expires
    )
    return {
        "status_code": status.HTTP_200_OK,
        "data": {
            "username": user['username'],
            "token": access_token,
            "user_id": user_id[0],
            "role_id": get_role(user_id[0]),
            "first_name": user['first_name'],
            "last_name": user['last_name'],
            "email": user['email'],
        },
    }
