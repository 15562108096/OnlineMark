from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ScanBatchCreate(BaseModel):
    name: str
    template_id: str
    exam_name: Optional[str] = None

class RecognitionConfig(BaseModel):
    template_id: str
    batch_id: Optional[str] = None
    sheet_ids: Optional[List[str]] = None
