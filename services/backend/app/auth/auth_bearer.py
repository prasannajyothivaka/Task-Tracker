from fastapi import Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.login_service import check_user_valid
from app.utility.exceptions_utility import get_user_exception


def verify_jwt(jwtoken: str):
    isTokenValid: bool = False
    try:
        payload = check_user_valid(jwtoken)
    except Exception:
        payload = None
    if payload:
        isTokenValid = True
    return isTokenValid


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if not credentials:
            raise get_user_exception()
        if credentials.scheme != "Bearer":
            raise get_user_exception()
        if not verify_jwt(credentials.credentials):
            raise get_user_exception()
        return credentials.credentials
