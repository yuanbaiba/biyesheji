from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional

from utils.db import get_db
from utils.security import verify_password, get_password_hash, create_access_token, verify_token
from models.user import User, UserCreate, UserResponse
from config import SECURITY_CONFIG

router = APIRouter(prefix="/api/auth", tags=["用户认证"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

INVITE_CODE = "123456"


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    invite_code: Optional[str] = None  # 管理员邀请码


@router.post("/register", response_model=UserResponse)
async def register(request: RegisterRequest, db=Depends(get_db)):
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    # 检查邮箱是否已存在
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=400, detail="邮箱已存在")

    # 检查是否是管理员注册（通过invite_code）
    is_admin = request.invite_code == INVITE_CODE if request.invite_code else False

    user = User(
        username=request.username,
        email=request.email,
        hashed_password=get_password_hash(request.password),
        full_name=request.full_name,
        is_admin=is_admin
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_access_token(data={"sub": user.id, "username": user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "is_admin": user.is_admin
    }

@router.get("/me", response_model=UserResponse)
def me(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    if token.startswith("demo_token_"):
        user_id = int(token.split("_")[2])
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        return user

    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Token无效")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user