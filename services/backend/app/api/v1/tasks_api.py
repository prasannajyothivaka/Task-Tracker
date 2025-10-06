from fastapi import APIRouter, Depends, Request
from sqlmodel import Session
from app.database import get_session
from app.utility import response as res
from app.utility.http_status_codes import HttpStatusCodes
from app.auth.auth_bearer import JWTBearer
from app.services.login_service import get_current_user
from app.services import task_service
from app.dto.task_dto import AddTask, UpdateTaskStatus

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# ------------------ CREATE ------------------
@router.post("/", dependencies=[Depends(JWTBearer())])
async def create_task(task: AddTask, db_session: Session = Depends(get_session), 
                      current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    result = task_service.create_task(user_id, task, db_session)
    return res.create_response(
        HttpStatusCodes.StatusCodes.SUCCESS_OK_200,
        HttpStatusCodes.StatusCodesDescription.SUCCESS_OK_200,
        result
    )

# ------------------ GET ALL ------------------
@router.get("/", dependencies=[Depends(JWTBearer())])
async def get_all_tasks( keyword: str = "", page: int = 1,
    db_session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    result = task_service.get_all_tasks(user_id,db_session,keyword,page)
    return res.create_response(
        HttpStatusCodes.StatusCodesDescription.SUCCESS_OK_200,
        HttpStatusCodes.StatusCodes.SUCCESS_OK_200,
        result
    )

# ------------------ GET TASK BY ID ------------------
@router.get("/{task_id}/", dependencies=[Depends(JWTBearer())])
async def get_task(task_id: int, db_session: Session = Depends(get_session)):
    result = task_service.get_task(task_id, db_session)
    return res.create_response(
        HttpStatusCodes.StatusCodesDescription.SUCCESS_OK_200,
        HttpStatusCodes.StatusCodes.SUCCESS_OK_200,
        result
    )

# ------------------ GET TASKS FOR LOGGED USER ------------------
@router.get("/user/me", dependencies=[Depends(JWTBearer())])
async def get_my_tasks(db_session: Session = Depends(get_session),
                    current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    result = task_service.get_user_tasks(user_id, db_session)
    return res.create_response(
        HttpStatusCodes.StatusCodesDescription.SUCCESS_OK_200,
        HttpStatusCodes.StatusCodes.SUCCESS_OK_200,
        result
    )

# ------------------ SEARCH TASKS ------------------
@router.get("/search/{keyword}", dependencies=[Depends(JWTBearer())])
async def search_tasks(keyword: str, db_session: Session = Depends(get_session)):
    result = task_service.search_tasks(keyword, db_session)
    return res.create_response(
        HttpStatusCodes.StatusCodesDescription.SUCCESS_OK_200,
        HttpStatusCodes.StatusCodes.SUCCESS_OK_200,
        result
    )

# ------------------ UPDATE TASK (FULL) ------------------
@router.post("/update/{task_id}/", dependencies=[Depends(JWTBearer())])
async def update_task(task_id: int, task_data: AddTask, 
                      db_session: Session = Depends(get_session), 
                      current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    updated_data = task_data.dict(exclude_unset=True)
    result = task_service.update_task(user_id,task_id, updated_data, db_session)
    return res.create_response(
        HttpStatusCodes.StatusCodesDescription.SUCCESS_OK_200,
        HttpStatusCodes.StatusCodes.SUCCESS_OK_200,
        result
    )

@router.post("/edit/{task_id}/", dependencies=[Depends(JWTBearer())])
async def update_task(
    task_id: int,
    request: Request,
    db_session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Dynamically update a single task column (e.g., `status`, `assigned_to`, `due_date`).
    Request body must be a JSON with exactly one key-value pair.
    """

    body = await request.json()

    if len(body) != 1:
        return res.create_response(
            HttpStatusCodes.StatusCodesDescription.BAD_REQUEST_400,
            HttpStatusCodes.StatusCodes.BAD_REQUEST_400,
            {"error": "Provide exactly one field to update"},
        )

    column, value = next(iter(body.items()))
    user_id = current_user["user_id"]

    result = task_service.update_task_column(user_id, task_id, column, value, db_session)

    return res.create_response(
        HttpStatusCodes.StatusCodesDescription.SUCCESS_OK_200,
        HttpStatusCodes.StatusCodes.SUCCESS_OK_200,
        result,
    )

# ------------------ UPDATE TASK STATUS (for assigned user) ------------------
@router.patch("/{task_id}/status", dependencies=[Depends(JWTBearer())])
async def update_task_status(task_id: int, status_data: UpdateTaskStatus, db_session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    updated_data = {"status": status_data.status, "updated_by": current_user["user_id"]}
    result = task_service.update_task(task_id, updated_data, db_session)
    return res.create_response(
        HttpStatusCodes.StatusCodesDescription.SUCCESS_OK_200,
        HttpStatusCodes.StatusCodes.SUCCESS_OK_200,
        result
    )

# ------------------ DELETE TASK ------------------
@router.delete("/{task_id}", dependencies=[Depends(JWTBearer())])
async def delete_task(task_id: int, db_session: Session = Depends(get_session)):
    result = task_service.delete_task(task_id, db_session)
    return res.create_response(
        HttpStatusCodes.StatusCodesDescription.SUCCESS_OK_200,
        HttpStatusCodes.StatusCodes.SUCCESS_OK_200,
        result
    )
