"""
    Endpoints related to data about user
"""
from app.dto.user_profile_dto import UserProfileUpdate,UserProfileResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.utility import response as res
from app.models.auth_user_model import User
from app.utility.http_status_codes import HttpStatusCodes
from app.services import auth_user_service
from app.dto.user_dto import AddUser
from app.services.login_service import get_password_hash
from app.auth.auth_bearer import JWTBearer
from app.services.login_service import get_current_user
from app.repositories.auth_user_repository import get_user_details_by_id, add_user_role
import logging
import time

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users",)

"""
    HTTP methods for users
"""

@router.get("/get_all_users/{role_id}", dependencies=[Depends(JWTBearer())],
            summary='Get All users',
            description="returns details about all the users")
async def get_users(role_id: int,
                    db_session: Session = Depends(get_session),
                    current_user: dict = Depends(get_current_user)):
    """
        Gets all users
    """
    start = time.time()
    logged_user_id = current_user['user_id']
    result = auth_user_service.get_all_users(logged_user_id, role_id, db_session)
    if len(result) > 0:
        response = res.create_response(HttpStatusCodes.StatusCodesDescription.SUCCESS_OK_200,
                                       HttpStatusCodes.StatusCodes.SUCCESS_OK_200,
                                       result)
        logger.info("{} ran in {}s".format("get_users" + str(role_id) + "_func", round(time.time() - start, 2)))
        return response

    response = res.create_response(HttpStatusCodes.StatusCodesDescription.NO_CONTENT_204,
                                   HttpStatusCodes.StatusCodes.NO_CONTENT_204,
                                   result)
    logger.info("{} ran in {}s".format("get_users" + str(role_id) + "_func", round(time.time() - start, 2)))
    return response


@router.get("/get_user_email/{email}", dependencies=[Depends(JWTBearer())],
            summary='Get user email',
            description="returns whether email exists or not")
async def get_email(email: str, db_session: Session = Depends(get_session),
                    current_user: dict = Depends(get_current_user)):
    """
        Gets all email
    """
    logged_user_id = current_user['user_id']
    logger.info(f'email {email}')
    result = auth_user_service.get_email(logged_user_id, email, db_session)
    logger.info(f'response {result}')
    return res.create_response(
        HttpStatusCodes.StatusCodesDescription.SUCCESS_OK_200,
        HttpStatusCodes.StatusCodes.SUCCESS_OK_200,
        result)


@router.delete(
    "/delete_user/{user_id}",
    dependencies=[Depends(JWTBearer())],
    summary="Delete user",
    description="Deletes user and related roles by user_id"
)
async def delete_user(
    user_id: int,
    db_session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a user and related roles
    """
    logged_user_id = current_user['user_id']
    logger.info(f"Request from logged_user_id={logged_user_id} to delete user_id={user_id}")

    result = auth_user_service.delete_user(logged_user_id, user_id, db_session)

    logger.info(f"Delete result for user_id={user_id}: {result}")
    return res.create_response(
        HttpStatusCodes.StatusCodesDescription.SUCCESS_OK_200,
        HttpStatusCodes.StatusCodes.SUCCESS_OK_200,
        result
    )

@router.post("/add_new_user", dependencies=[Depends(JWTBearer())],
             summary='Add a user',
             description="Adds a new user")
async def add_user(adduser: AddUser, db_session: Session = Depends(get_session),
                   current_user: dict = Depends(get_current_user)):
    """
        add a new user
    """
    logged_user_id = current_user['user_id']
    result = await auth_user_service.add_new_user(logged_user_id, adduser, db_session)
    return res.create_response(
        "New user added successfully",
        HttpStatusCodes.StatusCodes.SUCCESS_OK_200,
        result)


@router.post("/add_user_test/{email}/{username}/{password}/{f_name}/{l_name}")
async def add_user(
        email: str,username: str, password: str, f_name: str, l_name: str,
        db_session: Session = Depends(get_session)):
    """
        add a new user
    """
    new_user = User(first_name=f_name, last_name=l_name,
                    email=email, password=get_password_hash(password), is_superuser=0, username=username,
                    is_active=True, is_staff=True)
    db_session.add(new_user)
    db_session.commit()
    add_user_role(new_user.id, 3, db_session)
    
    db_session.close()
    return res.create_response(
        "New test user added successfully",
        HttpStatusCodes.StatusCodes.SUCCESS_OK_200)

@router.get("/profile/", dependencies=[Depends(JWTBearer())])
def get_profile(current_user=Depends(get_current_user),db_session: Session = Depends(get_session)):
    user = get_user_details_by_id(db_session, user_id=current_user['user_id'])
    return UserProfileResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name
    )

@router.put("/update_role/",dependencies=[Depends(JWTBearer())])
def update_role(
    user_id:int,
    role_id: int,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    logged_user_id = current_user['user_id']
    result = auth_user_service.update_role(logged_user_id, user_id, role_id, session)
    return res.create_response(
        "User role updated successfully",
        HttpStatusCodes.StatusCodes.SUCCESS_OK_200,
        result)
    

@router.get("/userlist", dependencies=[Depends(JWTBearer())],
            summary='Get All users',
            description="returns details about all the users")
async def get_users(
                    db_session: Session = Depends(get_session),
                    current_user: dict = Depends(get_current_user)):
    """
        Gets all users
    """
    logged_user_id = current_user['user_id']
    result = auth_user_service.get_users(logged_user_id, db_session)
    if len(result) > 0:
        response = res.create_response(HttpStatusCodes.StatusCodesDescription.SUCCESS_OK_200,
                                       HttpStatusCodes.StatusCodes.SUCCESS_OK_200,
                                       result)
        return response

    response = res.create_response(HttpStatusCodes.StatusCodesDescription.NO_CONTENT_204,
                                   HttpStatusCodes.StatusCodes.NO_CONTENT_204,
                                   result)
    return response

