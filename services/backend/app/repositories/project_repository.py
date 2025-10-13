from sqlmodel import select
from sqlalchemy import update, func, desc
from app.models.project_model import Project
from app.models.task_model import Task
from app.models.user_role_model import UserRole


def create_project(db_session, project: Project):
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


def get_user_role(db_session, user_id: int):
    return db_session.exec(
        select(UserRole.role_id).where(UserRole.user_id == user_id)
    ).first()


def get_projects_assigned_to_user(db_session, user_id: int):
    return select(Task.project_id).where(Task.assigned_to == user_id)


def get_all_projects_query(db_session, user_role_id: int = None, user_id: int = None, keyword: str = ""):
    # Base query with active projects
    query = select(Project).where(Project.is_active == True)
    
    # Restrict if role_id == 3 → only projects with tasks assigned to the user
    if user_role_id == 3 and user_id:
        assigned_projects_subquery = get_projects_assigned_to_user(db_session, user_id)
        query = query.where(Project.id.in_(assigned_projects_subquery))
    
    # Apply search filter if keyword is provided
    if keyword:
        query = query.where(Project.name.ilike(f"%{keyword}%"))
    
    return query


def count_projects(db_session, query):
    count_query = query.with_only_columns(func.count()).order_by(None)
    return db_session.exec(count_query).one()


def get_projects_paginated(db_session, query, offset: int, limit: int):
    query = query.order_by(desc(Project.id)).offset(offset).limit(limit)
    return db_session.exec(query).all()

def get_project_by_id(db_session, project_id: int):
    return db_session.get(Project, project_id)


def get_tasks_by_project_id(db_session, project_id: int):
    return db_session.exec(
        select(Task).where(Task.project_id == project_id, Task.is_active == True).order_by(desc(Task.id))
    ).all()


def get_projects_for_user(db_session, user_id: int):
    return db_session.exec(
        select(Project).where(Project.owner_id == user_id)
    ).all()


def search_projects(db_session, keyword: str):
    return db_session.exec(
        select(Project).where(
            (Project.name.ilike(f"%{keyword}%")) |
            (Project.description.ilike(f"%{keyword}%"))
        )
    ).all()


def update_project(db_session, project_id: int, project_data: dict):
    stmt = (
        update(Project)
        .where(Project.id == project_id)
        .values(**project_data)
    )
    
    result = db_session.exec(stmt)
    db_session.commit()
    
    return result.rowcount > 0

def delete_project(db_session, project: Project):
    db_session.delete(project)
    db_session.commit()
