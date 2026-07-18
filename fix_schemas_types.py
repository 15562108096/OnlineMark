import os
base = r'D:\Desktop\Gaston Studio\services\OnlineMark'

# 2. Fix template schemas
path = os.path.join(base, 'backend', 'app', 'schemas', 'template.py')
with open(path, 'r', encoding='utf-8') as f:
    data = f.read()

# Add shape/w/h to MarkerRequest
old = 'class MarkerRequest(BaseModel):\n    point_index: int\n    x: float\n    y: float\n    label: Optional[str] = None'
new = 'class MarkerRequest(BaseModel):\n    point_index: int\n    x: float\n    y: float\n    width: Optional[float] = 0.0\n    height: Optional[float] = 0.0\n    shape: Optional[str] = "circle"\n    label: Optional[str] = None'
data = data.replace(old, new)

with open(path, 'w', encoding='utf-8') as f:
    f.write(data)
print('2. Template schemas updated OK')

# 3. Fix frontend types
path = os.path.join(base, 'frontend', 'src', 'types', 'index.ts')
with open(path, 'r', encoding='utf-8') as f:
    data = f.read()

# Update Marker type
old = 'export interface Marker {\n  point_index: number;\n  x: number;\n  y: number;\n  label?: string;\n}'
new = 'export interface Marker {\n  point_index: number;\n  x: number;\n  y: number;\n  width?: number;\n  height?: number;\n  shape?: string;\n  label?: string;\n}'
data = data.replace(old, new)

# Update Zone type with config
old = 'export interface Zone {\n  id?: string;\n  zone_type: "student_info" | "objective" | "subjective";\n  label?: string;\n  x: number;\n  y: number;\n  width: number;\n  height: number;\n  sort_order?: number;\n}'
new = 'export interface Zone {\n  id?: string;\n  zone_type: "student_info" | "objective" | "subjective";\n  label?: string;\n  x: number;\n  y: number;\n  width: number;\n  height: number;\n  sort_order?: number;\n  config?: any;\n}'
data = data.replace(old, new)

# Update Question type with answer_positions
old = 'export interface Question {\n  id?: string;\n  question_number: number;\n  question_type: "single" | "multiple" | "judge";\n  options_count: number;\n  options?: string[];\n  option_layout: "horizontal" | "vertical";\n  score: number;\n  correct_answer?: string;\n  x?: number;\n  y?: number;\n  width?: number;\n  height?: number;\n  sort_order?: number;\n}'
new = 'export interface Question {\n  id?: string;\n  question_number: number;\n  question_type: "single" | "multiple" | "judge";\n  options_count: number;\n  options?: string[];\n  option_layout: "horizontal" | "vertical";\n  score: number;\n  correct_answer?: string;\n  x?: number;\n  y?: number;\n  width?: number;\n  height?: number;\n  sort_order?: number;\n  answer_positions?: AnswerPosition[];\n}\n\nexport interface AnswerPosition {\n  question_number: number;\n  option: string;\n  x: number;\n  y: number;\n  width?: number;\n  height?: number;\n  is_correct?: boolean;\n}'
data = data.replace(old, new)

with open(path, 'w', encoding='utf-8') as f:
    f.write(data)
print('3. Frontend types updated OK')
