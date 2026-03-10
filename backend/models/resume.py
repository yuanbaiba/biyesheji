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
    content = Column(Text, nullable=True)
    status = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)