# -*- coding: utf-8 -*-
import os, uuid, json, shutil, asyncio
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models.user import User
from app.models.template import Template
from app.models.scan import ScanBatch, ScannedSheet, RecognitionResult, SubjectiveImage, RecognitionStatus
from app.services.recognition import RecognitionEngine
from app.utils.auth import get_current_user
from typing import List

router = APIRouter(prefix="/api/scan", tags=["扫描识别"])

@router.post("/batch")
def create_batch(name: str = Form(...), template_id: str = Form(...),
                 exam_name: str = Form(None), db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    temp = db.query(Template).filter(Template.id == template_id).first()
    if not temp:
        raise HTTPException(status_code=404, detail="模板不存在")
    batch = ScanBatch(name=name, template_id=template_id, exam_name=exam_name, upload_order="sequential", created_by=current_user.id)
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return {"message": "批次创建成功", "batch": {"id": batch.id, "name": batch.name}}

@router.post("/upload")
async def upload_sheets(batch_id: str = Form(...), files: List[UploadFile] = File(...),
                        db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    batch = db.query(ScanBatch).filter(ScanBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")
    batch_dir = os.path.join(settings.SCAN_DIR, batch_id)
    os.makedirs(batch_dir, exist_ok=True)

    sheets = []
    for file in files:
        filename = f"{uuid.uuid4()}_{file.filename}"
        filepath = os.path.join(batch_dir, filename)
        with open(filepath, "wb") as f:
            content = await file.read()
            f.write(content)
        sheet = ScannedSheet(batch_id=batch_id, filename=file.filename, file_path=filepath, page_number=1, side="front")
        db.add(sheet)
        sheets.append(sheet)

    batch.total_sheets += len(sheets)
    db.commit()
    return {"message": f"上传成功，共{len(sheets)}张", "count": len(sheets)}

@router.post("/recognize/{batch_id}")
def recognize_batch(batch_id: str, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    batch = db.query(ScanBatch).filter(ScanBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")
    temp = db.query(Template).filter(Template.id == batch.template_id).first()
    if not temp:
        raise HTTPException(status_code=404, detail="模板不存在")

    sheets = db.query(ScannedSheet).filter(
        ScannedSheet.batch_id == batch_id,
        ScannedSheet.status != RecognitionStatus.COMPLETED
    ).all()

    engine = RecognitionEngine()
    subj_dir = os.path.join(settings.SUBJECTIVE_DIR, batch_id)
    os.makedirs(subj_dir, exist_ok=True)

    results = []
    for sheet in sheets:
        try:
            sheet.status = RecognitionStatus.PROCESSING
            db.commit()

            result = engine.process_sheet(sheet.file_path, temp)

            sheet.student_id = result.get("student_id")
            sheet.status = RecognitionStatus.COMPLETED
            db.commit()

            for ans in result.get("objective_answers", []):
                rr = RecognitionResult(
                    sheet_id=sheet.id,
                    question_number=ans["question_number"],
                    question_type=ans["question_type"],
                    detected_answer=ans.get("detected"),
                    correct_answer=ans.get("correct"),
                    is_correct=ans.get("is_correct"),
                    score=ans.get("score", 0),
                    max_score=ans.get("max_score", 0),
                    confidence=ans.get("confidence"),
                    details=json.dumps(ans)
                )
                db.add(rr)

            subj_images = engine.save_subjective_images(result, sheet.id, subj_dir)
            for si in subj_images:
                si_record = SubjectiveImage(
                    sheet_id=sheet.id,
                    question_number=si["question_number"],
                    file_path=si["file_path"],
                    max_score=0
                )
                q_data = [a for a in result.get("objective_answers", []) if a["question_number"] == si["question_number"]]
                db.add(si_record)

            db.commit()
            results.append({"sheet_id": sheet.id, "student_id": sheet.student_id, "status": "completed"})

        except Exception as e:
            sheet.status = RecognitionStatus.FAILED
            sheet.error_message = str(e)
            db.commit()
            results.append({"sheet_id": sheet.id, "status": "failed", "error": str(e)})

    batch.processed_sheets += len(results)
    processed = db.query(ScannedSheet).filter(
        ScannedSheet.batch_id == batch_id, ScannedSheet.status == RecognitionStatus.COMPLETED
    ).count()
    failed = db.query(ScannedSheet).filter(
        ScannedSheet.batch_id == batch_id, ScannedSheet.status == RecognitionStatus.FAILED
    ).count()
    batch.processed_sheets = processed
    batch.status = "completed" if processed + failed >= batch.total_sheets else "processing"
    db.commit()

    return {"message": f"识别完成，成功{processed}张，失败{failed}张", "results": results}

@router.get("/batch")
def list_batches(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    batches = db.query(ScanBatch).order_by(ScanBatch.created_at.desc()).all()
    result = []
    for b in batches:
        processed = db.query(ScannedSheet).filter(
            ScannedSheet.batch_id == b.id, ScannedSheet.status == RecognitionStatus.COMPLETED
        ).count()
        failed = db.query(ScannedSheet).filter(
            ScannedSheet.batch_id == b.id, ScannedSheet.status == RecognitionStatus.FAILED
        ).count()
        result.append({
            "id": b.id, "name": b.name, "template_id": b.template_id,
            "exam_name": b.exam_name, "total": b.total_sheets,
            "processed": processed, "failed": failed,
            "status": b.status, "created_at": b.created_at.isoformat() if b.created_at else None
        })
    return result

@router.get("/batch/{batch_id}")
def get_batch(batch_id: str, db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):
    batch = db.query(ScanBatch).filter(ScanBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")
    sheets = db.query(ScannedSheet).filter(ScannedSheet.batch_id == batch_id).all()
    return {
        "batch": {
            "id": batch.id, "name": batch.name, "template_id": batch.template_id,
            "exam_name": batch.exam_name, "total": batch.total_sheets,
            "processed": batch.processed_sheets, "status": batch.status,
            "created_at": batch.created_at.isoformat() if batch.created_at else None
        },
        "sheets": [{
            "id": s.id, "filename": s.filename, "student_id": s.student_id,
            "student_name": s.student_name, "status": s.status.value if hasattr(s.status, 'value') else str(s.status),
            "error_message": s.error_message
        } for s in sheets]
    }
