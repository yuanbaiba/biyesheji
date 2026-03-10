import os
from config import FILE_CONFIG


def save_upload_file(file, filename):
    """保存上传的文件"""
    upload_path = FILE_CONFIG['upload_path']
    os.makedirs(upload_path, exist_ok=True)

    file_path = os.path.join(upload_path, filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file)
    return file_path


def get_file_extension(filename):
    """获取文件后缀"""
    return os.path.splitext(filename)[1].lower()


def is_valid_resume_file(filename):
    """检查是否是合法的简历文件"""
    ext = get_file_extension(filename)
    return ext in ['.docx', '.pdf']