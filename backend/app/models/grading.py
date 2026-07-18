import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Enum, Boolean, Integer, Float, ForeignKey
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class GradingTask(Base):
    __tablename__ = "grading_tasks"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    batch_id = Column(CHAR(36), ForeignKey("scan_batches.id"), nullable=False)
    template_id = Column(CHAR(36), ForeignKey("templates.id"), nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    total_subjective = Column(Integer, default=0)
    graded_count = Column(Integer, default=0)
    threshold = Column(Float, default=5.0)
    created_by = Column(CHAR(36), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assignments = relationship("GradingAssignment", back_populates="task", cascade="all, delete-orphan")

class GradingAssignment(Base):
    __tablename__ = "grading_assignments"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(CHAR(36), ForeignKey("grading_tasks.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    question_number = Column(Integer, nullable=False)
    question_type = Column(String(20), default="subjective")
    total_count = Column(Integer, default=0)
    graded_count = Column(Integer, default=0)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("GradingTask", back_populates="assignments")

class Grade(Base):
    __tablename__ = "grades"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assignment_id = Column(CHAR(36), ForeignKey("grading_assignments.id", ondelete="CASCADE"), nullable=False)
    sheet_id = Column(CHAR(36), ForeignKey("scanned_sheets.id"), nullable=False)
    subjective_image_id = Column(CHAR(36), ForeignKey("subjective_images.id"), nullable=True)
    question_number = Column(Integer, nullable=False)
    score = Column(Float, nullable=False)
    teacher_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    grading_round = Column(Integer, default=1)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
