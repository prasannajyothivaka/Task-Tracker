from sqlmodel import select
from sqlalchemy import update,func, desc
from app.models.project_model import Project
from app.models.task_model import Task
from app.models.user_role_model import UserRole
import math


def create_project(db_session, project: Project):
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return {"id": project.id, "message": "Project created successfully"}


def get_all_projects(logged_user_id, db_session, keyword: str = "", page: int = 1):
    page_size = 10
    offset = (page - 1) * page_size

    # Step 1: Check the logged-in user's role
    user_role = db_session.exec(
        select(UserRole.role_id).where(UserRole.user_id == logged_user_id)
    ).first()

    # Step 2: Base query with active projects
    query = select(Project).where(Project.is_active == True)

    # Step 3: Restrict if role_id == 3 → only projects with tasks assigned to the user
    if user_role == 3:
        query = query.where(
            Project.id.in_(
                select(Task.project_id).where(Task.assigned_to == logged_user_id)
            )
        )

    # Step 4: Apply search filter if keyword is provided
    if keyword:
        query = query.where(Project.name.ilike(f"%{keyword}%"))

    # Step 5: Count total projects for pagination (with the same filters!)
    count_query = query.with_only_columns(func.count()).order_by(None)
    total_count = db_session.exec(count_query).one()

    pages = math.ceil(total_count / page_size) if total_count > 0 else 1

    # Step 6: Apply ordering, offset, and limit
    query = query.order_by(desc(Project.id)).offset(offset).limit(page_size)
    projects = db_session.exec(query).all()

    return {
        "projects": projects,
        "page": page,
        "pages": pages,
    }

def get_project_by_id(logged_user_id, db_session, project_id: int):
    # Get project
    project = db_session.get(Project, project_id)
    if not project:
        return None
    
    # Get all tasks for this project
    tasks = db_session.exec(
        select(Task).where(Task.project_id == project_id, Task.is_active == True).order_by(desc(Task.id))
    ).all()
    
    # Return both
    return {
        "project": project,
        "tasks": tasks
    }


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


def update_project(project_id, project: Project, user_id, db_session):

    stmt = (
        update(Project)
        .where(Project.id == project_id)
        .values(
            name=project.name,
            description=project.description,
            start_date=project.start_date,
            end_date=project.end_date,
            status=project.status,
            owner_id=user_id,
            updated_by=user_id
        )
    )

    result = db_session.exec(stmt)
    db_session.commit()

    # result.rowcount gives number of updated rows
    if result.rowcount == 0:
        return False
    
    return True

def delete_project(db_session, project: Project):
    db_session.delete(project)
    db_session.commit()
