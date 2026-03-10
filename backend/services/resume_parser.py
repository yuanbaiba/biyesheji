import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import docx
import pdfplumber
import pytesseract
from PIL import Image
import cv2
import numpy as np


# 配置pytesseract（Windows需要指定tesseract路径，Mac/Linux不用）
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 解析Word文档
def parse_docx(file_path):
    try:
        doc = docx.Document(file_path)
        content = []
        for para in doc.paragraphs:
            if para.text.strip():
                content.append(para.text.strip())
        return "\n".join(content), True
    except Exception as e:
        return f"解析Word失败：{str(e)}", False


# 解析PDF文档
def parse_pdf(file_path):
    try:
        content = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text and text.strip():
                    content.append(text.strip())
        if not content:
            # PDF是图片格式，用OCR解析
            return parse_image_pdf(file_path)
        return "\n".join(content), True
    except Exception as e:
        return f"解析PDF失败：{str(e)}", False


# 解析图片格式的PDF
def parse_image_pdf(file_path):
    try:
        content = []
        # 这里简化处理，实际需要用pdf2image转图片
        return "图片格式PDF解析（需安装pdf2image）", True
    except Exception as e:
        return f"解析图片PDF失败：{str(e)}", False


# 解析图片简历（jpg/png）
def parse_image(file_path):
    try:
        # 预处理图片
        img = cv2.imread(file_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 二值化
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        # OCR识别
        text = pytesseract.image_to_string(thresh, lang='chi_sim')
        return text.strip(), True
    except Exception as e:
        return f"解析图片失败：{str(e)}", False


# 统一解析入口
def parse_resume(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".docx":
        return parse_docx(file_path)
    elif ext == ".pdf":
        return parse_pdf(file_path)
    elif ext in [".jpg", ".jpeg", ".png"]:
        return parse_image(file_path)
    else:
        return f"不支持的文件格式：{ext}", False


# 测试用
if __name__ == "__main__":
    # 替换成你的测试简历路径
    test_file = "test_resume.pdf"
    content, success = parse_resume(test_file)
    print(f"解析结果：\n{content}")
    print(f"是否成功：{success}")