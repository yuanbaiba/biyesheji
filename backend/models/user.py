from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from utils.db import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str | None = None
    is_admin: bool

    class Config:
        from_attributes = True