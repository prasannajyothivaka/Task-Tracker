import os

import msal
from cachetools import TTLCache
from dotenv import load_dotenv
from fastapi import Request, APIRouter
from starlette.responses import RedirectResponse
from app.decorators.logger_decorator import logger_wraps
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

SCOPE = ["User.Read"]

load_dotenv()

session_cache = TTLCache(maxsize=100, ttl=600)

@logger_wraps()
def authenticate_user(token):
    if session_cache['access_token'] == token:
        return session_cache.get('id_token_claims')
    return False

@logger_wraps()
def _save_cache(cache):
    if cache.has_state_changed:
        session_cache["token_cache"] = cache.serialize()


def _get_token_from_cache(scope=None):
    cache = _load_cache()  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result

@logger_wraps()
def _load_cache():
    cache = msal.SerializableTokenCache()
    if session_cache.get("token_cache"):
        cache.deserialize(session_cache.get("token_cache"))
    return cache

@logger_wraps()
def _build_auth_code_flow(authority=None, scopes=None):
    return _build_msal_app().initiate_auth_code_flow(
        scopes or [],
        redirect_uri=os.getenv('SSO_REDIRECT_BACKEND_PATH'))

@logger_wraps()
def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        os.getenv('CLIENT_ID'), authority=authority or os.getenv('AUTHORITY'),
        client_credential=os.getenv('CLIENT_SECRET'), token_cache=cache)
