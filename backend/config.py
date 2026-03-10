import os

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "123456",  # 改成你自己的MySQL密码
    "database": "auto_interview",
    "charset": "utf8mb4"
}

SECURITY_CONFIG = {
    "secret_key": "auto-interview-2026-key-123456789",
    "algorithm": "HS256",
    "access_token_expire_minutes": 30
}

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
FILE_CONFIG = {
    "upload_path": UPLOAD_DIR,
    "allowed_ext": [".docx", ".pdf", ".jpg", ".jpeg", ".png"],
    "max_file_size": 10 * 1024 * 1024
}

LLM_CONFIG = {
    "api_key": "bce-v3/ALTAK-eTR4c4WtyvZDGClmCVrRK/3b81a396f9bbf09580275aa798d6b4142d756799",
    "secret_key": "",
    "token_url": "https://aip.baidubce.com/oauth/2.0/token",
    "chat_url": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-lite-pro-128k"
}

DEBUG = True
SERVER_PORT = 8000
CORS_ORIGINS = ["*"]