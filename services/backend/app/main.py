"""
Starting point of the application
"""
from logging.config import fileConfig
from os import path, environ
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.v1 import auth_user_api, projects_api, tasks_api, login_api
from app.core.config import settings

# ---------------------------
# DEBUG: Print all config variables
# ---------------------------
print("======= Loaded Configuration =======")
for key, value in settings.model_dump().items():
    # Mask sensitive info like passwords
    if "password" in key.lower():
        value = "*****"
    print(f"{key} = {value}")
print("===================================")

# ---------------------------
# Setup FastAPI app
# ---------------------------
def get_application():
    _app = FastAPI(title=settings.PROJECT_NAME)

    # GZip middleware
    _app.add_middleware(GZipMiddleware, minimum_size=1000)

    # CORS middleware
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return _app


app = get_application()

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

# DEBUG: check build folder
print("BUILD_DIR path:", BUILD_DIR)
print("Does BUILD_DIR exist?", BUILD_DIR.exists())
if BUILD_DIR.exists():
    print("Contents of BUILD_DIR:", [f.name for f in BUILD_DIR.iterdir()])

    # Serve static files
    static_dir = BUILD_DIR / "static"
    if static_dir.exists():
        print("Serving static files from:", static_dir)
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    else:
        print("WARNING: Static folder not found in build!")

    # Catch-all route for React frontend
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        # Ignore API paths
        if "api" in full_path:
            return {"detail": "Not Found"}

        index_path = BUILD_DIR / "index.html"
        print("Requested path:", full_path)
        print("Serving index.html from:", index_path)
        if index_path.exists():
            return FileResponse(index_path)
        else:
            print("ERROR: index.html not found!")
            return {"detail": "Not Found"}
else:
    print("ERROR: BUILD_DIR not found. React frontend will not render.")

# ---------------------------
# Explicit favicon route
# ---------------------------
favicon_path = BUILD_DIR / "favicon.ico"
if favicon_path.exists():
    @app.get("/favicon.ico")
    async def favicon():
        return FileResponse(favicon_path)
else:
    print("WARNING: favicon.ico not found in build folder")

# ---------------------------
# Logging
# ---------------------------
log_file_path = path.join(path.dirname(path.abspath(__file__)), "logging.conf")
fileConfig(log_file_path, disable_existing_loggers=False)

# ---------------------------
# Debug: Print Azure PORT if set
# ---------------------------
print("PORT environment variable:", environ.get("PORT", "not set"))
