import os
import json
import re
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from models.resume import Resume
from models.user import User
from utils.db import get_db
from utils.security import get_current_user
from utils.file_utils import save_upload_file, is_valid_resume_file
from services.agent_manager import agent_manager

router = APIRouter(prefix="/api/resume", tags=["简历管理"])


def extract_contact_info(content):
    """从简历内容中提取联系方式"""
    result = {"name": "", "phone": "", "email": "", "position": ""}

    if not content:
        return result

    # 统一换行符，方便处理
    content = content.replace('\r\n', '\n').replace('\r', '\n')

    # 提取手机号 - 多种格式，兼容各种前缀
    phone_label_patterns = [
        r'手机号[码]?[：:\s]*',      # 手机号码、手机号、手机：
        r'联系电话[码]?[：:\s]*',    # 联系电话、联系电话：
        r'移动电话[：:\s]*',         # 移动电话：
        r'电\s*话[码]?[：:\s]*',     # 电话、电话号码：
        r'Tel(?:ephone)?[：:\s]*',  # Tel:、Telephone:
        r'Mobile[：:\s]*',          # Mobile:
        r'手\s*机[：:\s]*',         # 手机：
    ]
    phone_body_pattern = r'([1][3-9]\d{9})'  # 匹配11位手机号

    # 先尝试带标签的匹配
    for label_pattern in phone_label_patterns:
        full_pattern = label_pattern + phone_body_pattern
        match = re.search(full_pattern, content, re.IGNORECASE)
        if match:
            result["phone"] = match.group(1)
            break

    # 如果没找到，尝试直接匹配独立的手机号（在行首或冒号后）
    if not result["phone"]:
        # 匹配形如 "手机 18367868899" 或 "电话: 18367868899" 的独立行
        standalone_patterns = [
            r'^手机[号\s]*([1][3-9]\d{9})',
            r'^电话[号\s]*([1][3-9]\d{9})',
            r'手机号[：:\s]*([1][3-9]\d{9})',
            r'联系手机[：:\s]*([1][3-9]\d{9})',
        ]
        for pattern in standalone_patterns:
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                result["phone"] = match.group(1)
                break

    # 如果还是没有，匹配任何出现的11位手机号（排除已知的其他号码）
    if not result["phone"]:
        all_phones = re.findall(r'\b([1][3-9]\d{9})\b', content)
        if all_phones:
            result["phone"] = all_phones[0]  # 取第一个

    # 提取邮箱 - 多种格式，兼容各种前缀
    email_label_patterns = [
        r'E-?mail[：:\s]*',           # E-mail:、Email:
        r'邮箱[：:\s]*',              # 邮箱：
        r'电子邮件[：:\s]*',          # 电子邮件：
        r'Mail[：:\s]*',              # Mail:
        r'信箱[：:\s]*',              # 信箱：
    ]
    email_body_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'

    # 先尝试带标签的匹配
    for label_pattern in email_label_patterns:
        full_pattern = label_pattern + email_body_pattern
        match = re.search(full_pattern, content, re.IGNORECASE)
        if match:
            result["email"] = match.group(1).lower()
            break

    # 如果没找到，直接匹配邮箱
    if not result["email"]:
        all_emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
        if all_emails:
            result["email"] = all_emails[0].lower()

    # 提取姓名 - 通常在简历开头
    name_patterns = [
        r'姓名[：:\s]*([^\s\n，,。.]+)',
        r'^([^\s\n，,。.]{2,5})(?=\s*\n|\s*[,，]|\s*$)',  # 开头2-5个汉字
        r'姓\s*名[：:\s]*([^\s\n，,。.]+)',
    ]
    for pattern in name_patterns:
        match = re.search(pattern, content)
        if match:
            name = match.group(1).strip()
            # 过滤掉明显不是姓名的
            if len(name) >= 2 and len(name) <= 6 and not any(x in name for x in ["电话", "邮箱", "地址", "简历", "求职", "意向", "学历", "教育", "专业", "技能", "项目", "经验", "工作"]):
                result["name"] = name
                break

    return result


def convert_analysis_for_frontend(analysis):
    """将分析结果转换为前端期望的格式"""
    if not analysis:
        return {}

    # 如果已经是扁平格式（前端期望的），直接返回
    if isinstance(analysis, dict) and "name" in analysis:
        return analysis

    # 如果是嵌套格式，进行转换
    if isinstance(analysis, dict):
        result = {}

        # basic_info 转换
        if "basic_info" in analysis:
            basic = analysis["basic_info"]
            result["name"] = basic.get("name", "")
            result["education"] = basic.get("education", "")
            result["working_years"] = basic.get("working_years", 0)

        # skills 转换 - 合并所有技能
        all_skills = []
        if "skills" in analysis:
            skills = analysis["skills"]
            if isinstance(skills, dict):
                for key in ["technical", "soft", "tools"]:
                    if key in skills and isinstance(skills[key], list):
                        all_skills.extend(skills[key])
            elif isinstance(skills, list):
                all_skills.extend(skills)
        result["skills"] = all_skills

        # basic_info 中可能有 email, phone
        if "basic_info" in analysis:
            basic = analysis["basic_info"]
            if not result.get("email") and basic.get("email"):
                result["email"] = basic.get("email", "")
            if not result.get("phone") and basic.get("phone"):
                result["phone"] = basic.get("phone", "")
            if not result.get("name") and basic.get("name"):
                result["name"] = basic.get("name", "")

        # experience_years
        result["experience_years"] = analysis.get("experience_years", 0)

        # projects
        result["projects"] = analysis.get("projects", [])

        # strengths
        result["strengths"] = analysis.get("strengths", [])

        # weaknesses
        result["weaknesses"] = analysis.get("weaknesses", [])

        # 其他字段
        result["position"] = analysis.get("job_preference", "")

        return result

    return {}


