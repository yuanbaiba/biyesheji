"""
职位管理功能测试
共6项测试用例
"""
import pytest


class TestJobList:
    """职位列表功能测试（2项）"""

    def test_list_active_jobs(self, client, test_job):
        """测试用例15：获取启用职位列表"""
        response = client.get("/api/jobs")
        assert response.status_code == 200
        jobs = response.json()
        assert len(jobs) >= 1
        for job in jobs:
            assert job["is_active"] == True

    def test_list_inactive_jobs_admin(self, client, admin_headers, test_job, db_session):
        """测试用例16：管理员查看所有职位（包括禁用的）"""
        # 先禁用职位
        test_job.is_active = False
        db_session.commit()

        response = client.get("/api/jobs", headers=admin_headers, params={"show_all": "true"})
        assert response.status_code == 200
        # show_all=true时应该返回所有职位
        assert len(response.json()) >= 1


class TestJobCRUD:
    """职位增删改查功能测试（4项）"""

    def test_create_job(self, client, admin_headers):
        """测试用例17：创建职位"""
        response = client.post("/api/jobs", headers=admin_headers, json={
            "title": "Java开发工程师",
            "job_type": "软件工程师",
            "department": "研发部",
            "salary_range": "20k-30k",
            "is_active": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Java开发工程师"

    def test_create_job_without_admin(self, client, auth_headers):
        """测试用例18：普通用户无法创建职位"""
        response = client.post("/api/jobs", headers=auth_headers, json={
            "title": "Test Job",
            "job_type": "其他"
        })
        assert response.status_code == 403

    def test_update_job(self, client, admin_headers, test_job):
        """测试用例19：更新职位"""
        response = client.put(f"/api/jobs/{test_job.id}", headers=admin_headers, json={
            "title": "Python高级工程师",
            "is_active": False
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Python高级工程师"
        assert data["is_active"] == False

    def test_delete_job(self, client, admin_headers, test_job):
        """测试用例20：删除职位"""
        response = client.delete(f"/api/jobs/{test_job.id}", headers=admin_headers)
        assert response.status_code == 200