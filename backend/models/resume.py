from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from utils.db import Base


class Resume(Base):
    __tablename__ = "resumes"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, index=True, nullable=False)
    file_name = Column(String(100), nullable=False)
    file_path = Column(String(200), nullable=False)
    name = Column(String(50), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    position = Column(String(50), nullable=True)
    skills = Column(Text, nullable=True)
    experience = Column(Text, nullable=True)
    content = Column(Text, nullable=True)  # 原始简历内容
    analysis = Column(Text, nullable=True)  # AI分析结果
    status = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)