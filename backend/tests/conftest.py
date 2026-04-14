"""
Pytest配置和共享fixtures
"""
import pytest
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from utils.db import Base, get_db
from models.user import User
from models.job import Job
from models.resume import Resume
from models.interview import Interview, InterviewAnswer
from utils.security import get_password_hash

# 测试数据库配置 - 使用SQLite内存数据库
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """覆盖数据库依赖"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """创建测试客户端"""
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """创建测试用户"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin(db_session):
    """创建测试管理员"""
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        is_admin=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def auth_headers(client, test_user):
    """获取用户认证token"""
    response = client.post("/api/auth/login", data={
        "username": "testuser",
        "password": "testpass123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client, test_admin):
    """获取管理员认证token"""
    response = client.post("/api/auth/login", data={
        "username": "admin",
        "password": "admin123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_job(db_session, test_admin):
    """创建测试职位"""
    job = Job(
        title="Python开发工程师",
        job_type="软件工程师",
        department="技术部",
        description="负责后端开发",
        requirements="熟悉Python",
        salary_range="15k-25k",
        location="杭州",
        headcount=3,
        is_active=True,
        created_by=test_admin.id
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    return job


@pytest.fixture
def test_resume(db_session, test_user):
    """创建测试简历"""
    resume = Resume(
        user_id=test_user.id,
        file_name="test_resume.pdf",
        file_path="/uploads/test_resume.pdf",
        name="张三",
        phone="18367868899",
        email="zhangsan@example.com",
        content="姓名：张三\n手机：18367868899\n邮箱：zhangsan@example.com\n技能：Python, JavaScript, SQL",
        analysis="{}"
    )
    db_session.add(resume)
    db_session.commit()
    db_session.refresh(resume)
    return resume


@pytest.fixture
def test_interview(db_session, test_user, test_resume, test_job):
    """创建测试面试"""
    interview = Interview(
        user_id=test_user.id,
        resume_id=test_resume.id,
        job_id=test_job.id,
        job_type="软件工程师",
        question_num=5,
        status=0
    )
    db_session.add(interview)
    db_session.commit()
    db_session.refresh(interview)
    return interview