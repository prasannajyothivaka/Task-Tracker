"""
    business logic related to login
"""
import os
import logging
import random
import string
import hashlib
import time
from typing import Optional
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select
from google.oauth2 import id_token
import requests 
from google.auth.transport import requests as google_requests
from dotenv import load_dotenv
from app.models.auth_user_model import User
from app.models.user_role_model import UserRole
from app.repositories.auth_user_repository import get_active_user_by_username
from app.utility.exceptions_utility import get_user_exception


SECRET = "ipxktnykorrirtjduyy"
ALGORITHM = "RS256"
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")


# Cache JWKS keys and expiry
JWKS_URL = os.getenv('JWKS_URL')
_jwks_cache = None
_jwks_last_fetch = 0
JWKS_TTL = os.getenv('JWKS_TTL')

load_dotenv()
logger = logging.getLogger(__name__)

def get_password_hash(password: str) -> str:
    try:
        sha256_hex = hashlib.sha256(password.encode("utf-8")).hexdigest()
        truncated = sha256_hex[:72]
        return bcrypt_context.hash(truncated)
    except Exception as e:
        # Log the error if you want
        print(f"⚠️ Password hashing failed: {e}")
        # Fallback: return the password as-is
        return password

def verify_password(password: str, hashed: str) -> bool:
    try:
        sha256_hex = hashlib.sha256(password.encode("utf-8")).hexdigest()
        truncated = sha256_hex[:72]
        return bcrypt_context.verify(truncated, hashed)
    except Exception as e:
        print(f"⚠️ Password verification failed: {e}")
        # Fallback: check raw password equality
        return password == hashed


def get_user_id(email,session):
    """get user id by email"""
    statement = select(User.id).where(User.email == email)
    return session.execute(statement).first()


def get_email_async(email: str, db_session):
    """
    gets details about email available or not
    """
    statement = select(User.email).where(User.email == email)
    results = db_session.execute(statement).first()
    is_exists = False
    if results != None:
        is_exists = True
    return is_exists


def get_jwks():
    """Fetch and cache Google's JWKS keys (certs)."""
    global _jwks_cache, _jwks_last_fetch
    now = time.time()
    if not _jwks_cache or (now - _jwks_last_fetch) > JWKS_TTL:
        resp = requests.get(JWKS_URL, timeout=2)  # quick fetch
        resp.raise_for_status()
        _jwks_cache = resp.json()
        _jwks_last_fetch = now
    return _jwks_cache


def get_user_data(token: str):
    """
    Validate Google ID token quickly using cached JWKS.
    """
    try:
        # 1. Extract token headers (which key was used)
        headers = jwt.get_unverified_header(token)
        jwks = get_jwks()

        key = next((jwk for jwk in jwks["keys"] if jwk["kid"] == headers["kid"]), None)
        if not key:
            raise HTTPException(status_code=401, detail="Invalid key ID")

        # 2. Decode & verify token locally
        idinfo = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=os.getenv("GOOGLE_CLIENT_ID"),
            issuer="https://accounts.google.com"
        )

        # 3. Build response
        return {
            "sub": idinfo.get("sub"),
            "email": idinfo.get("email"),
            "first_name": idinfo.get("given_name", ""),
            "last_name": idinfo.get("family_name", ""),
            "username": idinfo.get("name", ""),
        }

    except Exception as e:
        print("Google token validation failed:", e)
        raise HTTPException(status_code=401, detail="Invalid token")


def authenticated_user(username: str, password: str, session):
    """
    return authenticated user 
    """
    if user := get_active_user_by_username(username, session):
        return user if verify_password(password, user.password) else False
    else:
        return False

def get_user(username: str, session):
    """
    get_user
    """
    user = get_active_user_by_username(username['preferred_username'], session)
    if user and user.is_active:
        return {"status": True, "user": user}
    elif not user:
        user = token_create_user(username, session)
        return {"status": True, "user": user}
    return {"status": False, "user": False}

def create_access_token(user_id: int, email: str = None, roles: list = None, expires_delta: timedelta = None):
    """
    Create an access token (short-lived JWT for authentication).
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)  # default 1 hour expiry

    to_encode = {
        "user_id": user_id,
        "exp": expire,
        "type": "access",
    }

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET,
        algorithm=ALGORITHM
    )
    return encoded_jwt

def create_refresh_token(user_id: int, expires_delta: timedelta = None):
    """
    Create a refresh token with longer expiration.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=1)
    
    to_encode = {
        "user_id": user_id,
        "exp": expire,
        "type": "refresh"  # Mark as refresh token
    }
    
    encoded_jwt = jwt.encode(
        to_encode, 
        SECRET, 
        algorithm=ALGORITHM
    )
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_bearer)):
    """
        get the current user
    """
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise get_user_exception()
        return {"username": username, "user_id": user_id}
    except JWTError as e:
        raise get_user_exception() from e


def check_user_valid(token: str):
    """
        check user is valid or not
    """
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        # print(payload, 'check payload')
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            return False
        return True
    except JWTError as e:
        raise get_user_exception() from e


def token_create_user(data_obj, session):
    """
    create user if user not exists
    """
    logger.info("random_password generated for user %s: %s", data_obj['email'], random_password)
    new_user = User(
        username=data_obj['username'],
        email=data_obj['email'],
        first_name=data_obj['first_name'],
        last_name=data_obj['last_name'],
        password=get_password_hash(os.getenv("SSO_DEFAULT_PASSWORD")),
        is_active=True,
        is_sso_user=1
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    new_user_role = UserRole(role_id=3, user_id=new_user.id)
    session.add(new_user_role)
    session.commit()
    new_user = {
        "id": new_user.id,
        "sub": str(new_user.id),
        "email": new_user.email,
        "username": new_user.username,
        "first_name": new_user.first_name,
        "last_name": new_user.last_name
    }
    return new_user


def get_random_password(length):
    """generate random password"""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))
