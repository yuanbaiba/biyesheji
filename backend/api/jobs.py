from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from utils.db import get_db
from models.job import Job, JobCreate, JobUpdate, JobResponse
from api.auth import oauth2_scheme, me

router = APIRouter(prefix="/api/jobs", tags=["职位管理"])


def get_current_admin_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """验证管理员权限"""
    user = me(token, db)
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user


@router.get("", response_model=List[JobResponse])
def list_jobs(
    job_type: Optional[str] = None,
    is_active: Optional[bool] = True,
    show_all: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取职位列表（show_all=true时返回所有职位）"""
    query = db.query(Job)
    if job_type:
        query = query.filter(Job.job_type == job_type)
    # show_all=true 时返回所有职位（包括禁用的），用于管理员
    if show_all and show_all.lower() == 'true':
        pass  # 不过滤is_active
    elif is_active is not None:
        query = query.filter(Job.is_active == is_active)
    return query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """获取职位详情"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")
    return job


@router.post("", response_model=JobResponse)
def create_job(job: JobCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """创建职位（需管理员权限）"""
    try:
        user = me(token, db)
        if not user.is_admin:
            raise HTTPException(status_code=403, detail="需要管理员权限")
    except Exception:
        raise HTTPException(status_code=401, detail="请先登录")

    db_job = Job(
        title=job.title,
        department=job.department,
        job_type=job.job_type,
        description=job.description,
        requirements=job.requirements,
        salary_range=job.salary_range,
        location=job.location,
        headcount=job.headcount,
        is_active=job.is_active,
        created_by=user.id
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(job_id: int, job_update: JobUpdate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """更新职位（需管理员权限）"""
    try:
        user = me(token, db)
        if not user.is_admin:
            raise HTTPException(status_code=403, detail="需要管理员权限")
    except Exception:
        raise HTTPException(status_code=401, detail="请先登录")

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")

    update_data = job_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(job, key, value)

    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """删除职位（需管理员权限）"""
    try:
        user = me(token, db)
        if not user.is_admin:
            raise HTTPException(status_code=403, detail="需要管理员权限")
    except Exception:
        raise HTTPException(status_code=401, detail="请先登录")

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="职位不存在")

    db.delete(job)
    db.commit()
    return {"message": "删除成功"}


@router.get("/types/list")
def get_job_types():
    """获取所有职位类型"""
    return {
        "types": [
            {"value": "软件工程师", "label": "软件工程师"},
            {"value": "产品经理", "label": "产品经理"},
            {"value": "数据科学家", "label": "数据科学家"},
            {"value": "UI设计师", "label": "UI设计师"},
            {"value": "运营专员", "label": "运营专员"},
            {"value": "市场专员", "label": "市场专员"},
            {"value": "人力资源", "label": "人力资源"},
            {"value": "其他", "label": "其他"}
        ]
    }
