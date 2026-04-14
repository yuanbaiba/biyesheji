from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from utils.db import get_db
from utils.security import get_password_hash
from api.auth import oauth2_scheme, me
from models.user import User, UserResponse
from models.job import Job
from models.interview import Interview
from models.resume import Resume

router = APIRouter(prefix="/api/admin", tags=["管理员"])


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    is_admin: bool = True


class ToggleAdminResponse(BaseModel):
    message: str
    is_admin: bool


@router.get("/stats")
def get_stats(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """获取系统统计数据"""
    user = me(token, db)
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")

    total_users = db.query(User).count()
    total_jobs = db.query(Job).count()
    total_interviews = db.query(Interview).count()
    total_resumes = db.query(Resume).count()

    return {
        "total_users": total_users,
        "total_jobs": total_jobs,
        "total_interviews": total_interviews,
        "total_resumes": total_resumes
    }


@router.get("/users", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """获取所有用户列表"""
    user = me(token, db)
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")

    users = db.query(User).order_by(User.created_at.desc()).all()
    return users


@router.post("/users", response_model=UserResponse)
def create_admin_user(user_data: UserCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """创建管理员用户"""
    admin = me(token, db)
    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")

    # 检查用户名是否存在
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 检查邮箱是否存在
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="邮箱已存在")

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        is_admin=user_data.is_admin
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.put("/users/{user_id}/toggle-admin", response_model=ToggleAdminResponse)
def toggle_admin(user_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """切换用户管理员权限"""
    admin = me(token, db)
    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 不能取消自己的管理员权限
    if admin.id == user_id:
        raise HTTPException(status_code=400, detail="不能修改自己的管理员权限")

    target_user.is_admin = not target_user.is_admin
    db.commit()

    return {
        "message": f"已将用户 {target_user.username} 设置为{'管理员' if target_user.is_admin else '普通用户'}",
        "is_admin": target_user.is_admin
    }


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """删除用户"""
    admin = me(token, db)
    if not admin.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 不能删除自己
    if admin.id == user_id:
        raise HTTPException(status_code=400, detail="不能删除自己")

    db.delete(target_user)
    db.commit()
    return {"message": "删除成功"}


@router.get("/interviews")
def list_all_interviews(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """获取所有面试记录"""
    user = me(token, db)
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")

    interviews = db.query(Interview).order_by(Interview.created_at.desc()).all()

    result = []
    for interview in interviews:
        # 获取用户名
        applicant = db.query(User).filter(User.id == interview.user_id).first()
        username = applicant.username if applicant else "未知"

        # 获取简历信息
        resume = db.query(Resume).filter(Resume.id == interview.resume_id).first()
        resume_name = resume.file_name if resume else "未知"
        resume_content = resume.content[:500] + "..." if resume and resume.content and len(resume.content) > 500 else (resume.content if resume else "")
        # 提取简历中的姓名
        resume_name_display = resume.name if resume and resume.name else resume_name

        # 获取职位信息
        job = db.query(Job).filter(Job.id == interview.job_id).first() if interview.job_id else None
        job_title = job.title if job else interview.job_type

        # 计算已回答问题数
        from models.interview import InterviewAnswer
        answered_count = db.query(InterviewAnswer).filter(InterviewAnswer.interview_id == interview.id).count()

        result.append({
            "id": interview.id,
            "user_id": interview.user_id,
            "username": username,
            "resume_id": interview.resume_id,
            "resume_name": resume_name_display,
            "resume_content": resume_content,
            "job_id": interview.job_id,
            "job_title": job_title,
            "job_type": interview.job_type,
            "status": "已完成" if interview.status == 1 else "进行中",
            "status_code": interview.status,
            "total_score": interview.total_score if interview.total_score else 0,
            "question_num": interview.question_num,
            "answered_num": answered_count,
            "created_at": interview.created_at.isoformat() if interview.created_at else None,
            "finish_time": interview.finish_time.isoformat() if interview.finish_time else None
        })

    return result


@router.get("/resumes")
def list_all_resumes(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """获取所有简历"""
    user = me(token, db)
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")

    resumes = db.query(Resume).order_by(Resume.created_at.desc()).all()

    result = []
    for resume in resumes:
        # 获取用户名
        applicant = db.query(User).filter(User.id == resume.user_id).first()
        username = applicant.username if applicant else "未知"

        result.append({
            "id": resume.id,
            "user_id": resume.user_id,
            "username": username,
            "file_name": resume.file_name,
            "name": resume.name,
            "email": resume.email,
            "phone": resume.phone,
            "skills": resume.skills,
            "experience": resume.experience,
            "content": resume.content,
            "analysis": resume.analysis,
            "created_at": resume.created_at.isoformat() if resume.created_at else None
        })

    return result