import os
base = r'D:\Desktop\Gaston Studio\services\OnlineMark'

# Fix template model
path = os.path.join(base, 'backend', 'app', 'models', 'template.py')
with open(path, 'r', encoding='utf-8') as f:
    model = f.read()

# Add shape + w/h to TemplateMarker
old = 'label = Column(String(50), nullable=True)\n\n    template = relationship("Template", back_populates="markers")'
new = 'label = Column(String(50), nullable=True)\n    width = Column(Float, default=0.0)\n    height = Column(Float, default=0.0)\n    shape = Column(String(20), default="circle")\n\n    template = relationship("Template", back_populates="markers")'
model = model.replace(old, new)

# Add config to TemplateZone
old = 'sort_order = Column(Integer, default=0)\n\n    template = relationship("Template", back_populates="zones")'
new = 'sort_order = Column(Integer, default=0)\n    config = Column(JSON, nullable=True)\n\n    template = relationship("Template", back_populates="zones")'
model = model.replace(old, new)

# Update to_dict for TemplateMarker
model = model.replace(
    'return {"id": self.id, "point_index": self.point_index, "x": self.x, "y": self.y, "label": self.label}',
    'return {"id": self.id, "point_index": self.point_index, "x": self.x, "y": self.y, "width": self.width, "height": self.height, "shape": self.shape, "label": self.label}'
)

# Update to_dict for TemplateZone
model = model.replace(
    '"height": self.height, "sort_order": self.sort_order',
    '"height": self.height, "sort_order": self.sort_order, "config": self.config'
)

# Add answer_positions to ObjectiveQuestion
old = 'answer = Column(String(50), nullable=False)  # "A" or "AB" or "T"/"F"'
new = 'answer = Column(String(50), nullable=False)'
model = model.replace(old, new)  # Just the comment removal, already handled

# Add correct_answer + answer_positions in ObjectiveQuestion to_dict  
model = model.replace(
    '"correct_answer": self.correct_answer, "sort_order": self.sort_order',
    '"correct_answer": self.correct_answer, "answer_positions": self.answer_positions, "sort_order": self.sort_order'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(model)

print('1. Template model updated OK')
