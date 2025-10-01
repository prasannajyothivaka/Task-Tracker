"""
    CRUD operations   related to get admin
"""
from fastapi import Depends
from sqlmodel import Session, select
from sqlalchemy import or_
from app.database import get_session, engine
from app.models.user_role_model import UserRole
from app.models.role_model import Role
from app.models.auth_user_model import User

DEFAULT_USER_ROLE =3

def is_admin(logged_user_id:int,db_session: Session = Depends(get_session)):
    """
        Gets details of all  admin users available
    """
    statement=select(UserRole.user_id).\
        join(Role,UserRole.role_id==Role.id).\
        where(UserRole.user_id==logged_user_id,Role.role_name=='Admin')

    is_admin = db_session.exec(statement).first()
    if is_admin is None:
        return False
    else:
        return True

def get_role(logged_user_id:int):
    """
        get user role
    """
    statement = select(UserRole.role_id).where(UserRole.user_id == logged_user_id)

    with Session(engine) as session:
        role_id = session.exec(statement).first()
        if role_id is not None:
            return role_id
        else:
            return DEFAULT_USER_ROLE

def is_authorized_user(logged_user_id:int,db_session: Session = Depends(get_session)):
    """
        Gets details of all  admin users available
    """
    statement=select(UserRole.user_id).\
        join(Role,UserRole.role_id==Role.id).\
        where(UserRole.user_id==logged_user_id,
              or_(Role.role_name=='Admin',Role.role_name=='TaskCreator'))

    is_auth_user = db_session.exec(statement).first()
    if is_auth_user is None:
        return False
    else:
        return True


def get_admins_list(db_session: Session = Depends(get_session)):
    """
    fetch all user with admin priviliges
    """
    get_all_admins= select(UserRole.user_id).where(UserRole.role_id==1)
    admin_id = db_session.exec(get_all_admins).fetchall()

    return admin_id
