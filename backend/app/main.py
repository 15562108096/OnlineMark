# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import app.models
from app.config import settings
from app.database import init_db, engine, Base

# 创建所有表
Base.metadata.create_all(bind=engine)

from app.routers import auth, users, templates, scan, grading, scores

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件路由
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# 注册路由
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(templates.router)
app.include_router(scan.router)
app.include_router(grading.router)
app.include_router(scores.router)

@app.get("/")
def root():
    return {"name": settings.APP_NAME, "version": settings.APP_VERSION, "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
