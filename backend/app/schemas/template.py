from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MarkerRequest(BaseModel):
    point_index: int
    x: float
    y: float
    label: Optional[str] = None

class ZoneRequest(BaseModel):
    zone_type: str
    label: Optional[str] = None
    x: float
    y: float
    width: float
    height: float
    sort_order: Optional[int] = 0

class QuestionRequest(BaseModel):
    question_number: int
    question_type: str = "single"
    options_count: int = 4
    options: Optional[list] = None
    option_layout: str = "vertical"
    score: float = 1.0
    correct_answer: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    sort_order: Optional[int] = 0

class TemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    subject: Optional[str] = None
    grade: Optional[str] = None
    exam_name: Optional[str] = None
    info_method: str = "omr"
    markers: List[MarkerRequest] = []
    zones: List[ZoneRequest] = []
    questions: List[QuestionRequest] = []

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    subject: Optional[str] = None
    grade: Optional[str] = None
    exam_name: Optional[str] = None
    info_method: Optional[str] = None
    status: Optional[str] = None
    total_score: Optional[float] = None
    objective_score: Optional[float] = None
    subjective_score: Optional[float] = None
    markers: Optional[List[MarkerRequest]] = None
    zones: Optional[List[ZoneRequest]] = None
    questions: Optional[List[QuestionRequest]] = None
