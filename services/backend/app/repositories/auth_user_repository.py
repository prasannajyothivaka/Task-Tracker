"""
    CRUD operations for user related to different users
"""
import logging
import time
from datetime import datetime
from sqlalchemy.sql.functions import coalesce
from collections import defaultdict
from fastapi import Depends, HTTPException,status
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from sqlalchemy.orm import load_only
from sqlmodel import Session, select
from app.database import get_session
from app.models.auth_user_model import User
from app.dto.user_dto import AddUser
from app.models.task_model import Task
from app.models.project_model import Project
from app.models.user_role_model import UserRole
from app.models.role_model import Role
from app.repositories.user_role_repository import is_authorized_user, is_admin
from app.utility.exceptions_utility import unauthorised_exception
from passlib.context import CryptContext


load_dotenv()
logger = logging.getLogger(__name__)


def get_active_user_by_username(username, session):
    """
    gets the user name by its name
    """
    statement = select(User).where(User.email == username,User.is_active ==True).\
        options(load_only('id', 'username', 'first_name', 'last_name', 'email', 'last_login')).limit(1)
    return session.execute(statement).scalar_one_or_none()

def update_role(logged_user_id, user_id, role_id, session):
    """
    Update user role
    """
    if not is_admin(logged_user_id, session):
        raise unauthorised_exception()
    userrole_stmt = update(UserRole).where(UserRole.user_id == user_id).values(role_id=role_id)
    session.execute(userrole_stmt)
    
    session.commit()
    return "Role Updated Successfully"
    


def get_users_grouped(logged_user_id, db_session):
    """
    Get all users grouped by role name
    """
    if not is_admin(logged_user_id, db_session):
        raise unauthorised_exception()
    
    stmt = (
        select(
            User.id,
            User.first_name,
            User.last_name,
            User.email,
            User.username,
            UserRole.role_id,
            coalesce(Role.role_name, "User").label("role_name"),
        )
        .join(UserRole, UserRole.user_id == User.id, isouter=True)  # left join in case user has no role
        .join(Role, Role.id == UserRole.role_id, isouter=True)       # left join to get role name
        .order_by(Role.role_name, User.email)
    )

    results = db_session.exec(stmt).fetchall()

    # Convert Row objects to dicts
    users_as_dicts = [dict(user._mapping) for user in results]

    # Group by role_name
    grouped = defaultdict(list)
    for user in users_as_dicts:
        grouped[user["role_name"]].append(user)

    return dict(grouped)

def get_all_users(logged_user_id: int,user_role_id:int,
    db_session: Session = Depends(get_session)):
    """
        Gets details of all users available
    """
    if is_authorized_user(logged_user_id, db_session):

        statement = select(User.id, User.first_name, User.last_name,
                           User.email, User.username,
                           coalesce(UserRole.role_id, 3).label("role_id"))

        statement = statement.\
            join(UserRole, UserRole.user_id == User.id).\
            where(UserRole.role_id == user_role_id)

        get_users = statement.\
            order_by(User.email)

        start_query = time.time()
        results = db_session.exec(get_users).fetchall()
        logger.info("{} ran in {}s".\
            format("is_authorized_user_"+str(user_role_id)+"_query", round(time.time() - start_query, 2)))

        return results

    else:
        raise unauthorised_exception()

#use
def get_email(logged_user_id: int, email: str, db_session: Session = Depends(get_session)):
    """
        Gets details of email available or not
    """
    start = time.time()
    if is_admin(logged_user_id, db_session) == True:
        statement = select(User.email).where(User.email == email)
        results = db_session.exec(statement).first()
        is_exists = False
        if results != None:
            is_exists = True
            logger.info("{} ran in {}s".format("get_email", round(time.time() - start, 2)))
            
        return is_exists

    else:
        raise unauthorised_exception()


def add_user(adduser: AddUser,encrypt_password:str,
             db_session: Session = Depends(get_session)):
    """
    add new user
    """
    new_user = User(email=adduser.email, first_name=adduser.first_name,
                    last_name=adduser.last_name, password=encrypt_password,
                    is_superuser=0, username=adduser.email)
    db_session.add(new_user)
    db_session.flush()
    db_session.refresh(new_user)

    return new_user.id

def add_user_role(new_user_id: int, user_role_id : int,
                  db_session: Session = Depends(get_session)):
    """
    maps user role
    """
    new_user_role = UserRole(role_id=user_role_id, user_id=new_user_id)
    db_session.add(new_user_role)
    db_session.commit()
    db_session.close()

def get_user_id_async(email: str, db_session: AsyncSession):
    """
    gets details about email available or not
    """
    statement = select(User.id).where(User.email == email)
    results = db_session.execute(statement).first()
    return results


def get_user_details_by_id(session: Session, user_id: int):
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

def get_user_by_email(session: Session, email: str):
    return session.query(User).filter(User.email == email).first()

def update_user_profile(session: Session, user_id: int, name: str,
                        email: str, password: str):
    user = get_user_details_by_id(session, user_id)

    # check if email is already taken by another user
    if email:
        existing_user = get_user_by_email(session, email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Email already in use by another user")
        user.email = email

    if name:
        user.first_name = name

    if password:
        user.password = get_password_hash(password)

    from datetime import datetime
    user.updated_at = datetime.utcnow()

    session.commit()
    session.refresh(user)
    return user

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    """
        get hashed password
    """
    return bcrypt_context.hash(password)



def delete_user(logged_user_id, user_id, session):
    """Update tasks assigned_to as null and role_id in userrole table"""
    if not is_admin(logged_user_id, session):
        raise unauthorised_exception()
    
    # Update assigned_to as null in task table where assigned_to = user_id
    task_stmt = update(Task).where(Task.assigned_to == user_id).values(assigned_to=None)
    session.execute(task_stmt)
    
    # Update role_id as null in userrole table where user_id = user_id
    user_role = UserRole(user_id=user_id, role_id=3)
    session.merge(user_role)  # merge handles insert or update automatically
    session.commit()
    
    return {"message": f"User {user_id} tasks and roles updated successfully"}