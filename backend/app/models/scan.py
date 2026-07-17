import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Enum, Boolean, Integer, Float, JSON, ForeignKey
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class RecognitionStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ScanBatch(Base):
    __tablename__ = "scan_batches"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    template_id = Column(CHAR(36), ForeignKey("templates.id"), nullable=False)
    exam_name = Column(String(200), nullable=True)
    total_sheets = Column(Integer, default=0)
    processed_sheets = Column(Integer, default=0)
    status = Column(String(20), default="pending")
    created_by = Column(CHAR(36), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sheets = relationship("ScannedSheet", back_populates="batch", cascade="all, delete-orphan")

class ScannedSheet(Base):
    __tablename__ = "scanned_sheets"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(CHAR(36), ForeignKey("scan_batches.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(500), nullable=False)
    file_path = Column(String(500), nullable=False)
    student_id = Column(String(100), nullable=True)
    student_name = Column(String(100), nullable=True)
    status = Column(Enum(RecognitionStatus), default=RecognitionStatus.PENDING)
    error_message = Column(Text, nullable=True)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    batch = relationship("ScanBatch", back_populates="sheets")
    recognition_results = relationship("RecognitionResult", back_populates="sheet", cascade="all, delete-orphan")
    subjective_images = relationship("SubjectiveImage", back_populates="sheet", cascade="all, delete-orphan")

class RecognitionResult(Base):
    __tablename__ = "recognition_results"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sheet_id = Column(CHAR(36), ForeignKey("scanned_sheets.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(CHAR(36), nullable=True)
    question_number = Column(Integer, nullable=False)
    question_type = Column(String(20), nullable=False)
    detected_answer = Column(String(50), nullable=True)
    correct_answer = Column(String(50), nullable=True)
    is_correct = Column(Boolean, nullable=True)
    score = Column(Float, default=0.0)
    max_score = Column(Float, default=0.0)
    confidence = Column(Float, nullable=True)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    sheet = relationship("ScannedSheet", back_populates="recognition_results")

class SubjectiveImage(Base):
    __tablename__ = "subjective_images"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sheet_id = Column(CHAR(36), ForeignKey("scanned_sheets.id", ondelete="CASCADE"), nullable=False)
    question_number = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    score = Column(Float, nullable=True)
    max_score = Column(Float, nullable=True)
    graded = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    sheet = relationship("ScannedSheet", back_populates="subjective_images")
