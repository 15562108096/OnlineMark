# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import app.models
from app.config import settings
from app.database import init_db, engine, Base, run_migrations

Base.metadata.create_all(bind=engine)
run_migrations(engine)

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ─── Route Registration ─────────────────────────────────
# Strategy:
#   PHP_API_ENABLED=True  → DB routes go through PHP proxy on InfinityFree
#   PHP_API_ENABLED=False → DB routes use direct SQLAlchemy (local dev)

if settings.PHP_API_ENABLED:
    # Production: DB via PHP bridge on InfinityFree
    from app.routers.php_proxy import router as php_router
    app.include_router(php_router)
    # Python-only routes (upload, recognition, grading)
    from app.routers.scan import router as scan_router
    app.include_router(scan_router)
    from app.routers.grading import router as grading_router
    app.include_router(grading_router)
else:
    # Local dev: direct SQLAlchemy
    from app.routers import auth, users, templates, scan, grading, scores
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(templates.router)
    app.include_router(scan.router)
    app.include_router(grading.router)
    app.include_router(scores.router)

# ─── Frontend static files (SPA) ────────────────────────
FRONTEND_DIST = os.environ.get("FRONTEND_DIST", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist"))
if os.path.isdir(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="frontend_assets")
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        if full_path.startswith(("api/", "uploads/", "health")):
            from fastapi.responses import JSONResponse
            return JSONResponse({"detail": "Not Found"}, status_code=404)
        index_path = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path, media_type="text/html")
        return JSONResponse({"detail": "Not Found"}, status_code=404)

@app.get("/")
def root():
    return {"name": settings.APP_NAME, "version": settings.APP_VERSION, "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
