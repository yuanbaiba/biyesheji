"""
结果查看功能测试
共4项测试用例
"""
import pytest


class TestInterviewList:
    """面试列表功能测试（2项）"""

    def test_list_user_interviews(self, client, auth_headers, test_interview):
        """测试用例29：获取用户面试列表"""
        response = client.get(f"/api/interview/list?user_id={test_interview.user_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_list_own_interviews_only(self, client, auth_headers, test_interview, test_user):
        """测试用例30：只能看到自己的面试"""
        response = client.get(f"/api/interview/list?user_id={test_user.id}", headers=auth_headers)
        interviews = response.json()
        for interview in interviews:
            assert interview["user_id"] == test_user.id


class TestInterviewDetail:
    """面试详情功能测试（2项）"""

    def test_get_interview_detail(self, client, auth_headers, test_interview, test_user):
        """测试用例31：获取面试详情"""
        response = client.get(
            f"/api/interview/{test_interview.id}?user_id={test_user.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["job_type"] == "软件工程师"
        assert "resume" in data

    def test_cannot_view_others_interview(self, client, auth_headers, test_interview):
        """测试用例32：无法查看他人面试"""
        response = client.get(
            f"/api/interview/{test_interview.id}?user_id=9999",
            headers=auth_headers
        )
        assert response.status_code == 404