from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from utils.db import get_db
from models.user import User
from models.resume import Resume
from models.job import Job
from models.interview import Interview, InterviewAnswer
from services.llm_service import generate_interview_questions, evaluate_interview_answer

router = APIRouter(prefix="/api/interview", tags=["AI面试"])


class InterviewCreate(BaseModel):
    user_id: int
    resume_id: int
    job_id: int = None
    job_type: str
    question_num: int = 5


class AnswerSubmit(BaseModel):
    interview_id: int
    question: str
    answer: str
    job_type: str


@router.post("/create")
def create(info: InterviewCreate, db=Depends(get_db)):
    if not db.query(User).filter(User.id == info.user_id).first():
        raise HTTPException(status_code=404, detail="用户不存在")
    resume = db.query(Resume).filter(Resume.id == info.resume_id, Resume.user_id == info.user_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")
    if not resume.content or len(resume.content.strip()) < 10:
        raise HTTPException(status_code=400, detail="简历内容为空")

    # 检查职位是否存在且已启用
    if info.job_id:
        job = db.query(Job).filter(Job.id == info.job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="职位不存在")
        if not job.is_active:
            raise HTTPException(status_code=400, detail="该职位已下架，无法发起面试")

    qs, err = generate_interview_questions(resume.content, info.job_type, info.question_num)
    if err:
        raise HTTPException(status_code=500, detail=f"AI生成失败: {err}")

    interview = Interview(
        user_id=info.user_id,
        resume_id=info.resume_id,
        job_id=info.job_id,
        job_type=info.job_type,
        question_num=info.question_num,
        status=0
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)

    return {
        "code": 200,
        "message": "面试创建成功",
        "data": {
            "interview_id": interview.id,
            "questions": qs
        }
    }


@router.post("/submit_answer")
def submit(info: AnswerSubmit, db=Depends(get_db)):
    interview = db.query(Interview).filter(Interview.id == info.interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")

    eva, err = evaluate_interview_answer(info.question, info.answer, info.job_type)
    if err:
        raise HTTPException(status_code=500, detail=f"AI评价失败: {err}")

    ans = InterviewAnswer(
        interview_id=info.interview_id,
        question=info.question,
        answer=info.answer,
        evaluation=eva
    )
    db.add(ans)
    db.commit()

    return {
        "code": 200,
        "message": "提交成功",
        "data": {
            "evaluation": eva
        }
    }


@router.get("/list")
def list_interview(user_id: int, db=Depends(get_db)):
    interviews = db.query(Interview).filter(Interview.user_id == user_id).all()
    result = []
    for interview in interviews:
        # 获取简历信息
        resume = db.query(Resume).filter(Resume.id == interview.resume_id).first()
        # 获取答案列表
        answers = db.query(InterviewAnswer).filter(InterviewAnswer.interview_id == interview.id).all()

        result.append({
            "id": interview.id,
            "resume_id": interview.resume_id,
            "resume_name": resume.file_name if resume else "未知",
            "job_type": interview.job_type,
            "job_id": interview.job_id,
            "status": "已完成" if interview.status == 1 else "进行中",
            "question_num": interview.question_num,
            "answered_num": len(answers),
            "total_score": interview.total_score,
            "created_at": interview.created_at.isoformat() if interview.created_at else None,
            "finish_time": interview.finish_time.isoformat() if interview.finish_time else None
        })
    return result


@router.get("/{interview_id}")
def get_interview(interview_id: int, user_id: int, db=Depends(get_db)):
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == user_id
    ).first()
    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")

    # 获取简历信息
    resume = db.query(Resume).filter(Resume.id == interview.resume_id).first()
    # 获取答案列表
    answers = db.query(InterviewAnswer).filter(InterviewAnswer.interview_id == interview.id).all()

    # 解析 evaluation JSON
    parsed_answers = []
    for ans in answers:
        eval_data = None
        if ans.evaluation:
            try:
                import json
                eval_data = json.loads(ans.evaluation) if isinstance(ans.evaluation, str) else ans.evaluation
            except:
                eval_data = ans.evaluation
        parsed_answers.append({
            "id": ans.id,
            "question": ans.question,
            "answer": ans.answer,
            "evaluation": eval_data,
            "created_at": ans.created_at.isoformat() if ans.created_at else None
        })

    return {
        "id": interview.id,
        "resume_id": interview.resume_id,
        "resume": {
            "id": resume.id,
            "file_name": resume.file_name,
            "name": resume.name,
            "content": resume.content
        } if resume else None,
        "job_type": interview.job_type,
        "job_id": interview.job_id,
        "status": "已完成" if interview.status == 1 else "进行中",
        "question_num": interview.question_num,
        "answers": parsed_answers,
        "total_score": interview.total_score,
        "evaluation": interview.evaluation,
        "created_at": interview.created_at.isoformat() if interview.created_at else None,
        "finish_time": interview.finish_time.isoformat() if interview.finish_time else None
    }


class FinishRequest(BaseModel):
    interview_id: int
    user_id: int


@router.post("/finish")
def finish(body: FinishRequest = Body(...), db=Depends(get_db)):
    interview = db.query(Interview).filter(
        Interview.id == body.interview_id,
        Interview.user_id == body.user_id
    ).first()
    if not interview:
        raise HTTPException(status_code=404, detail="面试不存在")

    # 计算总得分（100分制，直接平均各题分数）
    answers = db.query(InterviewAnswer).filter(InterviewAnswer.interview_id == body.interview_id).all()
    total_score = 0
    scored_count = 0
    if answers:
        for ans in answers:
            if ans.evaluation:
                try:
                    import json
                    eva = json.loads(ans.evaluation) if isinstance(ans.evaluation, str) else ans.evaluation
                    score = eva.get('overall_score', 0)
                    total_score += score
                    scored_count += 1
                    print(f"答案 {ans.id} 得分: {score}")
                except Exception as e:
                    print(f"答案 {ans.id} 解析失败: {e}")
        # 用实际计分的答案数量来计算平均分
        total_score = round(total_score / scored_count, 1) if scored_count > 0 else 0
        print(f"面试 {body.interview_id} 总分: {total_score} ({scored_count}/{len(answers)} 题有分数)")

    interview.status = 1
    interview.finish_time = datetime.now()
    interview.total_score = total_score
    db.commit()

    return {
        "code": 200,
        "message": "面试已结束",
        "data": {
            "total_score": total_score
        }
    }