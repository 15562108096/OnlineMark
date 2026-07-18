import os
base = r"D:\Desktop\Gaston Studio\services\OnlineMark"
changes = []

# 1. Fix template schema - add answer_positions to QuestionRequest
path = os.path.join(base, "backend", "app", "schemas", "template.py")
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

old = "    correct_answer: Optional[str] = None\n    x: Optional[float] = None\n    y: Optional[float] = None\n    width: Optional[float] = None\n    height: Optional[float] = None\n    sort_order: Optional[int] = 0"
new = "    correct_answer: Optional[str] = None\n    answer_positions: Optional[list] = None\n    x: Optional[float] = None\n    y: Optional[float] = None\n    width: Optional[float] = None\n    height: Optional[float] = None\n    sort_order: Optional[int] = 0"
c = c.replace(old, new)
with open(path, "w", encoding="utf-8") as f:
    f.write(c)
changes.append("Schema QuestionRequest: added answer_positions")

# 2. Fix templates router - store answer_positions when creating questions
path = os.path.join(base, "backend", "app", "routers", "templates.py")
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Update create_template to pass answer_positions to ObjectiveQuestion
old_obj = '    for q in req.questions:\n        obj_q = ObjectiveQuestion(\n            template_id=temp.id, question_number=q.question_number,\n            question_type=q.question_type, options_count=q.options_count,\n            options=q.options or ["A","B","C","D"][:q.options_count],\n            option_layout=q.option_layout, score=q.score,\n            x=q.x, y=q.y, width=q.width, height=q.height,\n            correct_answer=q.correct_answer, sort_order=q.sort_order\n        )'
new_obj = '    for q in req.questions:\n        obj_q = ObjectiveQuestion(\n            template_id=temp.id, question_number=q.question_number,\n            question_type=q.question_type, options_count=q.options_count,\n            options=q.options or ["A","B","C","D"][:q.options_count],\n            option_layout=q.option_layout, score=q.score,\n            x=q.x, y=q.y, width=q.width, height=q.height,\n            correct_answer=q.correct_answer, sort_order=q.sort_order,\n            answer_positions=q.answer_positions\n        )'
c = c.replace(old_obj, new_obj)
changes.append("Templates router: create passes answer_positions")

# Also add marker shape fields and zone config
old_marker = '        marker = TemplateMarker(\n            template_id=temp.id, point_index=m.point_index,\n            x=m.x, y=m.y, label=m.label\n        )'
new_marker = '        marker = TemplateMarker(\n            template_id=temp.id, point_index=m.point_index,\n            x=m.x, y=m.y, width=m.width or 0, height=m.height or 0,\n            shape=m.shape or "circle", label=m.label\n        )'
c = c.replace(old_marker, new_marker)
changes.append("Templates router: marker shape fields")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

# 3. Update template update function to handle new fields
# Also add zone config support in the create router
old_zone_create = '        zone = TemplateZone(\n            template_id=temp.id, zone_type=z.zone_type, label=z.label,\n            x=z.x, y=z.y, width=z.width, height=z.height, sort_order=z.sort_order\n        )'
new_zone_create = '        zone = TemplateZone(\n            template_id=temp.id, zone_type=z.zone_type, label=z.label,\n            x=z.x, y=z.y, width=z.width, height=z.height, sort_order=z.sort_order,\n            config=z.config\n        )'
c = c.replace(old_zone_create, new_zone_create)
changes.append("Templates router: zone config support")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

for ch in changes:
    print(f"  {ch}")
print(f"Total: {len(changes)} backend fixes")
