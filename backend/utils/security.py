import sys
import os

# 原代码是 sys.path.append → 改成 sys.path.insert(0, ...)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException
from jose import JWTError, jwt
import hashlib
import secrets
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from config import SECURITY_CONFIG

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def _hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """哈希密码，返回(salt, hashed_password)"""
    if salt is None:
        salt = secrets.token_hex(16)
    # 使用sha256哈希 salt + password
    hash_obj = hashlib.sha256()
    hash_obj.update(salt.encode('utf-8'))
    hash_obj.update(password.encode('utf-8'))
    hashed = hash_obj.hexdigest()
    return salt, hashed

def get_password_hash(password: str) -> str:
    """生成密码哈希字符串，格式: salt$hash"""
    salt, hashed = _hash_password(password)
    return f"{salt}${hashed}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码（兼容旧哈希格式）"""
    if not hashed_password:
        return False

    # 检查是否是新的哈希格式 (salt$hash)
    if '$' in hashed_password:
        try:
            salt, stored_hash = hashed_password.split('$', 1)
            _, expected_hash = _hash_password(plain_password, salt)
            return secrets.compare_digest(stored_hash, expected_hash)
        except:
            # 解析失败，回退到旧方式
            pass

    # 兼容旧的明文哈希方式（仅用于迁移期间）
    import warnings
    warnings.warn("使用旧密码哈希格式，建议重置密码或重新注册", DeprecationWarning)
    return plain_password == hashed_password

# 生成JWT Token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    # sub必须是字符串
    if 'sub' in to_encode:
        to_encode['sub'] = str(to_encode['sub'])
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, SECURITY_CONFIG["secret_key"], algorithm="HS256"
    )
    return encoded_jwt

# 验证JWT Token
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECURITY_CONFIG["secret_key"], algorithms=["HS256"])
        sub = payload.get("sub")
        if sub is None:
            return None
        return int(sub)  # 转换回int
    except JWTError as e:
        print(f"JWT Error: {e}")
        return None

# 获取当前用户（简化版，用于演示）
def get_current_user(token: str = Depends(oauth2_scheme)):
    from models.user import User

    if token.startswith("demo_token_"):
        user_id = int(token.split("_")[2])
        # 这里应该从数据库获取用户，但为了简化返回模拟用户
        return User(id=user_id, username=f"user_{user_id}", email=f"user_{user_id}@example.com")

    user_id = verify_token(token)
    if user_id is None:
        raise HTTPException(401, "无效的认证令牌")

    # 从数据库获取用户
    from utils.db import SessionLocal
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        return user
    finally:
        db.close()