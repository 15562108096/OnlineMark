import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Enum, Boolean, Integer, Float, JSON, ForeignKey
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class ZoneType(str, enum.Enum):
    STUDENT_INFO = "student_info"
    OBJECTIVE = "objective"
    SUBJECTIVE = "subjective"

class QuestionType(str, enum.Enum):
    SINGLE_CHOICE = "single"
    MULTIPLE_CHOICE = "multiple"
    TRUE_FALSE = "judge"

class OMRMethod(str, enum.Enum):
    OMR = "omr"
    BARCODE = "barcode"

class OptionLayout(str, enum.Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"

class Template(Base):
    __tablename__ = "templates"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    subject = Column(String(100), nullable=True)
    grade = Column(String(50), nullable=True)
    exam_name = Column(String(200), nullable=True)
    image_path = Column(String(500), nullable=True, default="")
    pdf_path = Column(String(500), nullable=True)
    total_pages = Column(Integer, default=1)
    image_width = Column(Integer, nullable=True)
    image_height = Column(Integer, nullable=True)
    total_score = Column(Float, default=0.0)
    objective_score = Column(Float, default=0.0)
    subjective_score = Column(Float, default=0.0)
    info_method = Column(Enum(OMRMethod), default=OMRMethod.OMR)
    status = Column(String(20), default="draft")
    created_by = Column(CHAR(36), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    markers = relationship("TemplateMarker", back_populates="template", cascade="all, delete-orphan")
    zones = relationship("TemplateZone", back_populates="template", cascade="all, delete-orphan")
    questions = relationship("ObjectiveQuestion", back_populates="template", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "subject": self.subject,
            "grade": self.grade,
            "exam_name": self.exam_name,
            "image_path": self.image_path,
            "image_width": self.image_width,
            "image_height": self.image_height,
            "total_score": self.total_score,
            "objective_score": self.objective_score,
            "subjective_score": self.subjective_score,
            "info_method": self.info_method.value if self.info_method else "omr",
            "status": self.status,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "markers": [m.to_dict() for m in self.markers] if self.markers else [],
            "zones": [z.to_dict() for z in self.zones] if self.zones else [],
            "questions": [q.to_dict() for q in self.questions] if self.questions else []
        }

class TemplateMarker(Base):
    __tablename__ = "template_markers"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    template_id = Column(CHAR(36), ForeignKey("templates.id", ondelete="CASCADE"), nullable=False)
    point_index = Column(Integer, nullable=False)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    label = Column(String(50), nullable=True)
    page_number = Column(Integer, default=0)
    width = Column(Float, default=0.0)
    height = Column(Float, default=0.0)
    shape = Column(String(20), default="circle")

    template = relationship("Template", back_populates="markers")

    def to_dict(self):
        return {"id": self.id, "point_index": self.point_index, "x": self.x, "y": self.y, "width": self.width, "height": self.height, "shape": self.shape, "label": self.label, "page_number": self.page_number}

class TemplateZone(Base):
    __tablename__ = "template_zones"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    template_id = Column(CHAR(36), ForeignKey("templates.id", ondelete="CASCADE"), nullable=False)
    zone_type = Column(Enum(ZoneType), nullable=False)
    label = Column(String(200), nullable=True)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    width = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    sort_order = Column(Integer, default=0)
    answer_positions = Column(JSON, nullable=True)
    page_number = Column(Integer, default=0)
    config = Column(JSON, nullable=True)

    template = relationship("Template", back_populates="zones")

    def to_dict(self):
        return {
            "id": self.id, "zone_type": self.zone_type.value if self.zone_type else None,
            "label": self.label, "x": self.x, "y": self.y,
            "width": self.width, "height": self.height, "sort_order": self.sort_order, "page_number": self.page_number, "config": self.config
        }

class ObjectiveQuestion(Base):
    __tablename__ = "objective_questions"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    template_id = Column(CHAR(36), ForeignKey("templates.id", ondelete="CASCADE"), nullable=False)
    zone_id = Column(CHAR(36), ForeignKey("template_zones.id", ondelete="CASCADE"), nullable=True)
    question_number = Column(Integer, nullable=False)
    question_type = Column(Enum(QuestionType), nullable=False, default=QuestionType.SINGLE_CHOICE)
    options_count = Column(Integer, default=4)
    options = Column(JSON, nullable=True)
    option_layout = Column(Enum(OptionLayout), default=OptionLayout.VERTICAL)
    score = Column(Float, default=1.0)
    x = Column(Float, nullable=True)
    y = Column(Float, nullable=True)
    width = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    correct_answer = Column(String(50), nullable=True)
    answer_positions = Column(JSON, nullable=True)
    sort_order = Column(Integer, default=0)

    template = relationship("Template", back_populates="questions")

    def to_dict(self):
        return {
            "id": self.id, "zone_id": self.zone_id,
            "question_number": self.question_number,
            "question_type": self.question_type.value if self.question_type else None,
            "options_count": self.options_count, "options": self.options,
            "option_layout": self.option_layout.value if self.option_layout else None,
            "score": self.score, "x": self.x, "y": self.y,
            "width": self.width, "height": self.height,
            "correct_answer": self.correct_answer, "answer_positions": getattr(self, 'answer_positions', None), "sort_order": self.sort_order
        }

class CorrectAnswer(Base):
    __tablename__ = "correct_answers"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    template_id = Column(CHAR(36), ForeignKey("templates.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(CHAR(36), ForeignKey("objective_questions.id", ondelete="CASCADE"), nullable=True)
    question_number = Column(Integer, nullable=False)
    answer = Column(String(50), nullable=False)
    score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
