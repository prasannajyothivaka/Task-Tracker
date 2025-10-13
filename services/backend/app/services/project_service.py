from app.repositories import project_repository
from app.models.project_model import Project
from app.dto.project_dto import AddProject
import math


def create_project(user_id: int, project_data: AddProject, db_session):
    # Business logic: Create project with user as owner and creator
    new_project = Project(
        name=project_data.name,
        description=project_data.description,
        start_date=project_data.start_date,
        end_date=project_data.end_date,
        status=project_data.status,
        owner_id=user_id,
        created_by=user_id,
        updated_by=user_id
    )
    
    created_project = project_repository.create_project(db_session, new_project)
    
    # Business logic: Return formatted response
    return {"id": created_project.id, "message": "Project created successfully"}


def get_all_projects(logged_user_id, db_session, keyword, page):
    # Business logic: Handle pagination and user role-based access
    page_size = 10
    offset = (page - 1) * page_size
    
    # Get user role for access control
    user_role = project_repository.get_user_role(db_session, logged_user_id)
    
    # Build query based on user role and filters
    query = project_repository.get_all_projects_query(
        db_session, user_role, logged_user_id, keyword
    )
    
    # Business logic: Calculate pagination
    total_count = project_repository.count_projects(db_session, query)
    pages = math.ceil(total_count / page_size) if total_count > 0 else 1
    
    # Get paginated results
    projects = project_repository.get_projects_paginated(db_session, query, offset, page_size)
    
    return {
        "projects": projects,
        "page": page,
        "pages": pages,
    }


def get_project_by_id(logged_user_id, project_id: int, db_session):
    # Business logic: Get project and associated tasks
    project = project_repository.get_project_by_id(db_session, project_id)
    
    if not project:
        return {"message": "Project not found"}
    
    # Business logic: Get all tasks for this project
    tasks = project_repository.get_tasks_by_project_id(db_session, project_id)
    
    # Business logic: Format response with project and tasks
    return {
        "project": project,
        "tasks": tasks
    }


def get_projects_for_user(user_id: int, db_session):
    # Business logic: Get projects owned by specific user
    projects = project_repository.get_projects_for_user(db_session, user_id)
    
    # Business logic: Return formatted response
    return {
        "projects": projects,
        "count": len(projects)
    }


def search_projects(keyword: str, db_session):
    # Business logic: Validate search keyword
    if not keyword or len(keyword.strip()) < 2:
        return {"message": "Search keyword must be at least 2 characters long", "projects": []}
    
    # Perform search
    projects = project_repository.search_projects(db_session, keyword.strip())
    
    # Business logic: Return formatted response with search metadata
    return {
        "projects": projects,
        "keyword": keyword.strip(),
        "count": len(projects)
    }


def update_project(project_id: int, project, user_id: int, db_session):
    # Business logic: Prepare update data with user tracking
    update_data = {
        "name": project.name,
        "description": project.description,
        "start_date": project.start_date,
        "end_date": project.end_date,
        "status": project.status,
        "owner_id": user_id,
        "updated_by": user_id
    }
    
    # Business logic: Check if update was successful
    success = project_repository.update_project(db_session, project_id, update_data)
    
    if not success:
        return {"message": "Project not found or update failed"}
    
    return {"message": "Project updated successfully"}


def delete_project(project_id: int, db_session):
    # Business logic: Check if project exists before deletion
    project = project_repository.get_project_by_id(db_session, project_id)
    
    if not project:
        return {"message": "Project not found"}
    
    # Perform deletion
    project_repository.delete_project(db_session, project)
    
    # Business logic: Return success message
    return {"message": f"Project {project_id} deleted successfully"}
