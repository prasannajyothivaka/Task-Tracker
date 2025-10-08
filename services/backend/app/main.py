"""
Starting point of the application
"""
import os
from pathlib import Path
from logging.config import fileConfig
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.api.v1 import auth_user_api, projects_api, tasks_api, login_api
from app.core.config import settings

# ---------------------------
# Setup Logging
# ---------------------------
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logging.conf")
if os.path.exists(log_file_path):
    fileConfig(log_file_path, disable_existing_loggers=False)
else:
    print("⚠️ Logging config file not found:", log_file_path)

# ---------------------------
# Debug Config Variables
# ---------------------------
print("======= Loaded Configuration =======")
for key, value in settings.model_dump().items():
    if "password" in key.lower():
        value = "*****"
    print(f"{key} = {value}")
print("===================================")

# ---------------------------
# FastAPI App Initialization
# ---------------------------
def get_application() -> FastAPI:
    _app = FastAPI(title=settings.PROJECT_NAME)

    # Compression
    _app.add_middleware(GZipMiddleware, minimum_size=1000)

    # CORS
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
# API Routers
# ---------------------------
app.include_router(tasks_api.router, prefix="/api", tags=["Tasks"])
app.include_router(auth_user_api.router, prefix="/api", tags=["UserApi"])
app.include_router(projects_api.router, prefix="/api", tags=["Projects"])
app.include_router(login_api.router, prefix="/api", tags=["Login"])


# ---------------------------
# Serve React Frontend
# ---------------------------
BASE_DIR = Path(__file__).resolve().parent  # backend/app/
BUILD_DIR = BASE_DIR / "build"              # backend/app/build

print(f"🔍 BUILD_DIR path: {BUILD_DIR}")
print(f"📦 Does BUILD_DIR exist? {BUILD_DIR.exists()}")

if BUILD_DIR.exists():
    print(f"📁 BUILD_DIR contents: {[f.name for f in BUILD_DIR.iterdir()]}")
    static_dir = BUILD_DIR / "static"
    if static_dir.exists():
        print(f"✅ Serving static files from: {static_dir}")
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    else:
        print("⚠️ WARNING: Static folder not found inside build!")

    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        if "api" in full_path or full_path.startswith("docs") or full_path.startswith("redoc") or full_path.startswith("openapi.json"):
            return JSONResponse({"detail": "API route not found"}, status_code=404)

        index_path = BUILD_DIR / "index.html"
        print(f"🌐 Request for: /{full_path}")
        print(f"➡️ Serving index.html from: {index_path}")
        if index_path.exists():
            return FileResponse(index_path)
        else:
            print("❌ ERROR: index.html not found in build folder!")
            return JSONResponse({"detail": "Frontend not found"}, status_code=404)
else:
    print("❌ ERROR: BUILD_DIR not found. React frontend not deployed or copied properly.")

# ---------------------------
# Explicit favicon route
# ---------------------------
favicon_path = BUILD_DIR / "favicon.ico"
if favicon_path.exists():
    @app.get("/favicon.ico")
    async def favicon():
        return FileResponse(favicon_path)
else:
    print("⚠️ WARNING: favicon.ico not found in build folder")


# ---------------------------
# Environment Debug Info
# ---------------------------
print("🌍 PORT environment variable:", os.environ.get("PORT", "not set"))
print("📂 Current working directory:", os.getcwd())
print("🧩 Current directory files:", os.listdir("."))
