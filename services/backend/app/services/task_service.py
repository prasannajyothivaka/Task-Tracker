from app.repositories import task_repository
from app.repositories.user_role_repository import get_role
from app.models.task_model import Task
from app.dto.task_dto import AddTask
import math

# Constants
TASK_NOT_FOUND = "Task not found"
TASK_UPDATED_SUCCESS = "Task updated successfully"
TASK_DELETED_SUCCESS = "Task deleted successfully"


def create_task(user_id: int, task_data: AddTask, db_session):
    # Business logic: Create task with audit trail
    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        project_id=task_data.project_id,
        assigned_to=task_data.assigned_to,
        start_date=task_data.start_date,
        due_date=task_data.due_date,
        status=task_data.status,
        priority=task_data.priority,
        created_by=user_id,
        updated_by=user_id
    )
    
    created_task = task_repository.create_task(db_session, new_task)
    
    # Business logic: Return formatted response
    return {"id": created_task.id, "message": "Task created successfully"}

def get_task(task_id: int, db_session):
    task = task_repository.get_task_by_id(db_session, task_id)
    if not task:
        return {"message": TASK_NOT_FOUND}
    return task

def get_all_tasks(user_id, db_session, keyword, page):
    # Business logic: Handle pagination and role-based access
    page_size = 10
    offset = (page - 1) * page_size
    
    # Business logic: Get user role for access control
    role = get_role(user_id)
    
    # Business logic: Count total tasks for pagination
    total_count = task_repository.count_tasks_by_filters(db_session, role, user_id, keyword)
    pages = math.ceil(total_count / page_size) if total_count > 0 else 1
    
    # Get paginated tasks with details
    results = task_repository.get_tasks_with_details_paginated(
        db_session, role, user_id, keyword, offset, page_size
    )
    
    # Business logic: Format task data
    tasks = [
        {
            "id": row.id,
            "title": row.title,
            "description": row.description,
            "priority": row.priority,
            "status": row.status,
            "start_date": row.start_date,
            "due_date": row.due_date,
            "project_id": row.project_id,
            "project_name": row.project_name,
            "assigned_to": row.assigned_to,
            "username": row.username,
        }
        for row in results
    ]
    
    return {"tasks": tasks, "page": page, "pages": pages, "total": total_count}

def get_user_tasks(user_id: int, db_session):
    # Business logic: Get tasks assigned to specific user
    tasks = task_repository.get_tasks_for_user(db_session, user_id)
    
    # Business logic: Return formatted response
    return {
        "tasks": tasks,
        "count": len(tasks),
        "user_id": user_id
    }


def search_tasks(keyword: str, db_session):
    # Business logic: Validate search keyword
    if not keyword or len(keyword.strip()) < 2:
        return {"message": "Search keyword must be at least 2 characters long", "tasks": []}
    
    # Perform search
    tasks = task_repository.search_tasks(db_session, keyword.strip())
    
    # Business logic: Return formatted response with search metadata
    return {
        "tasks": tasks,
        "keyword": keyword.strip(),
        "count": len(tasks)
    }

def update_task(user_id, task_id: int, updated_data: dict, db_session):
    # Business logic: Add audit trail to update data
    updated_data_with_audit = {
        **updated_data,
        "updated_by": user_id
    }
    
    # Perform update
    updated = task_repository.update_task(db_session, task_id, updated_data_with_audit)
    
    # Business logic: Check if update was successful
    if not updated:
        return {"message": TASK_NOT_FOUND}
    
    return {"message": TASK_UPDATED_SUCCESS}


def update_task_column(task_id, column, value, db_session):
    # Business logic: Check if task exists first
    task = task_repository.get_task_by_id(db_session, task_id)
    if not task:
        return {"message": TASK_NOT_FOUND}
    
    # Business logic: Validate column update
    allowed_columns = ["status", "priority", "assigned_to", "title", "description"]
    if column not in allowed_columns:
        return {"message": f"Column '{column}' is not allowed to be updated"}
    
    # Perform update
    updated = task_repository.update_task_column(db_session, task_id, column, value)
    
    if not updated:
        return {"message": "Task update failed"}
    
    return {"message": TASK_UPDATED_SUCCESS}

def delete_task(task_id: int, db_session):
    # Business logic: Check if task exists before deletion
    task = task_repository.get_task_by_id(db_session, task_id)
    if not task:
        return {"message": TASK_NOT_FOUND}
    
    # Perform deletion
    deleted = task_repository.delete_task(db_session, task_id)
    
    if not deleted:
        return {"message": "Task deletion failed"}
    
    # Business logic: Return success message with task info
    return {"message": f"Task '{task.title}' deleted successfully"}
