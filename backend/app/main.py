"""
starting point of the application
"""
from logging.config import fileConfig
from os import path
from app.models.tables_model import create_tables
from app.api.v1 import auth
from fastapi import FastAPI
from starlette.responses import FileResponse, Response
from pathlib import Path
from fastapi.middleware.gzip import GZipMiddleware 
from fastapi.staticfiles import StaticFiles 
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import (auth_user_api, projects_api,
                        tasks_api, login_api,)


def get_application():
    """
    function to setup fastapi application
    """
    _app = FastAPI(
        title=settings.PROJECT_NAME
    )
    _app.add_middleware(GZipMiddleware, minimum_size=1000) 

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return _app


app = get_application()

#creates all tables in the database
create_tables()

# BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
# BUILD_DIR = BASE_DIR.parent / "frontend" / "build"  # task-tracker/frontend/build

# @app.get("/")
# def index():
#     return FileResponse(BUILD_DIR / "index.html")

# @app.exception_handler(404)
# async def exception_404_handler(request, exc):
#     return FileResponse(BUILD_DIR / "index.html")


app.include_router(tasks_api.router, prefix="/api",
    tags=['Tasks'])
app.include_router(auth_user_api.router, prefix="/api",tags=['UserApi'])
app.include_router(projects_api.router, prefix="/api",tags=['Projects'])

app.include_router(login_api.router, prefix='/api', tags=['Login'])
app.include_router(auth.router, prefix='', tags=['Login'])

# app.mount("/", StaticFiles(directory=BUILD_DIR), name="ui")  


log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logging.conf')
fileConfig(log_file_path, disable_existing_loggers=False)
