# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.utils.auth import hash_password, verify_password, create_access_token, get_current_user
from app.schemas.user import LoginRequest, TokenResponse, UserCreate, UserResponse, ChangePasswordRequest
from typing import List
from datetime import timedelta

router = APIRouter(prefix="/api/auth", tags=["认证"])

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="账号已被禁用")
    if user.role.value != req.role:
        raise HTTPException(status_code=401, detail=f"身份不匹配，该账号不是{req.role}身份")
    token = create_access_token({"sub": user.id, "role": user.role.value})
    return TokenResponse(access_token=token, user=user.to_dict())

@router.post("/register", response_model=dict)
def register(req: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    if req.role not in [r.value for r in UserRole]:
        raise HTTPException(status_code=400, detail="无效的角色类型")
    user = User(
        username=req.username,
        password_hash=hash_password(req.password),
        real_name=req.real_name,
        role=UserRole(req.role),
        email=req.email,
        phone=req.phone
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "注册成功", "user": user.to_dict()}

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user.to_dict()

@router.put("/password")
def change_password(req: ChangePasswordRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(req.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")
    current_user.password_hash = hash_password(req.new_password)
    db.commit()
    return {"message": "密码修改成功"}
