from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from utils.db import get_db
from models.user import User
from models.resume import Resume
from models.interview import Interview, InterviewAnswer
from services.llm_service import generate_interview_questions, evaluate_interview_answer

router = APIRouter(prefix="/api/interview", tags=["AI面试"])

class InterviewCreate(BaseModel):
    user_id: int
    resume_id: int
    job_type: str
    question_num: int =5

class AnswerSubmit(BaseModel):
    interview_id: int
    question: str
    answer: str
    job_type: str

@router.post("/create")
def create(info: InterviewCreate, db=Depends(get_db)):
    if not db.query(User).filter(User.id==info.user_id).first():
        raise HTTPException(404, "用户不存在")
    resume = db.query(Resume).filter(Resume.id==info.resume_id, Resume.user_id==info.user_id).first()
    if not resume:
        raise HTTPException(404, "简历不存在")
    if not resume.content or len(resume.content.strip())<10:
        raise HTTPException(400, "简历内容为空")
    qs, err = generate_interview_questions(resume.content, info.job_type, info.question_num)
    if err: raise HTTPException(500, f"AI生成失败: {err}")
    interview = Interview(user_id=info.user_id, resume_id=info.resume_id, job_type=info.job_type, question_num=info.question_num, status=0)
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return {"interview_id":interview.id, "questions":qs}

@router.post("/submit_answer")
def submit(info: AnswerSubmit, db=Depends(get_db)):
    if not db.query(Interview).filter(Interview.id==info.interview_id).first():
        raise HTTPException(404, "面试不存在")
    eva, err = evaluate_interview_answer(info.question, info.answer, info.job_type)
    if err: raise HTTPException(500, f"AI评价失败: {err}")
    ans = InterviewAnswer(interview_id=info.interview_id, question=info.question, answer=info.answer, evaluation=eva)
    db.add(ans)
    db.commit()
    return {"evaluation": eva}

@router.get("/list")
def list_interview(user_id: int, db=Depends(get_db)):
    return db.query(Interview).filter(Interview.user_id==user_id).all()

@router.post("/finish")
def finish(interview_id: int, user_id: int, db=Depends(get_db)):
    interview = db.query(Interview).filter(Interview.id==interview_id, Interview.user_id==user_id).first()
    if not interview: raise HTTPException(404, "面试不存在")
    interview.status =1
    interview.finish_time = datetime.now()
    db.commit()
    return {"message": "面试已结束"}