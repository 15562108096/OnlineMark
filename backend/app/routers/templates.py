# -*- coding: utf-8 -*-
import os, uuid, json, shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models.user import User
from app.models.template import Template, TemplateMarker, TemplateZone, ObjectiveQuestion, CorrectAnswer
from app.utils.auth import get_current_user
from app.schemas.template import TemplateCreate, TemplateUpdate
from typing import List, Optional

router = APIRouter(prefix="/api/templates", tags=["模板管理"])

@router.post("/upload-pdf")
async def upload_template_pdf(file: UploadFile = File(...)):
    import fitz
    import uuid
    ext = os.path.splitext(file.filename)[1] or ".pdf"
    if ext.lower() not in [".pdf"]:
        raise HTTPException(status_code=400, detail="只支持PDF文件")
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(settings.TEMPLATE_DIR, filename)
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)
    # Convert PDF to images
    from app.services.pdf_processor import PDFProcessor
    try:
        img_dir = os.path.join(settings.TEMPLATE_DIR, filename.replace(".pdf", ""))
        img_paths = PDFProcessor.pdf_to_images(filepath, img_dir)
        total_pages = len(img_paths)
        first_page = img_paths[0] if img_paths else filepath
        return {"filename": filename, "filepath": filepath, "url": f"/uploads/templates/{filename}",
                "total_pages": total_pages, "page_images": [f"/uploads/templates/{filename.replace(chr(46)+chr(112)+chr(100)+chr(102),chr(47))}{os.path.basename(p)}" for p in img_paths]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF转换失败: {str(e)}")

@router.post("/upload-image")
async def upload_template_image(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1] or ".png"
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(settings.TEMPLATE_DIR, filename)
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)
    return {"filename": filename, "filepath": filepath, "url": f"/uploads/templates/{filename}"}

@router.post("/", response_model=dict)
def create_template(req: TemplateCreate, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    temp = Template(
        name=req.name, description=req.description,
        subject=req.subject, grade=req.grade, exam_name=req.exam_name,
        info_method=req.info_method, total_pages=req.total_pages or 1,
        image_path=req.pdf_path or "", pdf_path=req.pdf_path,
        created_by=current_user.id
    )
    db.add(temp)
    db.flush()

    total_obj_score = 0.0
    total_subj_score = 0.0
    total_q_score = 0.0

    for m in req.markers:
        marker = TemplateMarker(
            template_id=temp.id, point_index=m.point_index,
            x=m.x, y=m.y, width=m.width or 0, height=m.height or 0,
            shape=m.shape or "circle", label=m.label
        )
        db.add(marker)

    for z in req.zones:
        zone = TemplateZone(
            template_id=temp.id, zone_type=z.zone_type, label=z.label,
            x=z.x, y=z.y, width=z.width, height=z.height, sort_order=z.sort_order,
            config=z.config
        )
        db.add(zone)
        if z.zone_type == "subjective":
            total_subj_score += 0

    for q in req.questions:
        obj_q = ObjectiveQuestion(
            template_id=temp.id, question_number=q.question_number,
            question_type=q.question_type, options_count=q.options_count,
            options=q.options or ["A","B","C","D"][:q.options_count],
            option_layout=q.option_layout, score=q.score,
            x=q.x, y=q.y, width=q.width, height=q.height,
            correct_answer=q.correct_answer, sort_order=q.sort_order,
            answer_positions=q.answer_positions
        )
        db.add(obj_q)
        db.flush()
        total_obj_score += q.score
        total_q_score += q.score

        if q.correct_answer:
            ca = CorrectAnswer(
                template_id=temp.id, question_id=obj_q.id,
                question_number=q.question_number, answer=q.correct_answer, score=q.score
            )
            db.add(ca)

    temp.total_score = total_q_score
    temp.objective_score = total_obj_score
    db.commit()
    db.refresh(temp)
    return {"message": "模板创建成功", "template": temp.to_dict()}

@router.get("/")
def list_templates(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    temps = db.query(Template).order_by(Template.created_at.desc()).all()
    return [t.to_dict() for t in temps]

@router.get("/{template_id}")
def get_template(template_id: str, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    temp = db.query(Template).filter(Template.id == template_id).first()
    if not temp:
        raise HTTPException(status_code=404, detail="模板不存在")
    return temp.to_dict()

@router.put("/{template_id}")
def update_template(template_id: str, req: TemplateUpdate,
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
    return {"message": "更新成功", "template": temp.to_dict()}

@router.delete("/{template_id}")
def delete_template(template_id: str, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    temp = db.query(Template).filter(Template.id == template_id).first()
    if not temp:
        raise HTTPException(status_code=404, detail="模板不存在")
    if temp.image_path and os.path.exists(temp.image_path):
        os.remove(temp.image_path)
    db.delete(temp)
    db.commit()
    return {"message": "删除成功"}

@router.get("/{template_id}/export")
def export_template(template_id: str, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    temp = db.query(Template).filter(Template.id == template_id).first()
    if not temp:
        raise HTTPException(status_code=404, detail="模板不存在")
    data = temp.to_dict()
    image_ext = os.path.splitext(temp.image_path or "")[1]
    data["image_data"] = None
    if temp.image_path and os.path.exists(temp.image_path):
        import base64
        with open(temp.image_path, "rb") as f:
            data["image_data"] = base64.b64encode(f.read()).decode()
        data["image_ext"] = image_ext
    return data
