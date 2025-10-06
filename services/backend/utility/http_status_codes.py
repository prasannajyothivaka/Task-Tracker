"""
    Enums for HTTP Status CodesS
"""
from enum import Enum

class HttpStatusCodes(): # pylint: disable=too-few-public-methods
    """
        Nested Classes for StatusCodes response and StatusCodesDesription response
    """
    def __init__(self):
        pass
    class StatusCodes(Enum):
        """
        Enums for StatusCodes
        """
        SUCCESS_OK_200: int = 200
        BAD_REQUEST_400: int = 400
        UNAUTHORIZED_401: int = 401
        FORBIDDEN_403: int = 403
        NOT_FOUND_404: int = 404
        INTERNAL_SERVER_ERROR_500: int = 500
        NOT_IMPLEMENTED_501: int = 501

    class StatusCodesDescription(Enum):
        """
        Enums for StatusCodesDescription
        """
        SUCCESS_OK_200: str = 'Ok'
        BAD_REQUEST_400: str = 'Bad Request'
        UNAUTHORIZED_401: str = 'Unauthorized'
        FORBIDDEN_403: str = 'Forbidden'
        NOT_FOUND_404: str = 'Not Found'
        INTERNAL_SERVER_ERROR_500: str = 'Internal Server Error'
        NOT_IMPLEMENTED_501: str = 'Not Implemented'
