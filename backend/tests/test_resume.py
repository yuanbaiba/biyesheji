"""
简历管理功能测试
共6项测试用例
"""
import pytest
import io


class TestResumeUpload:
    """简历上传功能测试（3项）"""

    def test_upload_resume_success(self, client, auth_headers):
        """测试用例9：简历上传成功"""
        file_content = b"Name: Test User\nPhone: 18367868899\nEmail: test@example.com"
        response = client.post(
            "/api/resume/upload",
            headers=auth_headers,
            files={"file": ("resume.txt", io.BytesIO(file_content), "text/plain")}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_upload_resume_without_auth(self, client):
        """测试用例10：未授权上传"""
        file_content = b"Test resume content"
        response = client.post(
            "/api/resume/upload",
            files={"file": ("resume.txt", io.BytesIO(file_content), "text/plain")}
        )
        assert response.status_code == 401

    def test_upload_invalid_file_type(self, client, auth_headers):
        """测试用例11：无效文件类型"""
        file_content = b"Test content"
        response = client.post(
            "/api/resume/upload",
            headers=auth_headers,
            files={"file": ("resume.exe", io.BytesIO(file_content), "application/octet-stream")}
        )
        assert response.status_code == 400
        assert "不支持的文件类型" in response.json()["detail"]


class TestResumeList:
    """简历列表功能测试（2项）"""

    def test_list_resumes(self, client, auth_headers, test_resume):
        """测试用例12：获取简历列表"""
        response = client.get("/api/resume/list", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) >= 1

    def test_list_resumes_own_only(self, client, auth_headers, test_resume):
        """测试用例13：只能看到自己的简历"""
        response = client.get("/api/resume/list", headers=auth_headers)
        data = response.json()["data"]
        for resume in data:
            assert resume["user_id"] == test_resume.user_id


class TestResumeDetail:
    """简历详情功能测试（1项）"""

    def test_get_resume_detail(self, client, auth_headers, test_resume):
        """测试用例14：获取简历详情"""
        response = client.get(f"/api/resume/{test_resume.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == "张三"