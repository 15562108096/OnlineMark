import os
b = r"D:\Desktop\Gaston Studio\services\OnlineMark"
print("Phase 1: Backend model upgrades")

# 1. Template model: multi-page + PDF + page_number
path = os.path.join(b, "backend", "app", "models", "template.py")
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

old = "    image_path = Column(String(500), nullable=False)"
new = "    image_path = Column(String(500), nullable=False)\n    pdf_path = Column(String(500), nullable=True)\n    total_pages = Column(Integer, default=1)"
c = c.replace(old, new)
print("  Template: added pdf_path, total_pages")

old = '    return {\"id\": self.id, \"name\": self.name,\n            \"description\": self.description,\n            \"subject\": self.subject,\n            \"grade\": self.grade,\n            \"exam_name\": self.exam_name,\n            \"image_path\": self.image_path,\n            \"image_width\": self.image_width,\n            \"image_height\": self.image_height,'
new = '    return {\"id\": self.id, \"name\": self.name,\n            \"description\": self.description,\n            \"subject\": self.subject,\n            \"grade\": self.grade,\n            \"exam_name\": self.exam_name,\n            \"image_path\": self.image_path,\n            \"pdf_path\": self.pdf_path,\n            \"total_pages\": self.total_pages,\n            \"image_width\": self.image_width,\n            \"image_height\": self.image_height,'
c = c.replace(old, new)
print("  Template: updated to_dict")

old = '    label = Column(String(50), nullable=True)\n    width = Column(Float, default=0.0)'
new = '    label = Column(String(50), nullable=True)\n    page_number = Column(Integer, default=0)\n    width = Column(Float, default=0.0)'
c = c.replace(old, new)
print("  TemplateMarker: added page_number")

old = 'return {\"id\": self.id, \"point_index\": self.point_index, \"x\": self.x, \"y\": self.y, \"width\": self.width, \"height\": self.height, \"shape\": self.shape, \"label\": self.label, \"page_number\": self.page_number}'
if old in c:
    pass  # already updated
old2 = 'return {\"id\": self.id, \"point_index\": self.point_index, \"x\": self.x, \"y\": self.y, \"width\": self.width, \"height\": self.height, \"shape\": self.shape, \"label\": self.label}'
new2 = 'return {\"id\": self.id, \"point_index\": self.point_index, \"x\": self.x, \"y\": self.y, \"width\": self.width, \"height\": self.height, \"shape\": self.shape, \"label\": self.label, \"page_number\": self.page_number}'
c = c.replace(old2, new2)
print("  TemplateMarker: updated to_dict")

old = "    sort_order = Column(Integer, default=0)\n    config = Column(JSON, nullable=True)"
new = "    sort_order = Column(Integer, default=0)\n    page_number = Column(Integer, default=0)\n    config = Column(JSON, nullable=True)"
c = c.replace(old, new)
print("  TemplateZone: added page_number")

old = '"height": self.height, "sort_order": self.sort_order, "page_number": self.page_number, "config": self.config'
if old in c:
    pass  # already updated
old2 = '"height": self.height, "sort_order": self.sort_order, "config": self.config'
new2 = '"height": self.height, "sort_order": self.sort_order, "page_number": self.page_number, "config": self.config'
c = c.replace(old2, new2)
print("  TemplateZone: updated to_dict")

old = "    correct_answer = Column(String(50), nullable=True)  # e.g., \"A\" or \"AB\"\n    answer_positions = Column(JSON, nullable=True)  # click-to-mark positions"
new = "    correct_answer = Column(String(50), nullable=True)\n    page_number = Column(Integer, default=0)\n    answer_positions = Column(JSON, nullable=True)"
c = c.replace(old, new)
print("  ObjectiveQuestion: added page_number")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

# 2. Scan model
path = os.path.join(b, "backend", "app", "models", "scan.py")
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

old = "    total_sheets = Column(Integer, default=0)"
new = "    total_sheets = Column(Integer, default=0)\n    upload_order = Column(String(20), default=\"sequential\")"
c = c.replace(old, new)
print("  ScanBatch: added upload_order")

old = "    error_message = Column(Text, nullable=True)"
new = "    error_message = Column(Text, nullable=True)\n    page_number = Column(Integer, default=1)\n    side = Column(String(20), default=\"front\")"
c = c.replace(old, new)
print("  ScannedSheet: added page_number, side")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

# 3. Schemas
path = os.path.join(b, "backend", "app", "schemas", "template.py")
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

old = "class MarkerRequest(BaseModel):\n    point_index: int\n    x: float\n    y: float\n    width: Optional[float] = 0.0\n    height: Optional[float] = 0.0\n    shape: Optional[str] = \"circle\"\n    label: Optional[str] = None"
new = "class MarkerRequest(BaseModel):\n    point_index: int\n    x: float\n    y: float\n    width: Optional[float] = 0.0\n    height: Optional[float] = 0.0\n    shape: Optional[str] = \"circle\"\n    label: Optional[str] = None\n    page_number: Optional[int] = 0"
c = c.replace(old, new)
print("  MarkerRequest: added page_number")

old = "class TemplateCreate(BaseModel):\n    name: str\n    description: Optional[str] = None\n    subject: Optional[str] = None\n    grade: Optional[str] = None\n    exam_name: Optional[str] = None\n    info_method: str = \"omr\"\n    markers: List[MarkerRequest] = []\n    zones: List[ZoneRequest] = []\n    questions: List[QuestionRequest] = []"
new = "class TemplateCreate(BaseModel):\n    name: str\n    description: Optional[str] = None\n    subject: Optional[str] = None\n    grade: Optional[str] = None\n    exam_name: Optional[str] = None\n    info_method: str = \"omr\"\n    total_pages: Optional[int] = 1\n    pdf_path: Optional[str] = None\n    markers: List[MarkerRequest] = []\n    zones: List[ZoneRequest] = []\n    questions: List[QuestionRequest] = []"
c = c.replace(old, new)
print("  TemplateCreate: added total_pages, pdf_path")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("\nPhase 1 complete: Backend models upgraded")
