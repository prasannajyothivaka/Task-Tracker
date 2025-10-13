"""
    business logic operations for user
"""
import logging
import time
from collections import defaultdict
from fastapi import Depends, HTTPException, status
from sqlmodel import Session
from app.database import get_session
from app.repositories import auth_user_repository
from app.dto.user_dto import AddUser
from app.services.login_service import get_password_hash, get_random_password
from app.repositories.user_role_repository import is_admin, is_authorized_user
from app.utility.exceptions_utility import unauthorised_exception
from app.decorators.logger_decorator import logger_wraps

# Constants
USER_NOT_FOUND = "User not found"
UNAUTHORIZED_ACCESS = "Unauthorized access"
EMAIL_ALREADY_EXISTS = "Email already in use by another user"
ROLE_UPDATED_SUCCESS = "Role Updated Successfully"

logger = logging.getLogger(__name__)


def get_all_users(logged_user_id: int, role_id: int, db_session: Session = Depends(get_session)):
    """
    Get details of users by role - business logic with authorization
    """
    start = time.time()
    
    # Business logic: Check authorization
    if not is_authorized_user(logged_user_id, db_session):
        raise unauthorised_exception()
    
    # Get users by role
    results = auth_user_repository.get_users_by_role(db_session, role_id)
    
    # Business logic: Log performance
    logger.info("{} ran in {}s".format(
        "get_all_users_service_" + str(role_id) + "_func", 
        round(time.time() - start, 2)
    ))
    
    return results

def get_users(logged_user_id: int, db_session: Session = Depends(get_session)):
    """
    Get users grouped by role - business logic with authorization
    """
    # Business logic: Check admin authorization
    if not is_admin(logged_user_id, db_session):
        raise unauthorised_exception()
    
    # Get users with roles
    users_as_dicts = auth_user_repository.get_users_with_roles(db_session)
    
    # Business logic: Group users by role name
    grouped = defaultdict(list)
    for user in users_as_dicts:
        grouped[user["role_name"]].append(user)
    
    return dict(grouped)

def update_role(logged_user_id, user_id, role_id, session):
    """
    Update user role - business logic with authorization
    """
    # Business logic: Check admin authorization
    if not is_admin(logged_user_id, session):
        raise unauthorised_exception()
    
    # Business logic: Validate user exists
    user = auth_user_repository.get_user_details_by_id(session, user_id)
    if not user:
        return {"message": USER_NOT_FOUND}
    
    # Update role
    success = auth_user_repository.update_user_role(session, user_id, role_id)
    
    if not success:
        return {"message": "Role update failed"}
    
    return {"message": ROLE_UPDATED_SUCCESS}


def get_email(logged_user_id: int, email: str, db_session: Session = Depends(get_session)):
    """
    Check if email exists - business logic with authorization
    """
    # Business logic: Check admin authorization
    if not is_admin(logged_user_id, db_session):
        raise unauthorised_exception()
    
    # Business logic: Validate email format
    if not email or "@" not in email:
        return {"exists": False, "message": "Invalid email format"}
    
    # Check if email exists
    exists = auth_user_repository.check_email_exists(db_session, email)
    
    return {"exists": exists, "email": email}


def delete_user(logged_user_id: int, user_id: int, db_session: Session = Depends(get_session)):
    """
    Deactivate user by unassigning tasks and setting default role - business logic
    """
    # Business logic: Check admin authorization
    if not is_admin(logged_user_id, db_session):
        raise unauthorised_exception()
    
    # Business logic: Check if user exists
    user = auth_user_repository.get_user_details_by_id(db_session, user_id)
    if not user:
        return {"message": USER_NOT_FOUND}
    
    # Business logic: Cannot delete self
    if logged_user_id == user_id:
        return {"message": "Cannot delete your own account"}
    
    # Business logic: Unassign all user tasks
    unassigned_count = auth_user_repository.unassign_user_tasks(db_session, user_id)
    
    # Business logic: Set user to default role
    auth_user_repository.update_user_role_to_default(db_session, user_id)
    
    return {
        "message": f"User {user_id} deactivated successfully",
        "tasks_unassigned": unassigned_count
    }



@logger_wraps()
async def add_new_user(logged_user_id: int, adduser: AddUser, db_session: Session = Depends(get_session)):
    """
    Add new user - business logic with validation and authorization
    """
    start = time.time()
    
    # Business logic: Check admin authorization
    if not is_admin(logged_user_id, db_session):
        raise unauthorised_exception()
    
    # Business logic: Validate email format
    if not adduser.email or "@" not in adduser.email:
        return {"message": "Invalid email format"}, None
    
    # Business logic: Check if user already exists
    user_exists = auth_user_repository.check_email_exists(db_session, adduser.email)
    
    if user_exists:
        return {"message": "User with this email already exists"}, None
    
    # Business logic: Handle password generation
    generated_password = None
    if adduser.password:
        encrypt_password = get_password_hash(adduser.password)
    else:
        generated_password = get_random_password(10)
        encrypt_password = get_password_hash(generated_password)
    
    # Business logic: Prepare user data
    user_data = {
        "email": adduser.email,
        "first_name": adduser.first_name,
        "last_name": adduser.last_name,
        "password": encrypt_password,
        "is_superuser": 0,
        "username": adduser.email
    }
    
    # Create user
    new_user_id = auth_user_repository.create_user(db_session, user_data)
    
    # Create user role mapping
    auth_user_repository.create_user_role(db_session, new_user_id, adduser.role_id)
    
    # Business logic: Log performance
    logger.info("{} ran in {}s".format("add_new_user_service", round(time.time() - start, 2)))
    
    return {
        "message": "User created successfully",
        "user_id": new_user_id,
        "generated_password": generated_password
    }, new_user_id


def update_user_profile(logged_user_id: int, user_id: int, name: str = None, 
                       email: str = None, password: str = None, db_session: Session = Depends(get_session)):
    """
    Update user profile - business logic with validation
    """
    # Business logic: Users can only update their own profile, or admins can update any
    if logged_user_id != user_id and not is_admin(logged_user_id, db_session):
        raise unauthorised_exception()
    
    # Business logic: Check if user exists
    user = auth_user_repository.get_user_details_by_id(db_session, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=USER_NOT_FOUND)
    
    # Business logic: Validate email if provided
    if email and email != user.email:
        existing_user = auth_user_repository.get_user_by_email(db_session, email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=EMAIL_ALREADY_EXISTS)
    
    # Business logic: Prepare update data
    update_data = {}
    if name:
        update_data["first_name"] = name
    if email:
        update_data["email"] = email
    if password:
        update_data["password"] = get_password_hash(password)
    
    # Update user
    updated_user = auth_user_repository.update_user_profile_data(db_session, user_id, update_data)
    
    return {"message": "Profile updated successfully", "user": updated_user}

