from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.database import get_session
from app.utility import response as res
from app.utility.http_status_codes import HttpStatusCodes
from app.auth.auth_bearer import JWTBearer
from app.dto.project_dto import AddProject
from app.services import project_service
from app.services.login_service import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects", tags=["Projects"])


# ------------------ CREATE ------------------
@router.post(
    "/create/",
    dependencies=[Depends(JWTBearer())],
    summary="Create a new project",
    description="Creates a new project for the logged-in user"
)
async def create_project(
    project: AddProject,
    db_session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    logged_user_id = current_user["user_id"]
    result = project_service.create_project(logged_user_id, project, db_session)
    logger.info(f"User {logged_user_id} creating project {project.name}")
    return res.create_response(
        HttpStatusCodes.StatusCodesDescription.SUCCESS_OK_200,
        HttpStatusCodes.StatusCodes.SUCCESS_OK_200,
        result
    )


# ------------------ GET ALL ------------------
@router.get(
    "/",
    dependencies=[Depends(JWTBearer())],
    summary="Get all projects",
    description="Returns all projects in the system"
)
async def get_all_projects(
    keyword: str = "",
    page: int = 1,
    db_session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    logged_user_id = current_user["user_id"]
    result = project_service.get_all_projects(
        logged_user_id, db_session, keyword=keyword, page=page)
    return res.create_response(
        HttpStatusCodes.StatusCodesDescription.SUCCESS_OK_200,
        HttpStatusCodes.StatusCodes.SUCCESS_OK_200,
        result,
    )


# ------------------ GET BY ID ------------------
@router.get(
    "/{project_id}/",
    dependencies=[Depends(JWTBearer())],
    summary="Get project by ID",
    description="Returns a project based on ID"
)
async def get_project_by_id(
    project_id: int,
    db_session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    result = project_service.get_project_by_id(current_user, project_id, db_session)
    return res.create_response(
        HttpStatusCodes.StatusCodesDescription.SUCCESS_OK_200,
        HttpStatusCodes.StatusCodes.SUCCESS_OK_200,
        result
    )


# ------------------ GET BY LOGGED USER ------------------
@router.get(
    "/user/projects",
    dependencies=[Depends(JWTBearer())],
    summary="Get projects for logged-in user",
    description="Returns all projects owned by the logged-in user"
)
async def get_user_projects(
    db_session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    logged_user_id = current_user["user_id"]
    result = project_service.get_projects_for_user(logged_user_id, db_session)
    return res.create_response(
        HttpStatusCodes.StatusCodesDescription.SUCCESS_OK_200,
        HttpStatusCodes.StatusCodes.SUCCESS_OK_200,
        result
    )


# ------------------ SEARCH ------------------
@router.get(
    "/search/{keyword}",
    dependencies=[Depends(JWTBearer())],
    summary="Search projects",
    description="Search projects by title or description"
)
async def search_projects(
    keyword: str,
    db_session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    result = project_service.search_projects(keyword, db_session)
    return res.create_response(
        HttpStatusCodes.StatusCodesDescription.SUCCESS_OK_200,
        HttpStatusCodes.StatusCodes.SUCCESS_OK_200,
        result
    )


# ------------------ UPDATE ------------------
@router.put(
    "/update/{project_id}/",
    dependencies=[Depends(JWTBearer())],
    summary="Update project",
    description="Update an existing project"
)
async def update_project(
    project_id: int,
    project_data: AddProject,
    db_session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    logged_user_id = current_user["user_id"]
    result = project_service.update_project(project_id, project_data, logged_user_id, db_session)
    return res.create_response(
        HttpStatusCodes.StatusCodesDescription.SUCCESS_OK_200,
        HttpStatusCodes.StatusCodes.SUCCESS_OK_200,
        result
    )


# ------------------ DELETE ------------------
@router.delete(
    "/{project_id}",
    dependencies=[Depends(JWTBearer())],
    summary="Delete project",
    description="Delete a project by ID"
)
async def delete_project(
    project_id: int,
    db_session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    result = project_service.delete_project(project_id, db_session)
    return res.create_response(
        HttpStatusCodes.StatusCodesDescription.SUCCESS_OK_200,
        HttpStatusCodes.StatusCodes.SUCCESS_OK_200,
        result
    )
