from sqlmodel import select, update, delete,func
from app.models.auth_user_model import User
from app.models.task_model import Task
from app.models.project_model import Project
from app.repositories.user_role_repository import get_role
import math


def create_task(db_session, task: Task):
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return {"id": task.id, "message": "Task created successfully"}

def get_task_by_id(db_session, task_id: int):
    return db_session.get(Task, task_id)


def get_all_tasks(user_id, db_session, keyword: str = "", page: int = 1, page_size: int = 10):
    role = get_role(user_id)

    # Count total tasks first
    count_stmt = select(func.count(Task.id))
    if role == 3:
        count_stmt = count_stmt.where(Task.assigned_to == user_id)
    if keyword:
        count_stmt = count_stmt.where(Task.title.ilike(f"%{keyword}%"))

    total_count = db_session.exec(count_stmt).one()  # this returns a tuple like (42,)
    total_count = total_count  # extract the integer

    pages = math.ceil(total_count / page_size) if total_count > 0 else 1

    # Now fetch paginated tasks
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

    if role == 3:
        statement = statement.where(Task.assigned_to == user_id)

    if keyword:
        statement = statement.where(Task.title.ilike(f"%{keyword}%"))

    statement = statement.order_by(Task.id)

    statement = statement.offset((page - 1) * page_size).limit(page_size)
    results = db_session.exec(statement).all()

    tasks = [
        {
            "id": row.id,
            "title": row.title,
            "description": row.description,
            "priority": row.priority,
            "status": row.status,
            "start_date":row.start_date,
            "due_date": row.due_date,
            "project_id": row.project_id,
            "project_name": row.project_name,
            "assigned_to": row.assigned_to,
            "username": row.username,
        }
        for row in results
    ]

    return {"tasks": tasks, "page": page, "pages": pages, "total": total_count}


def get_tasks_for_user(db_session, user_id: int):
    return db_session.exec(select(Task).where(Task.assigned_to == user_id)).all()

def search_tasks(db_session, keyword: str):
    return db_session.exec(
        select(Task).where(
            (Task.title.ilike(f"%{keyword}%")) |
            (Task.description.ilike(f"%{keyword}%"))
        )
    ).all()

def update_task(user_id,db_session, task_id: int, updated_data: dict):
    stmt = update(Task).where(Task.id == task_id).values(**updated_data)
    result = db_session.exec(stmt)
    db_session.commit()
    return result.rowcount > 0

def update_column(user_id: int, db_session, task_id: int, column: str, value):
    # Check if task exists
    task = db_session.get(Task, task_id)
    if task:
        # Update dynamically
        stmt = update(Task).where(Task.id == task_id).values({column: value})
        db_session.exec(stmt)
        db_session.commit()

        # Return updated task
        db_session.refresh(task)
        return "Task Updated Successfully"

def delete_task(db_session, task_id: int):
    stmt = delete(Task).where(Task.id == task_id)
    result = db_session.exec(stmt)
    db_session.commit()
    return result.rowcount > 0
