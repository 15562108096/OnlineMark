from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class LoginRequest(BaseModel):
    username: str
    password: str
    role: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class UserCreate(BaseModel):
    username: str
    password: str
    real_name: Optional[str] = None
    role: str = "student"
    email: Optional[str] = None
    phone: Optional[str] = None

class UserUpdate(BaseModel):
    real_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: str
    username: str
    real_name: Optional[str] = None
    role: str
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool
    created_at: Optional[str] = None
    created_by: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
