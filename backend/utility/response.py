"""
    common json response structure
"""
from dto import response_dto

def create_response(message:str,status:str,data:str=None):
    """
        function for mapping the response
    """
    final_response = response_dto.Response()
    final_response.message = message
    final_response.status = status
    final_response.data = data
    return final_response
