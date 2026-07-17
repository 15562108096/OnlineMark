# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.utils.auth import hash_password, get_current_user, require_role
from app.schemas.user import UserCreate, UserResponse
from typing import List
import uuid

router = APIRouter(prefix="/api/users", tags=["用户管理"])

@router.get("/", response_model=List[UserResponse])
def list_users(role: str = None, db: Session = Depends(get_db),
               current_user: User = Depends(require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN))):
    query = db.query(User)
    if role:
        query = query.filter(User.role == UserRole(role))
    return [u.to_dict() for u in query.all()]

@router.post("/", response_model=dict)
def create_user(req: UserCreate, db: Session = Depends(get_db),
                current_user: User = Depends(require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN))):
    if current_user.role == UserRole.ADMIN and req.role in ("super_admin", "admin"):
        raise HTTPException(status_code=403, detail="管理员不能创建管理员或超级管理员账号")
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(
        username=req.username,
        password_hash=hash_password(req.password),
        real_name=req.real_name,
        role=UserRole(req.role),
        email=req.email,
        phone=req.phone,
        created_by=current_user.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "创建成功", "user": user.to_dict()}

@router.delete("/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db),
                current_user: User = Depends(require_role(UserRole.SUPER_ADMIN))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=400, detail="不能删除超级管理员")
    db.delete(user)
    db.commit()
    return {"message": "删除成功"}

@router.put("/{user_id}/toggle-active")
def toggle_active(user_id: str, db: Session = Depends(get_db),
                  current_user: User = Depends(require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=400, detail="不能操作超级管理员")
    user.is_active = not user.is_active
    db.commit()
    return {"message": "状态已更新", "is_active": user.is_active}

@router.get("/teachers", response_model=List[UserResponse])
def list_teachers(db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    teachers = db.query(User).filter(User.role == UserRole.TEACHER, User.is_active == True).all()
    return [t.to_dict() for t in teachers]
