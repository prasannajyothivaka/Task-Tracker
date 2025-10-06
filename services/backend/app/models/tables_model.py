"""
    Responsible for calling all functions for creating tables
"""
from app.models import (
    auth_user_model, project_model, 
    role_model, task_model, 
    user_role_model
)
from app.database import engine
from app.models import auth_user_model

def create_tables():
    """
        main function for creating tables by calling respective create model functions
    """
    #For Creating tables in the database
    task_model.SQLModel.metadata.create_all(engine)
    auth_user_model.SQLModel.metadata.create_all(engine)
    user_role_model.SQLModel.metadata.create_all(engine)
    role_model.SQLModel.metadata.create_all(engine)
    project_model.SQLModel.metadata.create_all(engine)
