"""
面试流程功能测试
共8项测试用例
"""
import pytest
import json


class TestInterviewCreate:
    """面试创建功能测试（3项）"""

    def test_create_interview_success(self, client, auth_headers, test_resume, test_job):
        """测试用例21：创建面试成功"""
        response = client.post("/api/interview/create", headers=auth_headers, json={
            "user_id": test_resume.user_id,
            "resume_id": test_resume.id,
            "job_id": test_job.id,
            "job_type": "软件工程师",
            "question_num": 5
        })
        assert response.status_code == 200
        data = response.json()
        assert "questions" in data["data"]
        assert data["message"] == "面试创建成功"

    def test_create_interview_inactive_job(self, client, auth_headers, test_resume, test_job, admin_headers):
        """测试用例22：禁用的职位无法发起面试"""
        # 先禁用职位
        client.put(f"/api/jobs/{test_job.id}", headers=admin_headers, json={"is_active": False})

        response = client.post("/api/interview/create", headers=auth_headers, json={
            "user_id": test_resume.user_id,
            "resume_id": test_resume.id,
            "job_id": test_job.id,
            "job_type": "软件工程师",
            "question_num": 5
        })
        assert response.status_code == 400
        assert "已下架" in response.json()["detail"]

    def test_create_interview_empty_resume(self, client, auth_headers, test_user, test_job, db_session):
        """测试用例23：空简历无法发起面试"""
        # 创建空简历
        empty_resume = Resume(
            user_id=test_user.id,
            file_name="empty.pdf",
            file_path="/uploads/empty.pdf",
            content="",
            analysis="{}"
        )
        db_session.add(empty_resume)
        db_session.commit()
        db_session.refresh(empty_resume)

        response = client.post("/api/interview/create", headers=auth_headers, json={
            "user_id": test_user.id,
            "resume_id": empty_resume.id,
            "job_id": test_job.id,
            "job_type": "软件工程师",
            "question_num": 5
        })
        assert response.status_code == 400
        assert "简历内容为空" in response.json()["detail"]


class TestInterviewAnswer:
    """面试回答功能测试（3项）"""

    def test_submit_answer(self, client, auth_headers, test_interview):
        """测试用例24：提交回答成功"""
        response = client.post("/api/interview/submit_answer", headers=auth_headers, json={
            "interview_id": test_interview.id,
            "question": "请介绍一下你自己",
            "answer": "我是一名有三年经验的Python开发工程师，熟悉Web开发。",
            "job_type": "软件工程师"
        })
        assert response.status_code == 200
        data = response.json()
        assert "evaluation" in data["data"]

    def test_submit_empty_answer(self, client, auth_headers, test_interview):
        """测试用例25：空回答获得低分"""
        response = client.post("/api/interview/submit_answer", headers=auth_headers, json={
            "interview_id": test_interview.id,
            "question": "请介绍一下你自己",
            "answer": "无",
            "job_type": "软件工程师"
        })
        assert response.status_code == 200
        evaluation = json.loads(response.json()["data"]["evaluation"])
        assert evaluation["overall_score"] < 20

    def test_submit_irrelevant_answer(self, client, auth_headers, test_interview):
        """测试用例26：答非所问获得低分"""
        response = client.post("/api/interview/submit_answer", headers=auth_headers, json={
            "interview_id": test_interview.id,
            "question": "请介绍一下你自己",
            "answer": "我不会",
            "job_type": "软件工程师"
        })
        assert response.status_code == 200
        evaluation = json.loads(response.json()["data"]["evaluation"])
        assert evaluation["overall_score"] < 20


class TestInterviewFinish:
    """面试结束功能测试（2项）"""

    def test_finish_interview(self, client, auth_headers, test_interview, db_session):
        """测试用例27：结束面试并计算总分"""
        # 先添加回答
        answer = InterviewAnswer(
            interview_id=test_interview.id,
            question="问题1",
            answer="这是一段完整的回答，包含足够的细节来展示我的技术能力。",
            evaluation=json.dumps({"overall_score": 85, "scores": {}})
        )
        db_session.add(answer)
        db_session.commit()

        response = client.post("/api/interview/finish", headers=auth_headers, json={
            "interview_id": test_interview.id,
            "user_id": test_interview.user_id
        })
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total_score"] > 0

    def test_finish_nonexistent_interview(self, client, auth_headers, test_user):
        """测试用例28：不存在的面试无法结束"""
        response = client.post("/api/interview/finish", headers=auth_headers, json={
            "interview_id": 9999,
            "user_id": test_user.id
        })
        assert response.status_code == 404


# 修复导入问题
from models.resume import Resume
from models.interview import InterviewAnswer