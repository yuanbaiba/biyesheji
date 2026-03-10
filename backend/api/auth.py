from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import BaseModel

from utils.db import get_db
from models.user import User, UserCreate, UserResponse

SECRET_KEY = "auto-interview-2026-key-123456789"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(prefix="/api/auth", tags=["用户认证"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_password_hash(p): return p
def verify_password(p, h): return p == h

def create_token(data):
    return f"demo_token_{data['sub']}_{data['username']}_{datetime.now().timestamp()}"

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str

@router.post("/register", response_model=UserResponse)
def register(u: UserCreate, db=Depends(get_db)):
    if db.query(User).filter(User.username==u.username).first():
        raise HTTPException(400, "用户名已存在")
    if db.query(User).filter(User.email==u.email).first():
        raise HTTPException(400, "邮箱已存在")
    user = User(username=u.username, email=u.email, hashed_password=get_password_hash(u.password), full_name=u.full_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(form=Depends(OAuth2PasswordRequestForm), db=Depends(get_db)):
    user = db.query(User).filter(User.username==form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(401, "用户名或密码错误")
    token = create_token({"sub":user.id, "username":user.username})
    return {"access_token":token, "token_type":"bearer", "user_id":user.id, "username":user.username}

@router.get("/me", response_model=UserResponse)
def me(token=Depends(oauth2_scheme), db=Depends(get_db)):
    if token.startswith("demo_token_"):
        user_id = int(token.split("_")[2])
        return db.query(User).filter(User.id==user_id).first()
    raise HTTPException(401, "Token无效")