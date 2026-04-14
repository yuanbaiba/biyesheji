"""
性能测试
测试系统在不同负载条件下的表现
"""
import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor


class TestAPIResponseTime:
    """单次API响应时间测试"""

    @pytest.fixture(autouse=True)
    def setup(self, client, auth_headers, test_resume, test_job):
        self.client = client
        self.headers = auth_headers
        self.resume_id = test_resume.id
        self.job_id = test_job.id
        self.user_id = test_resume.user_id

    def test_health_check_response_time(self):
        """性能测试1：健康检查响应时间≤500ms"""
        start = time.time()
        response = self.client.get("/api/health")
        elapsed = (time.time() - start) * 1000
        assert response.status_code == 200
        assert elapsed < 500, f"响应时间{elapsed}ms超过500ms"

    def test_login_response_time(self):
        """性能测试2：登录响应时间≤1秒"""
        start = time.time()
        response = self.client.post("/api/auth/login", data={
            "username": "testuser",
            "password": "testpass123"
        })
        elapsed = (time.time() - start) * 1000
        assert response.status_code == 200
        assert elapsed < 1000, f"响应时间{elapsed}ms超过1000ms"

    def test_interview_create_response_time(self):
        """性能测试3：创建面试响应时间≤2秒"""
        start = time.time()
        response = self.client.post("/api/interview/create", headers=self.headers, json={
            "user_id": self.user_id,
            "resume_id": self.resume_id,
            "job_id": self.job_id,
            "job_type": "软件工程师",
            "question_num": 5
        })
        elapsed = (time.time() - start) * 1000
        assert response.status_code == 200
        assert elapsed < 2000, f"响应时间{elapsed}ms超过2000ms"


class TestConcurrentAccess:
    """并发访问测试"""

    @pytest.fixture(autouse=True)
    def setup(self, client, auth_headers, test_resume, test_job):
        self.client = client
        self.headers = auth_headers
        self.resume_id = test_resume.id
        self.job_id = test_job.id
        self.user_id = test_resume.user_id

    def make_request(self):
        """发起一次请求"""
        try:
            response = self.client.get("/api/health")
            return response.status_code == 200
        except:
            return False

    def test_50_concurrent_requests(self):
        """性能测试4：50用户并发无崩溃"""
        success_count = 0
        error_count = 0

        def worker():
            nonlocal success_count, error_count
            try:
                if self.make_request():
                    success_count += 1
                else:
                    error_count += 1
            except:
                error_count += 1

        threads = []
        for _ in range(50):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert error_count == 0, f"有{error_count}个请求失败"
        assert success_count == 50, f"只有{success_count}个请求成功"

    def test_100_concurrent_interviews(self):
        """性能测试5：100用户并发创建面试"""
        success_count = 0
        error_count = 0

        def create_interview():
            nonlocal success_count, error_count
            try:
                response = self.client.post("/api/interview/create", headers=self.headers, json={
                    "user_id": self.user_id,
                    "resume_id": self.resume_id,
                    "job_id": self.job_id,
                    "job_type": "软件工程师",
                    "question_num": 3
                })
                if response.status_code == 200:
                    success_count += 1
                else:
                    error_count += 1
            except:
                error_count += 1

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(create_interview) for _ in range(100)]
            for f in futures:
                f.result()

        # 允许部分失败（服务降级），但不能全部失败
        assert success_count > 0, "所有请求都失败了"
        print(f"\n100并发测试: 成功{success_count}, 失败{error_count}")


class TestStability:
    """稳定性测试"""

    def test_continuous_requests_stability(self, client):
        """性能测试6：连续100次请求稳定性"""
        failure_count = 0
        for _ in range(100):
            response = client.get("/api/health")
            if response.status_code != 200:
                failure_count += 1

        failure_rate = failure_count / 100
        assert failure_rate < 0.01, f"故障率{failure_rate*100}%超过1%"