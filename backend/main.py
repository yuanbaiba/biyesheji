import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pymysql
from config import DB_CONFIG

mysql_config = {
    "host": DB_CONFIG['host'],
    "port": DB_CONFIG['port'],
    "user": DB_CONFIG['user'],
    "password": DB_CONFIG['password'],
    "charset": DB_CONFIG['charset']
}

try:
    conn = pymysql.connect(**mysql_config, connect_timeout=10)
    cursor = conn.cursor()

    # 检查RESET_DB环境变量
    reset_db = os.environ.get('RESET_DB', '').lower() == 'true'

    if reset_db:
        # 重置模式：删除并重建数据库
        print(f"重置数据库: {DB_CONFIG['database']}")
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_CONFIG['database']};")
        cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    else:
        # 安全模式：检查数据库是否存在，不存在则创建
        cursor.execute(f"SHOW DATABASES LIKE '{DB_CONFIG['database']}';")
        if not cursor.fetchone():
            print(f"创建数据库: {DB_CONFIG['database']}")
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        else:
            print(f"数据库已存在: {DB_CONFIG['database']}")

    conn.commit()
except Exception as e:
    print(f"数据库错误: {e}")
    sys.exit(1)
finally:
    if 'cursor' in locals(): cursor.close()
    if 'conn' in locals(): conn.close()

try:
    from utils.db import init_db
    init_db()
except Exception as e:
    print(f"表初始化: {e}")

from config import FILE_CONFIG
os.makedirs(FILE_CONFIG['upload_path'], exist_ok=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import CORS_ORIGINS

app = FastAPI(title="智能面试系统API", version="1.0.0", docs_url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api.auth import router as auth_router
from api.resume import router as resume_router
from api.interview import router as interview_router
from api.jobs import router as jobs_router
from api.admin import router as admin_router

app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(interview_router)
app.include_router(jobs_router)
app.include_router(admin_router)

@app.get("/api/health")
def health():
    return {"code":200, "message":"ok"}

if __name__ == "__main__":
    import uvicorn
    from config import SERVER_PORT, DEBUG
    uvicorn.run(app="main:app", host="0.0.0.0", port=SERVER_PORT, reload=DEBUG)