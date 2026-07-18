# -*- coding: utf-8 -*-
"""数据库连接配置"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import os

DB_TYPE = settings.DB_TYPE.lower()

if settings.PHP_API_ENABLED:
    # PHP桥接模式：使用SQLite内存引擎作为SQLAlchemy的占位
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
else:
    # 直连模式
    if DB_TYPE == "mysql":
        engine = create_engine(settings.DATABASE_URL, pool_size=10, max_overflow=20, pool_pre_ping=True)
    else:
        engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

import sqlalchemy as sa
from sqlalchemy import text

def run_migrations(engine):
    """Add new columns to existing tables"""
    if settings.PHP_API_ENABLED:
        # 桥接模式下跳过SQLite内存表的迁移
        return
    migs = [
        ("templates", "total_pages", "ALTER TABLE templates ADD COLUMN total_pages INTEGER DEFAULT 1"),
        ("templates", "pdf_path", "ALTER TABLE templates ADD COLUMN pdf_path VARCHAR(500)"),
        ("template_markers", "page_number", "ALTER TABLE template_markers ADD COLUMN page_number INTEGER DEFAULT 0"),
        ("template_zones", "page_number", "ALTER TABLE template_zones ADD COLUMN page_number INTEGER DEFAULT 0"),
        ("objective_questions", "page_number", "ALTER TABLE objective_questions ADD COLUMN page_number INTEGER DEFAULT 0"),
        ("scan_batches", "upload_order", "ALTER TABLE scan_batches ADD COLUMN upload_order VARCHAR(20) DEFAULT 'sequential'"),
        ("scanned_sheets", "page_number", "ALTER TABLE scanned_sheets ADD COLUMN page_number INTEGER DEFAULT 1"),
        ("scanned_sheets", "side", "ALTER TABLE scanned_sheets ADD COLUMN side VARCHAR(20) DEFAULT 'front'"),
        ("objective_questions", "answer_positions", "ALTER TABLE objective_questions ADD COLUMN answer_positions JSON"),
        ("template_zones", "answer_positions", "ALTER TABLE template_zones ADD COLUMN answer_positions JSON"),
    ]
    for table, column, sql in migs:
        try:
            with engine.connect() as conn:
                conn.execute(text(sql))
                conn.commit()
        except Exception:
            pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    if not settings.PHP_API_ENABLED:
        Base.metadata.create_all(bind=engine)
