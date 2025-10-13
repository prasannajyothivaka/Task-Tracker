from fastapi import Depends, APIRouter, status, Form, HTTPException, Body
from jose import jwt
import os

from app.api.v1.auth import authenticate_user
from app.database import get_session
from sqlmodel import Session
from app.services.login_service import (get_user_data,get_user_id,
    get_email_async, create_access_token, token_create_user, get_user, create_refresh_token)
from datetime import timedelta
from app.repositories.user_role_repository import get_role
from app.dto.user_dto import SSOLoginRequest
from app.utility.exceptions_utility import token_exception

router = APIRouter()

@router.post("/refresh-token")
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
    session: Session = Depends(get_session)
):
    """
    Exchange refresh token for new access token.
    """
    try:
        # Decode refresh token
        payload = jwt.decode(
            refresh_token,
            os.getenv("SECRET_KEY"),
            algorithms=["HS256"]
        )
        
        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user info
        from app.models.auth_user_model import User
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        # ✅ Generate NEW access token
        new_access_token = create_access_token(
            user_id=user.id,
            email=user.email,
            expires_delta=timedelta(minutes=30)
        )
        
        return {
            "status_code": 200,
            "data": {
                "token": new_access_token
            }
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.post("/sso-login")
async def sso_login(payload: SSOLoginRequest, session: Session = Depends(get_session)):
    token = payload.token
    if not token:
        raise HTTPException(status_code=400, detail="Token is required")

    # Validate SSO token
    user = get_user_data(token)
    db_user = get_email_async(user['email'], session)

    if not db_user:
        user = token_create_user(user, session)

    user_id = get_user_id(user['email'], session)

    # Create BOTH access and refresh tokens
    access_token_expires = timedelta(minutes=30)  # Short-lived
    refresh_token_expires = timedelta(hours=3)     # Long-lived

    access_token = create_access_token(
        user_id=user_id[0],
        email=user['email'],
        expires_delta=access_token_expires
    )
    
    #Create refresh token
    refresh_token = create_refresh_token(
        user_id=user_id[0],
        expires_delta=refresh_token_expires
    )

    return {
        "status_code": status.HTTP_200_OK,
        "data": {
            "username": user['username'],
            "token": access_token,           # ✅ Access token
            "refresh_token": refresh_token,   # ✅ NEW: Refresh token
            "user_id": user_id[0],
            "role_id": get_role(user_id[0]),
            "first_name": user['first_name'],
            "last_name": user['last_name'],
            "email": user['email'],
        },
    }