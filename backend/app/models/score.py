import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, ForeignKey
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from app.database import Base

class ExamScore(Base):
    __tablename__ = "exam_scores"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(CHAR(36), ForeignKey("scan_batches.id"), nullable=False)
    sheet_id = Column(CHAR(36), ForeignKey("scanned_sheets.id"), nullable=False)
    student_id = Column(String(100), nullable=True)
    student_name = Column(String(100), nullable=True)
    objective_score = Column(Float, default=0.0)
    subjective_score = Column(Float, default=0.0)
    total_score = Column(Float, default=0.0)
    full_score = Column(Float, default=0.0)
    rank = Column(String(20), nullable=True)
    details = Column(String(5000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
