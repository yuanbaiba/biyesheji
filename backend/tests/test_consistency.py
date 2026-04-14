"""
一致性验证测试
验证AI评价与人工评价的一致性
"""
import pytest
import json


class TestEvaluationConsistency:
    """评价一致性测试"""

    @pytest.fixture(autouse=True)
    def setup(self, client, auth_headers, test_resume, test_job):
        self.client = client
        self.headers = auth_headers
        self.resume_id = test_resume.id
        self.job_id = test_job.id
        self.user_id = test_resume.user_id

    def test_good_answer_high_score(self):
        """一致性测试1：优秀回答获得高分（75%以上）"""
        good_answer = """在我的上一个项目中，我担任后端开发负责人，带领团队5人开发了一套电商系统。
        我负责的核心模块是订单处理系统，使用Python的FastAPI框架构建。
        遇到的主要技术挑战是高并发场景下的库存扣减问题，我通过Redis分布式锁和消息队列实现了解决方案，
        将系统吞吐量从1000 QPS提升到了5000 QPS，项目上线后运行稳定，得到了客户的好评。"""

        response = self.client.post("/api/interview/submit_answer", headers=self.headers, json={
            "interview_id": self.user_id,
            "question": "请介绍一下你最成功的项目经历",
            "answer": good_answer,
            "job_type": "软件工程师"
        })

        assert response.status_code == 200
        evaluation = json.loads(response.json()["data"]["evaluation"])
        assert evaluation["overall_score"] >= 75, f"优秀回答只得了{evaluation['overall_score']}分"

    def test_poor_answer_low_score(self):
        """一致性测试2：差回答获得低分（40%以下）"""
        poor_answer = "还行吧"

        response = self.client.post("/api/interview/submit_answer", headers=self.headers, json={
            "interview_id": self.user_id,
            "question": "请介绍一下你最成功的项目经历",
            "answer": poor_answer,
            "job_type": "软件工程师"
        })

        assert response.status_code == 200
        evaluation = json.loads(response.json()["data"]["evaluation"])
        assert evaluation["overall_score"] < 40, f"敷衍回答得了{evaluation['overall_score']}分"

    def test_irrelevant_answer_low_score(self):
        """一致性测试3：答非所问获得低分"""
        irrelevant_answer = "我不会忘记"

        response = self.client.post("/api/interview/submit_answer", headers=self.headers, json={
            "interview_id": self.user_id,
            "question": "请介绍一下你最成功的项目经历",
            "answer": irrelevant_answer,
            "job_type": "软件工程师"
        })

        assert response.status_code == 200
        evaluation = json.loads(response.json()["data"]["evaluation"])
        assert evaluation["overall_score"] < 30, f"答非所问得了{evaluation['overall_score']}分"

    def test_technical_accuracy_scoring(self):
        """一致性测试4：技术准确性维度评分"""
        # 包含明显技术错误的回答
        tech_wrong_answer = """我精通Python，所有语法我都完全掌握。
        关于数据库，我知道MySQL是一种数据库，它能够存储数据。
        关于并发，我使用过多线程技术来提高性能。"""

        response = self.client.post("/api/interview/submit_answer", headers=self.headers, json={
            "interview_id": self.user_id,
            "question": "你如何保证代码质量",
            "answer": tech_wrong_answer,
            "job_type": "软件工程师"
        })

        assert response.status_code == 200
        evaluation = json.loads(response.json()["data"]["evaluation"])
        # 技术准确性应该较低
        assert evaluation["scores"]["accuracy"] < 15, f"技术错误回答准确性得了{evaluation['scores']['accuracy']}分"

    def test_evidence_scoring(self):
        """一致性测试5：证据支撑维度评分"""
        # 有项目案例的回答
        with_evidence = """我在项目中遇到了内存泄漏问题，通过Profiling工具定位到是第三方SDK的缓存导致的，
        最终通过升级SDK版本和添加手动清理机制解决了问题。
        具体使用了Python的memory_profiler和objgraph工具进行排查。"""

        without_evidence = """我遇到过内存泄漏问题，解决方法是升级SDK。"""

        # 有证据的回答应该得高分
        response1 = self.client.post("/api/interview/submit_answer", headers=self.headers, json={
            "interview_id": self.user_id,
            "question": "遇到过什么技术挑战",
            "answer": with_evidence,
            "job_type": "软件工程师"
        })

        # 没证据的回答应该得低分
        response2 = self.client.post("/api/interview/submit_answer", headers=self.headers, json={
            "interview_id": self.user_id,
            "question": "遇到过什么技术挑战",
            "answer": without_evidence,
            "job_type": "软件工程师"
        })

        eval1 = json.loads(response1.json()["data"]["evaluation"])
        eval2 = json.loads(response2.json()["data"]["evaluation"])

        # 有详细案例的证据分应该更高
        assert eval1["scores"]["evidence"] > eval2["scores"]["evidence"], \
            f"有案例:{eval1['scores']['evidence']} vs 无案例:{eval2['scores']['evidence']}"

    def test_completeness_scoring(self):
        """一致性测试6：完整性维度评分"""
        complete_answer = """我的优势有以下三点：
        第一，技术能力扎实，熟悉Python、JavaScript、Go等多种语言；
        第二，沟通能力强，曾负责与客户的需求对接；
        第三，学习能力强，自学了机器学习和区块链技术。"""

        incomplete_answer = """我的优势是技术能力强。"""

        response1 = self.client.post("/api/interview/submit_answer", headers=self.headers, json={
            "interview_id": self.user_id,
            "question": "你有哪些优势",
            "answer": complete_answer,
            "job_type": "软件工程师"
        })

        response2 = self.client.post("/api/interview/submit_answer", headers=self.headers, json={
            "interview_id": self.user_id,
            "question": "你有哪些优势",
            "answer": incomplete_answer,
            "job_type": "软件工程师"
        })

        eval1 = json.loads(response1.json()["data"]["evaluation"])
        eval2 = json.loads(response2.json()["data"]["evaluation"])

        # 完整回答的完整性分数应该更高
        assert eval1["scores"]["completeness"] >= eval2["scores"]["completeness"]

    def test_relevance_dimension(self):
        """一致性测试7：相关性维度评分"""
        relevant_answer = """作为软件工程师，我认为持续集成非常重要。
        我在项目中使用了Jenkins进行自动化部署，配合GitHub Actions实现代码提交后自动测试和部署。
        部署时间从原来的30分钟缩短到了5分钟。"""

        irrelevant_answer = """我喜欢打篮球，每周都会和朋友一起打球。"""

        response1 = self.client.post("/api/interview/submit_answer", headers=self.headers, json={
            "interview_id": self.user_id,
            "question": "谈谈你对DevOps的理解",
            "answer": relevant_answer,
            "job_type": "软件工程师"
        })

        response2 = self.client.post("/api/interview/submit_answer", headers=self.headers, json={
            "interview_id": self.user_id,
            "question": "谈谈你对DevOps的理解",
            "answer": irrelevant_answer,
            "job_type": "软件工程师"
        })

        eval1 = json.loads(response1.json()["data"]["evaluation"])
        eval2 = json.loads(response2.json()["data"]["evaluation"])

        # 切题的回答相关性应该更高
        assert eval1["scores"]["relevance"] > eval2["scores"]["relevance"], \
            f"切题:{eval1['scores']['relevance']} vs 跑题:{eval2['scores']['relevance']}"

    def test_multi_dimension_consistency(self):
        """一致性测试8：多维度综合评分一致性"""
        mixed_answer = """我认为Python很难学。
        我用一个框架叫Django，它可以开发网站。
        项目经验方面，我参与过一个项目。"""

        response = self.client.post("/api/interview/submit_answer", headers=self.headers, json={
            "interview_id": self.user_id,
            "question": "请评价你的Python能力",
            "answer": mixed_answer,
            "job_type": "软件工程师"
        })

        evaluation = json.loads(response.json()["data"]["evaluation"])

        # 验证各维度分数在合理范围
        for dimension, score in evaluation["scores"].items():
            assert 0 <= score <= 20, f"{dimension}分数{score}超出范围"

        # 综合分数应该是各维度平均（允许一定误差）
        expected_total = sum(evaluation["scores"].values())
        assert abs(evaluation["overall_score"] - expected_total) < 5, \
            f"综合分数{evaluation['overall_score']}与维度总分{expected_total}不一致"