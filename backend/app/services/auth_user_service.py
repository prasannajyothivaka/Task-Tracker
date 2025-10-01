"""
    business logic operations for user
"""
import logging
import time
from app.decorators.logger_decorator import logger_wraps
from fastapi import Depends
from sqlmodel import Session
from app.database import get_session
from app.repositories import auth_user_repository
from app.dto.user_dto import AddUser
from app.services.login_service import get_password_hash,get_random_password
from app.repositories.user_role_repository import is_admin
from app.utility.exceptions_utility import unauthorised_exception


logger = logging.getLogger(__name__)

def get_all_users(logged_user_id: int,role_id:int,
        db_session: Session = Depends(get_session)):
    """
    get details of user
    """
    start = time.time()
    logger.info("{} ran in {}s".\
        format("get_all_users_service_"+str(role_id)+"_func", round(time.time() - start, 2)))
    return auth_user_repository.get_all_users(logged_user_id,role_id,db_session)

def get_users(logged_user_id: int,
        db_session: Session = Depends(get_session)):
    """
    get details of user
    """
    return auth_user_repository.get_users_grouped(logged_user_id,db_session)

def update_role(logged_user_id, user_id, role_id, session):
    """
    update user role
    """
    return auth_user_repository.update_role(logged_user_id, user_id, role_id, session)


def get_email(logged_user_id: int,
        email: str, db_session: Session = Depends(get_session)):
    """
    get details of user email
    """
    return auth_user_repository.get_email(logged_user_id, email, db_session)


def delete_user(logged_user_id: int, user_id: int,
    db_session: Session = Depends(get_session)):
    """
    delete  user 
    """
    return auth_user_repository.delete_user(logged_user_id, user_id, db_session)



@logger_wraps()
async def add_new_user(logged_user_id: int, adduser: AddUser,
                   db_session: Session = Depends(get_session)):
    """
        add new user
    """
    start = time.time()
    if is_admin(logged_user_id, db_session):
        if adduser.password:
            encrypt_password=adduser.password
        else:
            password = get_random_password(10)
            encrypt_password = get_password_hash(password)

        user_exists=auth_user_repository.get_email(logged_user_id, adduser.email, db_session)

        if user_exists ==False:
            new_user_id = auth_user_repository.add_user(
                adduser, encrypt_password,db_session)


            auth_user_repository.add_user_role(new_user_id, adduser.role_id, db_session)
            logger.info("{} ran in {}s".\
                format("add_new_user_service", round(time.time() - start, 2)))
        return password, new_user_id
    else:
        raise unauthorised_exception()

