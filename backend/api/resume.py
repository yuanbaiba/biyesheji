import os
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from models.resume import Resume
from models.user import User
from utils.db import get_db
from utils.security import get_current_user
from utils.file_utils import save_upload_file, is_valid_resume_file
from services.resume_parser import parse_resume

router = APIRouter(prefix="/resume", tags=["resume"])


@router.post("/upload")
async def upload_resume(
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # 验证文件
    if not is_valid_resume_file(file.filename):
        return {"error": "Invalid file type, only docx and pdf are supported"}

    # 保存文件
    file_path = save_upload_file(file.file.read(), file.filename)

    # 解析简历
    parsed = parse_resume(file_path, file.filename)
    if not parsed:
        return {"error": "Could not parse resume"}

    # 保存到数据库
    resume = Resume(
        user_id=current_user.id,
        name=parsed.get('name', ''),
        phone=parsed.get('phone', ''),
        email=parsed.get('email', ''),
        position=parsed.get('position', ''),
        skills=parsed.get('skills', ''),
        experience=parsed.get('experience', '')
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return {
        "id": resume.id,
        "name": resume.name,
        "phone": resume.phone,
        "email": resume.email,
        "position": resume.position,
        "skills": resume.skills,
        "experience": resume.experience
    }


@router.get("/list")
async def list_resumes(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    return resumes


@router.get("/{resume_id}")
async def get_resume(
        resume_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    return resume