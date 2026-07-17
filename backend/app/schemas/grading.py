from pydantic import BaseModel
from typing import Optional, List

class GradingTaskCreate(BaseModel):
    name: str
    batch_id: str
    template_id: str
    threshold: float = 5.0

class GradingAssignRequest(BaseModel):
    task_id: str
    teacher_id: str
    question_numbers: List[int]

class GradeSubmit(BaseModel):
    assignment_id: str
    sheet_id: str
    subjective_image_id: Optional[str] = None
    question_number: int
    score: float
    comment: Optional[str] = None
    grading_round: int = 1
