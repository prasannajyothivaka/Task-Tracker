from app.repositories import task_repository
from app.models.task_model import Task
from app.dto.task_dto import AddTask

def create_task(user_id: int, task_data: AddTask, db_session):
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
    return task_repository.create_task(db_session, new_task)

def get_task(task_id: int, db_session):
    task = task_repository.get_task_by_id(db_session, task_id)
    if not task:
        return {"message": "Task not found"}
    return task

def get_all_tasks(user_id,db_session, keyword, page):
    return task_repository.get_all_tasks(user_id,db_session,keyword,page)

def get_user_tasks(user_id: int, db_session):
    return task_repository.get_tasks_for_user(db_session, user_id)

def search_tasks(keyword: str, db_session):
    return task_repository.search_tasks(db_session, keyword)

def update_task(user_id, task_id: int, updated_data: dict, db_session):
    updated = task_repository.update_task(user_id,db_session, task_id, updated_data)
    if not updated:
        return {"message": "Task not found"}
    return {"message": "Task updated successfully"}


def update_task_column(user_id, task_id, column, value, db_session) :

    return task_repository.update_column(user_id, db_session, task_id, column, value)

def delete_task(task_id: int, db_session):
    deleted = task_repository.delete_task(db_session, task_id)
    if not deleted:
        return {"message": "Task not found"}
    return {"message": "Task deleted successfully"}
