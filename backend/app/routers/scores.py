# -*- coding: utf-8 -*-
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.scan import ScanBatch, ScannedSheet, RecognitionResult, SubjectiveImage
from app.models.score import ExamScore
from app.utils.auth import get_current_user
from typing import List
from io import BytesIO

router = APIRouter(prefix="/api/scores", tags=["成绩管理"])

@router.post("/calculate/{batch_id}")
def calculate_scores(batch_id: str, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    batch = db.query(ScanBatch).filter(ScanBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")
    sheets = db.query(ScannedSheet).filter(
        ScannedSheet.batch_id == batch_id,
        ScannedSheet.status == "completed"
    ).all()

    results = []
    for sheet in sheets:
        obj_results = db.query(RecognitionResult).filter(
            RecognitionResult.sheet_id == sheet.id
        ).all()
        obj_score = sum(r.score for r in obj_results)

        subj_images = db.query(SubjectiveImage).filter(
            SubjectiveImage.sheet_id == sheet.id,
            SubjectiveImage.graded == True
        ).all()
        subj_score = sum(s.score for s in subj_images if s.score) if subj_images else 0

        total = obj_score + subj_score
        full_score = sum(r.max_score for r in obj_results) + sum(s.max_score for s in subj_images if s.max_score) if subj_images else sum(r.max_score for r in obj_results)

        existing = db.query(ExamScore).filter(ExamScore.sheet_id == sheet.id).first()
        if existing:
            existing.objective_score = obj_score
            existing.subjective_score = subj_score
            existing.total_score = total
        else:
            es = ExamScore(
                batch_id=batch_id, sheet_id=sheet.id,
                student_id=sheet.student_id, student_name=sheet.student_name,
                objective_score=obj_score, subjective_score=subj_score,
                total_score=total, full_score=full_score,
                details=json.dumps([r.details for r in obj_results] if obj_results else [])
            )
            db.add(es)

        results.append({
            "sheet_id": sheet.id, "student_id": sheet.student_id,
            "objective": obj_score, "subjective": subj_score, "total": total
        })

    db.commit()
    scores = db.query(ExamScore).filter(ExamScore.batch_id == batch_id).order_by(ExamScore.total_score.desc()).all()
    for idx, s in enumerate(scores):
        s.rank = f"{idx + 1}/{len(scores)}"
    db.commit()

    return {"message": "成绩计算完成", "results": results}

@router.get("/batch/{batch_id}")
def get_batch_scores(batch_id: str, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    scores = db.query(ExamScore).filter(ExamScore.batch_id == batch_id).order_by(ExamScore.total_score.desc()).all()
    return [{
        "id": s.id, "student_id": s.student_id, "student_name": s.student_name,
        "objective_score": s.objective_score, "subjective_score": s.subjective_score,
        "total_score": s.total_score, "full_score": s.full_score,
        "rank": s.rank
    } for s in scores]

@router.get("/statistics/{batch_id}")
def get_statistics(batch_id: str, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    scores = db.query(ExamScore).filter(ExamScore.batch_id == batch_id).all()
    if not scores:
        return {"message": "暂无数据"}

    total_scores = [s.total_score for s in scores]
    avg = sum(total_scores) / len(total_scores) if total_scores else 0
    max_s = max(total_scores) if total_scores else 0
    min_s = min(total_scores) if total_scores else 0
    passed = sum(1 for s in total_scores if s >= (scores[0].full_score * 0.6)) if scores[0].full_score else 0

    return {
        "total_students": len(total_scores),
        "average": round(avg, 2),
        "max_score": max_s,
        "min_score": min_s,
        "pass_count": passed,
        "pass_rate": round(passed / len(total_scores) * 100, 2) if total_scores else 0,
        "full_score": scores[0].full_score if scores else 0
    }

@router.get("/export/{batch_id}")
def export_scores(batch_id: str, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    import csv
    scores = db.query(ExamScore).filter(ExamScore.batch_id == batch_id).order_by(ExamScore.total_score.desc()).all()
    if not scores:
        raise HTTPException(status_code=404, detail="暂无成绩数据")

    output = []
    header = ["排名", "考号", "姓名", "客观题得分", "主观题得分", "总分", "满分"]
    output.append(",".join(header))
    for s in scores:
        row = [s.rank or "", s.student_id or "", s.student_name or "",
               str(s.objective_score), str(s.subjective_score),
               str(s.total_score), str(s.full_score)]
        output.append(",".join(row))

    return {"csv": "\n".join(output), "filename": f"scores_{batch_id}.csv"}
