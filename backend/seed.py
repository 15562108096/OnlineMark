# -*- coding: utf-8 -*-
"""初始化数据库 - 创建超级管理员账号"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db, SessionLocal, engine, Base
import app.models
from app.models.user import User, UserRole
from app.utils.auth import hash_password
import uuid

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "37108220071109031X")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Zyw20071109")
ADMIN_REAL_NAME = os.getenv("ADMIN_REAL_NAME", "超级管理员")

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == ADMIN_USERNAME).first()
        if existing:
            print("超级管理员账号已存在，跳过创建")
            return

        admin = User(
            id=str(uuid.uuid4()),
            username=ADMIN_USERNAME,
            password_hash=hash_password(ADMIN_PASSWORD),
            real_name=ADMIN_REAL_NAME,
            role=UserRole.SUPER_ADMIN,
            is_active=True
        )
        db.add(admin)
        db.commit()
        print("超级管理员账号创建成功！")
        print(f"账号: {ADMIN_USERNAME}")
        print(f"密码: {ADMIN_PASSWORD}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
