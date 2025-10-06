from app.repositories import project_repository
from app.models.project_model import Project
from app.dto.project_dto import AddProject


def create_project(user_id: int, project_data: AddProject, db_session):
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
    return project_repository.create_project(db_session, new_project)


def get_all_projects(logged_user_id, db_session, keyword, page):
    return project_repository.get_all_projects(
        logged_user_id,db_session, keyword, page)


def get_project_by_id(logged_user_id,project_id: int, db_session):
    project = project_repository.get_project_by_id(logged_user_id,db_session, project_id)
    if not project:
        return {"message": "Project not found"}
    return project


def get_projects_for_user(user_id: int, db_session):
    return project_repository.get_projects_for_user(db_session, user_id)


def search_projects(keyword: str, db_session):
    return project_repository.search_projects(db_session, keyword)


def update_project(project_id: int, project, user_id: int, db_session):
    return project_repository.update_project(project_id,project,user_id,db_session)


def delete_project(project_id: int, db_session):
    project = project_repository.get_project_by_id(db_session, project_id)
    if not project:
        return {"message": "Project not found"}
    project_repository.delete_project(db_session, project)
    return {"message": f"Project {project_id} deleted successfully"}