def safe_literal_eval(data):
    """安全解析Python字面量"""
    if not data:
        return {}
    if isinstance(data, dict):
        return data
    try:
        import ast
        return ast.literal_eval(data)
    except:
        return {}


@router.post("/upload")
async def upload_resume(
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # 验证文件
    if not is_valid_resume_file(file.filename):
        raise HTTPException(status_code=400, detail="不支持的文件类型，仅支持 docx 和 pdf")

    # 保存文件
    file_path = save_upload_file(file.file.read(), file.filename)

    try:
        # 使用多智能体系统处理简历
        result = agent_manager.process_resume(file_path)
        content = result.get("content", "")

        # 从内容中提取联系方式
        contact = extract_contact_info(content)

        # 保存到数据库
        resume = Resume(
            user_id=current_user.id,
            file_name=file.filename,
            file_path=file_path,
            name=contact.get("name", ""),
            phone=contact.get("phone", ""),
            email=contact.get("email", ""),
            position=contact.get("position", ""),
            content=content,
            analysis=str(result.get("analysis", {}))
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)

        # 返回时也包含提取的信息
        analysis_data = result.get("analysis", {})
        if isinstance(analysis_data, dict):
            if "skills" not in analysis_data or not analysis_data.get("skills"):
                analysis_data["skills"] = {}
            if "technical" not in analysis_data.get("skills", {}):
                analysis_data["skills"]["technical"] = []
            if "name" not in analysis_data:
                analysis_data["name"] = contact.get("name", "")
            if "phone" not in analysis_data:
                analysis_data["phone"] = contact.get("phone", "")
            if "email" not in analysis_data:
                analysis_data["email"] = contact.get("email", "")

        return {
            "code": 200,
            "message": "上传成功",
            "data": {
                "id": resume.id,
                "file_name": resume.file_name,
                "name": contact.get("name", ""),
                "phone": contact.get("phone", ""),
                "email": contact.get("email", ""),
                "content_preview": (content[:500] + "...") if content and len(content) > 500 else content,
                "analysis": analysis_data
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"简历处理失败: {str(e)}")


@router.get("/list")
async def list_resumes(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).all()
    result = []
    for resume in resumes:
        raw_analysis = safe_literal_eval(resume.analysis)
        analysis = convert_analysis_for_frontend(raw_analysis)
        result.append({
            "id": resume.id,
            "file_name": resume.file_name,
            "name": resume.name or analysis.get("name", ""),
            "phone": resume.phone or analysis.get("phone", ""),
            "email": resume.email or analysis.get("email", ""),
            "position": resume.position or analysis.get("position", ""),
            "skills": resume.skills or ",".join(analysis.get("skills", [])) if analysis.get("skills") else "",
            "experience": resume.experience or "",
            "content_preview": (resume.content[:200] + "...") if resume.content and len(resume.content) > 200 else resume.content,
            "analysis": analysis,
            "created_at": resume.created_at.isoformat() if resume.created_at else None
        })
    return {
        "code": 200,
        "message": "获取成功",
        "data": result
    }


@router.get("/{resume_id}")
async def get_resume(
        resume_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()

    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")

    raw_analysis = safe_literal_eval(resume.analysis)
    analysis = convert_analysis_for_frontend(raw_analysis)

    return {
        "code": 200,
        "message": "获取成功",
        "data": {
            "id": resume.id,
            "file_name": resume.file_name,
            "file_path": resume.file_path,
            "name": resume.name or analysis.get("name", ""),
            "phone": resume.phone or analysis.get("phone", ""),
            "email": resume.email or analysis.get("email", ""),
            "position": resume.position or analysis.get("position", ""),
            "skills": resume.skills or ",".join(analysis.get("skills", [])) if analysis.get("skills") else "",
            "experience": resume.experience or "",
            "content": resume.content,
            "analysis": analysis,
            "created_at": resume.created_at.isoformat() if resume.created_at else None
        }
    }


@router.delete("/{resume_id}")
async def delete_resume(
        resume_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()

    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在")

    # 删除文件
    if resume.file_path and os.path.exists(resume.file_path):
        try:
            os.remove(resume.file_path)
        except:
            pass

    db.delete(resume)
    db.commit()

    return {
        "code": 200,
        "message": "删除成功"
    }