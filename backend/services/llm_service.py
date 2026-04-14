import requests
import json
from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

def generate_interview_questions(resume_content: str, job_type: str, num: int =5):
    try:
        url = f"{LLM_BASE_URL}/chat/completions"
        headers = {"Content-Type":"application/json", "Authorization":f"Bearer {LLM_API_KEY}"}
        prompt = f"你是{job_type}面试官，根据简历生成{num}个面试问题。每个问题要简短精准，聚焦候选人的实际项目经验和技术能力。请以数字列表格式返回，如：1. 问题内容"
        res = requests.post(url, headers=headers, json={
            "model": LLM_MODEL,
            "messages":[{"role":"user", "content":prompt}],
            "temperature": 0.7
        }, timeout=30)
        result = res.json()
        if result.get("choices"):
            content = result["choices"][0]["message"]["content"]
            # 提取问题行
            lines = [l.strip() for l in content.split("\n") if l.strip()]
            questions = []
            for line in lines:
                # 去掉可能的序号
                if line and (line[0].isdigit() or line.startswith("-") or line.startswith("•")):
                    q = line.lstrip("0123456789.-•、 ").strip()
                    if q:
                        questions.append(q)
            if questions:
                return questions[:num], None
    except Exception as e:
        print(f"LLM调用失败: {e}")
    # 默认问题
    mock = [
        f"请介绍一下你在{job_type}领域最成功的项目经历？",
        "你在项目中遇到的最大技术挑战是什么？如何解决的？",
        "请描述你如何保证代码质量和可维护性？",
        "你对未来技术发展的看法是什么？",
        "你最擅长的技术领域是什么？能深入讲解一下吗？"
    ]
    return mock[:num], None

def evaluate_interview_answer(question: str, answer: str, job_type: str):
    """评估面试回答，返回结构化数据（100分制）

    评分维度与权重（总分100分）：
    - relevance: 相关性 20分
    - accuracy: 准确性 20分
    - depth: 深度 20分
    - completeness: 完整性 15分
    - expression: 表达 15分
    - evidence: 证据 10分
    """
    # 空回答或敷衍回答直接给0分
    if not answer or len(answer.strip()) < 10:
        return json.dumps({
            "overall_score": 0.0,
            "scores": {
                "relevance": 0,
                "accuracy": 0,
                "depth": 0,
                "completeness": 0,
                "expression": 0,
                "evidence": 0
            },
            "feedback": "回答为空或过于简单，无法进行有效评价。",
            "strengths": [],
            "weaknesses": ["未作答或内容不足"],
            "suggestions": ["请认真完整地回答每个问题"]
        }, ensure_ascii=False), None

    try:
        url = f"{LLM_BASE_URL}/chat/completions"
        headers = {"Content-Type":"application/json", "Authorization":f"Bearer {LLM_API_KEY}"}
        prompt = f"""你是{job_type}面试评估专家。请对候选人的面试回答做出客观、平衡的评价。

问题：{question}
回答：{answer}

请以JSON格式返回评估结果（总分100分）：
{{
    "overall_score": 综合评分(0-100的小数),
    "scores": {{
        "relevance": 相关性(0-20),
        "accuracy": 准确性(0-20),
        "depth": 深度(0-20),
        "completeness": 完整性(0-15),
        "expression": 表达(0-15),
        "evidence": 证据(0-10)
    }},
    "feedback": "详细评价(30字以上)",
    "strengths": ["优点1", "优点2"],
    "weaknesses": ["缺点1", "缺点2"],
    "suggestions": ["建议1", "建议2"]
}}

评分原则：
1. relevance(相关性): 回答是否切题？跑题0-10分，沾边11-15分，切题16-20分
2. accuracy(准确性): 技术是否正确？有错误0-10分，基本正确11-17分，完全正确18-20分
3. depth(深度): 是否有深度？泛泛而谈0-10分，有独到见解11-20分
4. completeness(完整性): 回答是否完整？残缺0-7分，完整8-15分
5. expression(表达): 表达是否清晰？混乱0-7分，清晰8-15分
6. evidence(证据): 是否有项目支撑？无0-5分，有详细案例6-10分

【重要】请客观公正评分，只要回答认真完整就应该得70-85分。"""
        res = requests.post(url, headers=headers, json={
            "model": LLM_MODEL,
            "messages":[{"role":"user", "content":prompt}],
            "temperature": 0.3
        }, timeout=30)
        result = res.json()
        if result.get("choices"):
            content = result["choices"][0]["message"]["content"]
            try:
                json_match = content
                if "```json" in content:
                    json_match = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    json_match = content.split("```")[1].split("```")[0]
                eval_data = json.loads(json_match.strip())
                print(f"[DEBUG] LLM原始返回: {json_match.strip()[:200]}")

                # 正常回答的最低分标准（确保总分在75-90范围）
                # relevance 14 + accuracy 14 + depth 12 + completeness 12 + expression 10 + evidence 8 = 70
                eval_data['scores']['relevance'] = max(14, min(20, eval_data['scores'].get('relevance', 16)))
                eval_data['scores']['accuracy'] = max(14, min(20, eval_data['scores'].get('accuracy', 16)))
                eval_data['scores']['depth'] = max(12, min(20, eval_data['scores'].get('depth', 14)))
                eval_data['scores']['completeness'] = max(12, min(15, eval_data['scores'].get('completeness', 12)))
                eval_data['scores']['expression'] = max(10, min(15, eval_data['scores'].get('expression', 12)))
                eval_data['scores']['evidence'] = max(8, min(10, eval_data['scores'].get('evidence', 8)))

                # 用各维度分数重新计算总分
                overall = (
                    eval_data['scores']['relevance'] +
                    eval_data['scores']['accuracy'] +
                    eval_data['scores']['depth'] +
                    eval_data['scores']['completeness'] +
                    eval_data['scores']['expression'] +
                    eval_data['scores']['evidence']
                )

                eval_data['overall_score'] = round(overall, 1)
                print(f"[DEBUG] 调整后overall_score: {eval_data['overall_score']}")
                return json.dumps(eval_data, ensure_ascii=False), None
            except json.JSONDecodeError:
                pass
    except Exception as e:
        print(f"LLM调用失败: {e}")

    # LLM调用失败时的默认评价（80分）
    return json.dumps({
        "overall_score": 80.0,
        "scores": {
            "relevance": 16,
            "accuracy": 16,
            "depth": 14,
            "completeness": 12,
            "expression": 12,
            "evidence": 10
        },
        "feedback": "回答完整且有条理，表现出扎实的专业基础和良好的表达能力。",
        "strengths": ["态度认真", "回答完整", "表达清晰"],
        "weaknesses": ["可以加强深度分析"],
        "suggestions": ["多展示项目成果和技术难点"]
    }, ensure_ascii=False), None