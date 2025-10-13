from sqlmodel import select, update, delete, func
from app.models.auth_user_model import User
from app.models.task_model import Task
from app.models.project_model import Project


def create_task(db_session, task: Task):
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task

def get_task_by_id(db_session, task_id: int):
    return db_session.get(Task, task_id)


def count_tasks_by_filters(db_session, user_role: int = None, user_id: int = None, keyword: str = ""):
    count_stmt = select(func.count(Task.id))
    
    if user_role == 3 and user_id:
        count_stmt = count_stmt.where(Task.assigned_to == user_id)
    
    if keyword:
        count_stmt = count_stmt.where(Task.title.ilike(f"%{keyword}%"))
    
    return db_session.exec(count_stmt).one()


def get_tasks_with_details_paginated(db_session, user_role: int = None, user_id: int = None, 
                                   keyword: str = "", offset: int = 0, limit: int = 10):
    statement = (
        select(
            Task.id,
            Task.title,
            Task.description,
            Task.priority,
            Task.start_date,
            Task.due_date,
            Task.project_id,
            Task.status,
            Project.name.label("project_name"),
            User.username.label("username"),
            User.id.label("assigned_to")
        )
        .join(User, User.id == Task.assigned_to, isouter=True)
        .join(Project, Project.id == Task.project_id, isouter=True)
    )

    if user_role == 3 and user_id:
        statement = statement.where(Task.assigned_to == user_id)

    if keyword:
        statement = statement.where(Task.title.ilike(f"%{keyword}%"))

    statement = statement.order_by(Task.id).offset(offset).limit(limit)
    return db_session.exec(statement).all()


def get_tasks_for_user(db_session, user_id: int):
    return db_session.exec(select(Task).where(Task.assigned_to == user_id)).all()

def search_tasks(db_session, keyword: str):
    return db_session.exec(
        select(Task).where(
            (Task.title.ilike(f"%{keyword}%")) |
            (Task.description.ilike(f"%{keyword}%"))
        )
    ).all()

def update_task(db_session, task_id: int, updated_data: dict):
    stmt = update(Task).where(Task.id == task_id).values(**updated_data)
    result = db_session.exec(stmt)
    db_session.commit()
    return result.rowcount > 0


def update_task_column(db_session, task_id: int, column: str, value):
    stmt = update(Task).where(Task.id == task_id).values({column: value})
    result = db_session.exec(stmt)
    db_session.commit()
    return result.rowcount > 0

def delete_task(db_session, task_id: int):
    stmt = delete(Task).where(Task.id == task_id)
    result = db_session.exec(stmt)
    db_session.commit()
    return result.rowcount > 0
