# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.template import Template
from app.models.scan import ScanBatch, ScannedSheet, SubjectiveImage
from app.models.grading import GradingTask, GradingAssignment, Grade
from app.utils.auth import get_current_user, require_role
from app.schemas.grading import GradingTaskCreate, GradingAssignRequest, GradeSubmit
from typing import List

router = APIRouter(prefix="/api/grading", tags=["评卷管理"])

@router.post("/task")
def create_grading_task(req: GradingTaskCreate, db: Session = Depends(get_db),
                        current_user: User = Depends(require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN))):
    batch = db.query(ScanBatch).filter(ScanBatch.id == req.batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")
    task = GradingTask(
        name=req.name, batch_id=req.batch_id, template_id=req.template_id,
        threshold=req.threshold, created_by=current_user.id
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return {"message": "阅卷任务创建成功", "task": {"id": task.id, "name": task.name}}

@router.get("/task")
def list_grading_tasks(db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    query = db.query(GradingTask)
    if current_user.role not in (UserRole.SUPER_ADMIN, UserRole.ADMIN):
        teacher_assignments = db.query(GradingAssignment.teacher_id).filter(
            GradingAssignment.teacher_id == current_user.id
        ).subquery()
        tasks = db.query(GradingTask).filter(
            GradingTask.id.in_(db.query(GradingAssignment.task_id).filter(
                GradingAssignment.teacher_id == current_user.id
            ))
        ).all()
    else:
        tasks = query.order_by(GradingTask.created_at.desc()).all()

    result = []
    for t in tasks:
        assignments = db.query(GradingAssignment).filter(GradingAssignment.task_id == t.id).all()
        result.append({
            "id": t.id, "name": t.name, "batch_id": t.batch_id,
            "template_id": t.template_id, "status": t.status.value if hasattr(t.status, 'value') else str(t.status),
            "total_subjective": t.total_subjective, "graded_count": t.graded_count,
            "threshold": t.threshold, "created_at": t.created_at.isoformat() if t.created_at else None,
            "assignments": [{
                "id": a.id, "teacher_id": a.teacher_id,
                "question_number": a.question_number,
                "total_count": a.total_count, "graded_count": a.graded_count,
                "status": a.status
            } for a in assignments]
        })
    return result

@router.post("/assign")
def assign_grading(req: GradingAssignRequest, db: Session = Depends(get_db),
                   current_user: User = Depends(require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN))):
    task = db.query(GradingTask).filter(GradingTask.id == req.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    teacher = db.query(User).filter(User.id == req.teacher_id, User.role == UserRole.TEACHER).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="教师不存在")

    sheets = db.query(ScannedSheet).filter(
        ScannedSheet.batch_id == task.batch_id,
        ScannedSheet.status == "completed"
    ).all()

    created = []
    for qnum in req.question_numbers:
        existing = db.query(GradingAssignment).filter(
            GradingAssignment.task_id == req.task_id,
            GradingAssignment.teacher_id == req.teacher_id,
            GradingAssignment.question_number == qnum
        ).first()
        if existing:
            continue
        subj_count = db.query(SubjectiveImage).filter(
            SubjectiveImage.question_number == qnum,
            SubjectiveImage.sheet_id.in_([s.id for s in sheets])
        ).count()
        assignment = GradingAssignment(
            task_id=req.task_id, teacher_id=req.teacher_id,
            question_number=qnum, total_count=max(subj_count, len(sheets)),
            status="pending"
        )
        db.add(assignment)
        created.append(assignment)

    db.commit()
    return {"message": "分配成功", "count": len(created)}

@router.get("/pending")
def get_pending_grading(current_user: User = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    # Teachers and admins can grade
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="仅教师和管理员可查看待评阅列表")
    assignments = db.query(GradingAssignment).filter(
        GradingAssignment.teacher_id == current_user.id,
        GradingAssignment.status != "completed"
    ).all()

    result = []
    for a in assignments:
        task = db.query(GradingTask).filter(GradingTask.id == a.task_id).first()
        subj_images = db.query(SubjectiveImage).filter(
            SubjectiveImage.question_number == a.question_number,
            SubjectiveImage.graded == False
        ).limit(10).all()

        result.append({
            "assignment_id": a.id,
            "task_name": task.name if task else "",
            "question_number": a.question_number,
            "total_count": a.total_count,
            "graded_count": a.graded_count,
            "pending_images": [{
                "id": s.id, "file_path": s.file_path,
                "sheet_id": s.sheet_id, "max_score": s.max_score
            } for s in subj_images]
        })
    return result

@router.post("/grade")
def submit_grade(req: GradeSubmit, db: Session = Depends(get_db),
                 current_user: User = Depends(require_role(UserRole.TEACHER, UserRole.ADMIN, UserRole.SUPER_ADMIN))):
    assignment = db.query(GradingAssignment).filter(
        GradingAssignment.id == req.assignment_id,
        GradingAssignment.teacher_id == current_user.id
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="分配记录不存在")

    grade = Grade(
        assignment_id=req.assignment_id, sheet_id=req.sheet_id,
        subjective_image_id=req.subjective_image_id,
        question_number=req.question_number, score=req.score,
        teacher_id=current_user.id, grading_round=req.grading_round,
        comment=req.comment
    )
    db.add(grade)

    task = db.query(GradingTask).filter(GradingTask.id == assignment.task_id).first()
    teachers_count = db.query(GradingAssignment).filter(
        GradingAssignment.task_id == assignment.task_id,
        GradingAssignment.question_number == req.question_number
    ).count()

    round_grades = db.query(Grade).filter(
        Grade.assignment_id == req.assignment_id,
        Grade.sheet_id == req.sheet_id,
        Grade.question_number == req.question_number
    ).all()

    if len(round_grades) >= teachers_count and teachers_count > 1 and task:
        scores = [g.score for g in round_grades]
        avg_diff = max(scores) - min(scores)
        if avg_diff > task.threshold:
            pass
        else:
            avg_score = sum(scores) / len(scores)
            if req.subjective_image_id:
                subj_img = db.query(SubjectiveImage).filter(
                    SubjectiveImage.id == req.subjective_image_id
                ).first()
                if subj_img:
                    subj_img.score = avg_score
                    subj_img.graded = True
        if req.subjective_image_id:
            subj_img = db.query(SubjectiveImage).filter(
                SubjectiveImage.id == req.subjective_image_id
            ).first()
            if subj_img:
                subj_img.score = req.score
                subj_img.graded = True
    elif req.subjective_image_id:
        subj_img = db.query(SubjectiveImage).filter(
            SubjectiveImage.id == req.subjective_image_id
        ).first()
        if subj_img:
            subj_img.score = req.score
            subj_img.graded = True

    assignment.graded_count += 1
    if assignment.graded_count >= assignment.total_count:
        assignment.status = "completed"
    db.commit()

    return {"message": "评分提交成功"}
