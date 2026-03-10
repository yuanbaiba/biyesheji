import requests
from config import LLM_CONFIG

def generate_interview_questions(resume_content: str, job_type: str, num: int =5):
    try:
        url = LLM_CONFIG['chat_url']
        headers = {"Content-Type":"application/json", "Authorization":f"Bearer {LLM_CONFIG['api_key']}"}
        prompt = f"你是{job_type}面试官，根据简历生成{num}个问题，简历：{resume_content[:500]}"
        res = requests.post(url, headers=headers, json={"messages":[{"role":"user", "content":prompt}]}, timeout=20)
        result = res.json()
        if result.get("result"):
            qs = [q.strip() for q in result["result"].split("\n") if q.strip()]
            return qs[:num], None
    except:
        pass
    mock = [
        f"你在{job_type}的毕设项目中，核心技术栈是什么？",
        "你使用FastAPI开发接口时，如何做异常处理？",
        "你接入大模型API时，做了哪些稳定性优化？"
    ]
    return mock[:num], None

def evaluate_interview_answer(question: str, answer: str, job_type: str):
    try:
        url = LLM_CONFIG['chat_url']
        headers = {"Content-Type":"application/json", "Authorization":f"Bearer {LLM_CONFIG['api_key']}"}
        prompt = f"你是{job_type}面试官，评价这个回答：问题{question}，回答{answer}"
        res = requests.post(url, headers=headers, json={"messages":[{"role":"user", "content":prompt}]}, timeout=20)
        result = res.json()
        if result.get("result"):
            return result["result"].strip(), None
    except:
        pass
    return "回答清晰，能准确回应问题，体现了相关技术的基础认知，建议补充具体项目细节增强说服力。", None

def get_access_token():
    return "mock_token", None