import os
base = r"D:\Desktop\Gaston Studio\services\OnlineMark"
path = os.path.join(base, "backend", "app", "routers", "templates.py")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Fix update_template to handle markers, zones, questions
old_update = """def update_template(template_id: str, req: TemplateUpdate,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    temp = db.query(Template).filter(Template.id == template_id).first()
    if not temp:
        raise HTTPException(status_code=404, detail="模板不存在")

    update_data = req.dict(exclude_unset=True, exclude_none=True)
    for key in ['markers', 'zones', 'questions']:
        update_data.pop(key, None)

    for key, value in update_data.items():
        setattr(temp, key, value)
    db.commit()
    db.refresh(temp)
    return {"message": "更新成功", "template": temp.to_dict()}"""

new_update = """def update_template(template_id: str, req: TemplateUpdate,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    temp = db.query(Template).filter(Template.id == template_id).first()
    if not temp:
        raise HTTPException(status_code=404, detail="模板不存在")

    update_data = req.dict(exclude_unset=True, exclude_none=True)
    for key in ['markers', 'zones', 'questions']:
        update_data.pop(key, None)

    for key, value in update_data.items():
        setattr(temp, key, value)
    
    # Handle markers if provided
    if req.markers is not None:
        db.query(TemplateMarker).filter(TemplateMarker.template_id == template_id).delete()
        for m in req.markers:
            marker = TemplateMarker(
                template_id=template_id, point_index=m.point_index,
                x=m.x, y=m.y, width=m.width or 0, height=m.height or 0,
                shape=m.shape or "circle", label=m.label
            )
            db.add(marker)
    
    # Handle zones if provided
    if req.zones is not None:
        db.query(TemplateZone).filter(TemplateZone.template_id == template_id).delete()
        for z in req.zones:
            zone = TemplateZone(
                template_id=template_id, zone_type=z.zone_type, label=z.label,
                x=z.x, y=z.y, width=z.width, height=z.height,
                sort_order=z.sort_order, config=z.config
            )
            db.add(zone)
    
    # Handle questions if provided
    if req.questions is not None:
        db.query(ObjectiveQuestion).filter(ObjectiveQuestion.template_id == template_id).delete()
        for q in req.questions:
            obj_q = ObjectiveQuestion(
                template_id=template_id, question_number=q.question_number,
                question_type=q.question_type, options_count=q.options_count,
                options=q.options or ["A","B","C","D"][:q.options_count],
                option_layout=q.option_layout, score=q.score,
                x=q.x, y=q.y, width=q.width, height=q.height,
                correct_answer=q.correct_answer, sort_order=q.sort_order,
                answer_positions=q.answer_positions
            )
            db.add(obj_q)
            if q.correct_answer:
                ca = CorrectAnswer(
                    template_id=template_id, question_id=obj_q.id,
                    question_number=q.question_number, answer=q.correct_answer, score=q.score
                )
                db.add(ca)
    
    db.commit()
    db.refresh(temp)
    return {"message": "更新成功", "template": temp.to_dict()}"""

if old_update in c:
    c = c.replace(old_update, new_update)
    print("update_template fixed with full update support")
else:
    print("WARN: update_template pattern not found")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)
