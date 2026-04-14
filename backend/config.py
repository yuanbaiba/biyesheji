import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "123456"),
    "database": os.getenv("DB_NAME", "auto_interview"),
    "charset": os.getenv("DB_CHARSET", "utf8mb4")
}

SECURITY_CONFIG = {
    "secret_key": os.getenv("SECRET_KEY", "auto-interview-2026-key-123456789"),
    "algorithm": os.getenv("JWT_ALGORITHM", "HS256"),
    "access_token_expire_minutes": int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
}

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
FILE_CONFIG = {
    "upload_path": UPLOAD_DIR,
    "allowed_ext": [".docx", ".pdf", ".jpg", ".jpeg", ".png"],
    "max_file_size": 10 * 1024 * 1024,
    "baidu_api_key": os.getenv("BAIDU_API_KEY", ""),
    "baidu_secret_key": os.getenv("BAIDU_SECRET_KEY", "")
}

# LLM 配置 - DeepSeek
LLM_API_KEY = os.getenv("ANTHROPIC_API_KEY", "sk-b30f6108cea045378e136b9d0b0dfc75")
LLM_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "https://api.deepseek.com")
LLM_MODEL = os.getenv("ANTHROPIC_MODEL", "deepseek-chat")

DEBUG = os.getenv("DEBUG", "True").lower() == "true"
SERVER_PORT = int(os.getenv("SERVER_PORT", "8001"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
