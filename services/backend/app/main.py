"""
Starting point of the application
"""
from logging.config import fileConfig
from os import path
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.models.tables_model import create_tables
from app.api.v1 import auth_user_api, projects_api, tasks_api, login_api
from app.core.config import settings

print("🚀 BACKEND_CORS_ORIGINS:", settings.BACKEND_CORS_ORIGINS)


def get_application():
    """
    Setup FastAPI application
    """
    _app = FastAPI(title=settings.PROJECT_NAME)

    # GZip middleware
    _app.add_middleware(GZipMiddleware, minimum_size=1000)

    # CORS middleware
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).rstrip('/') for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return _app


app = get_application()

# Create all tables in the database
create_tables()

# ---------------------------
# Include API routers (all under /api)
# ---------------------------
app.include_router(tasks_api.router, prefix="/api", tags=["Tasks"])
app.include_router(auth_user_api.router, prefix="/api", tags=["UserApi"])
app.include_router(projects_api.router, prefix="/api", tags=["Projects"])
app.include_router(login_api.router, prefix="/api", tags=["Login"])


# ---------------------------
# Serve React frontend (build folder)
# ---------------------------
BASE_DIR = Path(__file__).resolve().parent  # backend/app/
BUILD_DIR = BASE_DIR / "build"  # backend/app/build

if BUILD_DIR.exists():
    # Serve static files (CSS/JS/images)
    app.mount("/static", StaticFiles(directory=BUILD_DIR / "static"), name="static")

    # Catch-all route for React (non-API routes)
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        # 🚨 Ignore all /api paths so they return proper FastAPI error JSON
        if full_path.startswith("api"):
            return FileResponse("404.html") if (BUILD_DIR / "404.html").exists() else {"detail": "Not Found"}

        index_path = BUILD_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"detail": "Not Found"}



# ---------------------------
# Logging
# ---------------------------
log_file_path = path.join(path.dirname(path.abspath(__file__)), "logging.conf")
fileConfig(log_file_path, disable_existing_loggers=False)
