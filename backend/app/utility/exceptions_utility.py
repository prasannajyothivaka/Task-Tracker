"""Exception Utility"""
from fastapi import HTTPException, status


def raise_item_can_not_be_found_exception():
    """Item Can not be found exception"""

    return HTTPException(
        status_code=404,
        detail='Item not found',
    )


def get_user_exception():
    """User exception"""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return credentials_exception


def token_exception():
    """Token exception"""

    token_mismatch_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return token_mismatch_exception


def password_exception():
    """password exception"""
    get_password_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return get_password_exception


def unauthorised_exception():
    """password exception"""
    unauthorized_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Access Denied",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return unauthorized_exception
