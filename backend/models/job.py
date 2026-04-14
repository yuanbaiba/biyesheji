from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum
from datetime import datetime
from utils.db import Base
import enum


class JobType(str, enum.Enum):
    SOFTWARE_ENGINEER = "软件工程师"
    PRODUCT_MANAGER = "产品经理"
    DATA_SCIENTIST = "数据科学家"
    UX_DESIGNER = "UI设计师"
    OPERATIONS = "运营专员"
    MARKETING = "市场专员"
    HR = "人力资源"
    OTHER = "其他"


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(100), nullable=False, index=True)
    department = Column(String(50), nullable=True)
    job_type = Column(String(50), nullable=False)  # 软件工程师, 产品经理, etc.
    description = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    salary_range = Column(String(50), nullable=True)  # e.g., "15k-25k"
    location = Column(String(100), nullable=True)
    headcount = Column(Integer, default=1)  # 招聘人数
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, nullable=True)  # 管理员ID
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


from pydantic import BaseModel
from typing import Optional


class JobCreate(BaseModel):
    title: str
    department: Optional[str] = None
    job_type: str
    description: Optional[str] = None
    requirements: Optional[str] = None
    salary_range: Optional[str] = None
    location: Optional[str] = None
    headcount: int = 1
    is_active: bool = True  # 默认启用


class JobUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    job_type: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    salary_range: Optional[str] = None
    location: Optional[str] = None
    headcount: Optional[int] = None
    is_active: Optional[bool] = None


class JobResponse(BaseModel):
    id: int
    title: str
    department: Optional[str] = None
    job_type: str
    description: Optional[str] = None
    requirements: Optional[str] = None
    salary_range: Optional[str] = None
    location: Optional[str] = None
    headcount: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
