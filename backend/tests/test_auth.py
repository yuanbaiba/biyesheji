"""
用户认证功能测试
共8项测试用例
"""
import pytest


class TestUserRegistration:
    """用户注册功能测试（3项）"""

    def test_register_success(self, client):
        """测试用例1：用户注册成功"""
        response = client.post("/api/auth/register", json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"

    def test_register_duplicate_username(self, client, test_user):
        """测试用例2：用户名已存在"""
        response = client.post("/api/auth/register", json={
            "username": "testuser",
            "email": "another@example.com",
            "password": "password123"
        })
        assert response.status_code == 400
        assert "用户名已存在" in response.json()["detail"]

    def test_register_duplicate_email(self, client, test_user):
        """测试用例3：邮箱已存在"""
        response = client.post("/api/auth/register", json={
            "username": "anotheruser",
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == 400
        assert "邮箱已存在" in response.json()["detail"]


class TestUserLogin:
    """用户登录功能测试（3项）"""

    def test_login_success(self, client, test_user):
        """测试用例4：登录成功"""
        response = client.post("/api/auth/login", data={
            "username": "testuser",
            "password": "testpass123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["username"] == "testuser"

    def test_login_wrong_password(self, client, test_user):
        """测试用例5：密码错误"""
        response = client.post("/api/auth/login", data={
            "username": "testuser",
            "password": "wrongpassword"
        })
        assert response.status_code == 401

    def test_login_user_not_found(self, client):
        """测试用例6：用户不存在"""
        response = client.post("/api/auth/login", data={
            "username": "nonexistent",
            "password": "password123"
        })
        assert response.status_code == 401


class TestUserInfo:
    """用户信息功能测试（2项）"""

    def test_get_user_info(self, client, auth_headers, test_user):
        """测试用例7：获取当前用户信息"""
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["is_admin"] == False

    def test_get_user_info_unauthorized(self, client):
        """测试用例8：未授权访问"""
        response = client.get("/api/auth/me")
        assert response.status_code == 401