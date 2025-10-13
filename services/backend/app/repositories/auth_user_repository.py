"""
    CRUD operations for user related to different users
"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from sqlalchemy.orm import load_only
from sqlmodel import Session, select
from app.database import get_session
from app.models.auth_user_model import User
from app.models.task_model import Task
from app.models.user_role_model import UserRole
from app.models.role_model import Role
from passlib.context import CryptContext



def get_active_user_by_username(username, session):
    """
    Get an active user by their username or email.
    """
    statement = (
        select(User)
        .where(User.email == username, User.is_active == True)
        .options(
            load_only(
                User.id,
                User.username,
                User.first_name,
                User.last_name,
                User.email,
                User.last_login,
            )
        )
        .limit(1)
    )
    return session.execute(statement).scalar_one_or_none()


def update_user_role(session, user_id, role_id):
    """
    Update user role - data access only
    """
    userrole_stmt = update(UserRole).where(UserRole.user_id == user_id).values(role_id=role_id)
    result = session.execute(userrole_stmt)
    session.commit()
    return result.rowcount > 0
    


def get_users_with_roles(db_session):
    """
    Get all users with their role information - data access only
    """
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
        .join(UserRole, UserRole.user_id == User.id, isouter=True)
        .join(Role, Role.id == UserRole.role_id, isouter=True)
        .order_by(Role.role_name, User.email)
    )

    results = db_session.exec(stmt).fetchall()
    return [dict(user._mapping) for user in results]

def get_users_by_role(db_session, user_role_id: int):
    """
    Get all users by specific role - data access only
    """
    statement = select(
        User.id, User.first_name, User.last_name,
        User.email, User.username,
        coalesce(UserRole.role_id, 3).label("role_id")
    ).join(UserRole, UserRole.user_id == User.id)\
     .where(UserRole.role_id == user_role_id)\
     .order_by(User.email)

    return [dict(row) for row in db_session.exec(statement).mappings().all()]


def check_email_exists(db_session, email: str):
    """
    Check if email exists in database - data access only
    """
    statement = select(User.email).where(User.email == email)
    result = db_session.exec(statement).first()
    return result is not None


def create_user(db_session, user_data: dict):
    """
    Create new user - data access only
    """
    new_user = User(**user_data)
    db_session.add(new_user)
    db_session.flush()
    db_session.refresh(new_user)
    return new_user.id

def create_user_role(db_session, user_id: int, role_id: int):
    """
    Create user role mapping - data access only
    """
    new_user_role = UserRole(role_id=role_id, user_id=user_id)
    db_session.add(new_user_role)
    db_session.commit()
    return True

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

def update_user_profile_data(session: Session, user_id: int, update_data: dict):
    """
    Update user profile - data access only
    """
    user = get_user_details_by_id(session, user_id)
    
    for key, value in update_data.items():
        if hasattr(user, key) and value is not None:
            setattr(user, key, value)
    
    from datetime import datetime, timezone
    user.updated_at = datetime.now(timezone.utc)
    
    session.commit()
    session.refresh(user)
    return user

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    """
        get hashed password
    """
    return bcrypt_context.hash(password)



def unassign_user_tasks(session, user_id):
    """
    Unassign all tasks from user - data access only
    """
    task_stmt = update(Task).where(Task.assigned_to == user_id).values(assigned_to=None)
    result = session.execute(task_stmt)
    return result.rowcount


def update_user_role_to_default(session, user_id, default_role_id=3):
    """
    Update user role to default role - data access only
    """
    user_role = UserRole(user_id=user_id, role_id=default_role_id)
    session.merge(user_role)
    session.commit()
    return True