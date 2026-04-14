from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from datetime import datetime
from utils.db import Base


class Interview(Base):
    __tablename__ = "interviews"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, index=True, nullable=False)
    resume_id = Column(Integer, index=True, nullable=False)
    job_id = Column(Integer, index=True, nullable=True)  # 关联职位
    job_type = Column(String(50), nullable=False)
    question_num = Column(Integer, default=5)
    status = Column(Integer, default=0)  # 0=进行中, 1=已完成
    total_score = Column(Float, nullable=True)  # 总得分
    evaluation = Column(Text, nullable=True)  # AI评价
    created_at = Column(DateTime, default=datetime.now)
    finish_time = Column(DateTime, nullable=True)


class InterviewAnswer(Base):
    __tablename__ = "interview_answers"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    interview_id = Column(Integer, index=True, nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    evaluation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)