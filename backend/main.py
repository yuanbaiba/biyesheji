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
    cursor.execute(f"DROP DATABASE IF EXISTS {DB_CONFIG['database']};")
    cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
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

app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(interview_router)

@app.get("/api/health")
def health():
    return {"code":200, "message":"ok"}

if __name__ == "__main__":
    import uvicorn
    from config import SERVER_PORT, DEBUG
    uvicorn.run(app="main:app", host="0.0.0.0", port=SERVER_PORT, reload=DEBUG)