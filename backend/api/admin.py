from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.resume import Resume
from models.interview import Interview
from utils.db import get_db
from utils.security import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def get_stats(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """获取用户统计数据"""
    resume_count = db.query(Resume).filter(Resume.user_id == current_user.id).count()
    interview_count = db.query(Interview).filter(Interview.user_id == current_user.id).count()

    # 计算平均评分
    interviews = db.query(Interview).filter(
        Interview.user_id == current_user.id,
        Interview.status == "finished"
    ).all()

    avg_score = 0
    if interviews:
        total = sum(i.total_score for i in interviews)
        avg_score = round(total / len(interviews), 1)

    return {
        "resume_count": resume_count,
        "interview_count": interview_count,
        "avg_score": avg_score
    }