import requests
import json
import re
import os
from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from typing import Dict, List, Optional, Tuple

# 全局访问令牌缓存
_access_token = None
_token_expires_at = None

def get_access_token():
    """获取访问令牌 - 支持多种API格式"""
    global _access_token, _token_expires_at

    # 如果已有有效令牌，直接返回
    if _access_token and _token_expires_at and datetime.now() < _token_expires_at:
        return _access_token

    try:
        # 优先使用环境变量中的配置
        api_key = os.getenv('ANTHROPIC_API_KEY') or os.getenv('LLM_API_KEY', '')
        base_url = os.getenv('ANTHROPIC_BASE_URL', '')

        # 如果配置了DeepSeek或其他API
        if 'deepseek' in base_url.lower() or 'sfkey' in base_url.lower():
            # DeepSeek格式 - 直接使用API key
            _access_token = api_key
            _token_expires_at = datetime.now() + timedelta(days=30)
            return _access_token

        # 百度API token获取
        token_url = os.getenv('LLM_TOKEN_URL', 'https://aip.baidubce.com/oauth/2.0/token')
        secret_key = os.getenv('LLM_SECRET_KEY', '')

        # API key格式: bce-v3/ACCESS_KEY/SECRET_KEY
        key_parts = api_key.split('/')
        if len(key_parts) >= 3:
            client_id = key_parts[1]
            client_secret = key_parts[2]
        elif len(key_parts) == 2:
            client_id = key_parts[0]
            client_secret = key_parts[1]
        else:
            client_id = api_key
            client_secret = secret_key

        params = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        }

        response = requests.post(token_url, params=params, timeout=10)
        result = response.json()

        if 'access_token' in result:
            _access_token = result['access_token']
            expires_in = result.get('expires_in', 2592000)
            _token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)
            return _access_token
        else:
            print(f"获取access_token失败: {result}")
            return None
    except Exception as e:
        print(f"获取access_token异常: {e}")
        return None

class BaseAgent:
    """基础代理类"""
    def __init__(self, role: str, system_prompt: str):
        self.role = role
        self.system_prompt = system_prompt

    def call_llm(self, messages: List[Dict], temperature: float = 0.7) -> Optional[str]:
        """调用LLM API"""
        try:
            # 使用 config.py 中的配置
            api_key = LLM_API_KEY
            base_url = LLM_BASE_URL
            model = LLM_MODEL

            if base_url and api_key:
                url = base_url.rstrip('/') + '/v1/chat/completions'
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                payload = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature
                }
                res = requests.post(url, headers=headers, json=payload, timeout=60)
                result = res.json()

                if 'error' in result:
                    print(f"LLM API错误: {result.get('error')}")
                    return None

                if result.get("choices") and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"].strip()

        except Exception as e:
            print(f"LLM调用失败: {e}")
        return None

    def chat(self, user_prompt: str, temperature: float = 0.7) -> Optional[str]:
        """简单的对话调用"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        return self.call_llm(messages, temperature)


class ResumeAnalysisAgent(BaseAgent):
    """简历分析代理 - 深入分析候选人背景"""

    def __init__(self):
        super().__init__(
            "简历分析专家",
            """你是专业的简历分析专家，擅长从简历中提取关键信息并进行深度分析。
            你的职责包括：
            1. 提取候选人的技术技能、项目经验、工作经历
            2. 识别候选人的核心优势和潜在弱点
            3. 分析候选人与职位的匹配度
            4. 为后续面试问题生成提供有针对性的背景信息

            请始终保持专业、客观的分析态度。"""
        )

    def analyze_resume(self, resume_content: str) -> Dict:
        """深度分析简历内容"""
        prompt = f"""请深度分析以下简历内容，提取关键信息并进行初步评估：

简历内容：
{resume_content[:3000]}

请以JSON格式返回完整的分析结果：
{{
    "basic_info": {{
        "name": "姓名（如果提供）",
        "education": "学历信息",
        "working_years": 工作年限数字
    }},
    "skills": {{
        "technical": ["技术技能1", "技术技能2"],
        "soft": ["软技能1", "软技能2"],
        "tools": ["工具/框架1", "工具/框架2"]
    }},
    "experience_years": 总工作经验年限数字,
    "projects": [
        {{
            "name": "项目名称",
            "description": "项目描述",
            "tech_stack": "使用的技术栈",
            "role": "在项目中的角色"
        }}
    ],
    "strengths": ["优势1", "优势2", "优势3"],
    "weaknesses": ["需要改进的地方1", "需要改进的地方2"],
    "career_highlights": ["职业亮点1", "职业亮点2"],
    "job_preference": "推测的职位偏好",
    "salary_expectation": "推测的薪资期望（如果可推断）"
}}"""

        response = self.chat(prompt)
        if response:
            try:
                # 尝试解析JSON
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    return json.loads(json_match.group())
            except (json.JSONDecodeError, ValueError):
                pass

        # 返回默认分析结果
        return self._default_analysis()

    def _default_analysis(self) -> Dict:
        return {
            "basic_info": {"name": "", "education": "本科", "working_years": 2},
            "skills": {
                "technical": ["Python", "JavaScript", "SQL"],
                "soft": ["沟通能力", "团队协作", "问题解决"],
                "tools": ["Git", "Docker", "Linux"]
            },
            "experience_years": 2,
            "projects": [
                {"name": "智能面试系统", "description": "基于LLM的面试系统", "tech_stack": "Python, FastAPI, Vue", "role": "全栈开发"}
            ],
            "strengths": ["技术基础扎实", "学习能力强", "善于沟通"],
            "weaknesses": ["项目经验相对较少", "需要更多大型项目历练"],
            "career_highlights": ["独立完成多个项目", "熟练使用主流技术栈"],
            "job_preference": "软件工程师",
            "salary_expectation": "15K-25K"
        }


class QuestionGenerationAgent(BaseAgent):
    """问题生成代理 - 生成针对性的面试问题"""

    def __init__(self):
        super().__init__(
            "面试官",
            """你是一位经验丰富的技术面试官，擅长根据候选人的背景和职位要求，
            生成精准、有深度的面试问题。你的问题应该：
            1. 基于候选人的实际项目经验和技术栈
            2. 能够区分候选人的真实能力和表面了解
            3. 从简单到复杂，循序渐进
            4. 既有技术深度，也有实际应用场景

            请像一位资深面试官一样提问。"""
        )

    def generate_questions(self, resume_analysis: Dict, job_type: str, num: int = 5,
                         interview_history: List[Dict] = None) -> List[Dict]:
        """生成面试问题列表（带类型和意图）"""
        history = interview_history or []

        # 基于历史问题避免重复
        asked_topics = set()
        for h in history:
            asked_topics.add(h.get('topic', ''))

        prompt = f"""基于以下简历分析和职位类型，生成{num}个高质量的技术面试问题。

职位类型：{job_type}

候选人背景分析：
- 技术栈：{', '.join(resume_analysis.get('skills', {}).get('technical', []))}
- 工具/框架：{', '.join(resume_analysis.get('skills', {}).get('tools', []))}
- 工作经验：{resume_analysis.get('experience_years', 0)}年
- 项目经验：{', '.join([p.get('name', '') for p in resume_analysis.get('projects', [])])}
- 优势：{', '.join(resume_analysis.get('strengths', []))}
- 需要改进：{', '.join(resume_analysis.get('weaknesses', []))}

已问过的问题主题：{', '.join(asked_topics) if asked_topics else '无'}

请生成{num}个不同主题的面试问题，每个问题包含：
- question: 问题内容
- type: 问题类型（technical/behavioral/project/coding/system_design）
- topic: 问题主题（用于去重）
- difficulty: 难度（1-5，5最难）
- intent: 出题意图

请以JSON数组格式返回。"""

        response = self.chat(prompt)
        if response:
            try:
                json_match = re.search(r'\[[\s\S]*\]', response)
                if json_match:
                    questions = json.loads(json_match.group())
                    if isinstance(questions, list) and len(questions) >= num:
                        return questions[:num]
            except (json.JSONDecodeError, ValueError):
                pass

        return self._default_questions(job_type, num)

    def _default_questions(self, job_type: str, num: int) -> List[Dict]:
        defaults = [
            {"question": f"请介绍一下你在{job_type}领域最成功的项目经历？", "type": "project", "topic": "项目经历", "difficulty": 3, "intent": "了解候选人的实际项目经验和贡献"},
            {"question": "你在项目中遇到的最大技术挑战是什么？如何解决的？", "type": "technical", "topic": "技术挑战", "difficulty": 4, "intent": "评估问题解决能力和技术深度"},
            {"question": "请描述你如何保证代码质量和可维护性？", "type": "technical", "topic": "代码质量", "difficulty": 3, "intent": "了解工程实践能力"},
            {"question": "你对未来技术发展的看法是什么？", "type": "behavioral", "topic": "技术视野", "difficulty": 2, "intent": "评估学习热情和技术视野"},
            {"question": "你最擅长的技术领域是什么？能深入讲解一下吗？", "type": "technical", "topic": "技术深度", "difficulty": 5, "intent": "评估技术深度和表达能力"}
        ]
        return defaults[:num]


class FollowUpQuestionAgent(BaseAgent):
    """追问代理 - 根据候选人回答动态生成追问"""

    def __init__(self):
        super().__init__(
            "追问专家",
            """你是一位擅长追问的面试官，能够根据候选人的回答进行深入追问。
            你的追问应该：
            1. 顺着候选人的回答继续深入挖掘
            2. 针对候选人提到的具体细节提问
            3. 发现回答中的模糊或矛盾之处进行澄清
            4. 引导候选人展示更深层的能力

            每次追问应该简短、精准、直击要害。"""
        )

    def generate_followup(self, question: str, answer: str, resume_analysis: Dict) -> Optional[str]:
        """根据回答生成追问"""
        prompt = f"""基于以下面试问答对，判断是否需要追问，并生成追问问题。

原始问题：{question}
候选人回答：{answer}

候选人背景：
- 技术栈：{', '.join(resume_analysis.get('skills', {}).get('technical', []))}
- 项目经验：{[p.get('name', '') for p in resume_analysis.get('projects', [])]}

如果回答：
1. 过于笼统模糊 → 追问具体细节
2. 提到但未展开 → 追问深入展开
3. 存在矛盾或疑点 → 追问澄清
4. 回答精彩 → 追问更深入的思考
5. 回答简短 → 引导补充更多信息

请判断是否需要追问。如果需要，请生成一个精准的追问问题（50字以内）。
如果不需要追问，请回复"不需要追问"。

请以JSON格式返回：{{"need_followup": true/false, "followup_question": "追问内容"或null}}"""

        response = self.chat(prompt, temperature=0.5)
        if response:
            try:
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    result = json.loads(json_match.group())
                    if not result.get("need_followup"):
                        return None
                    return result.get("followup_question")
            except (json.JSONDecodeError, ValueError):
                pass
        return None


class AnswerEvaluationAgent(BaseAgent):
    """答案评估代理 - 全面评估候选人回答"""

    def __init__(self):
        super().__init__(
            "面试评估专家",
            """你是一位严格的技术面试评估专家，擅长客观、公正、多维度地评估候选人的回答。
            你的评估必须严格：
            1. 绝不给虚假高分，必须基于实际表现评分
            2. 对于模糊、空洞、敷衍的回答必须给低分（1-2分）
            3. 只有真正有价值、有深度、有具体例子的回答才能给高分（4-5分）
            4. 区分"知道概念"和"真正掌握和运用"

            评分标准（必须严格执行）：
            - 5分：回答极其优秀，超出预期，有独到见解
            - 4分：回答良好，能结合实际经验，有一定深度
            - 3分：回答基本合格，但缺乏深度或具体例子
            - 2分：回答过于简单、模糊或存在错误
            - 1分：回答完全错误或敷衍了事"""
        )

    def evaluate_answer(self, question: str, answer: str, job_type: str,
                       resume_analysis: Dict, followup_answer: str = None) -> Dict:
        """评估回答（可包含追问的回答）"""
        combined_answer = answer
        if followup_answer:
            combined_answer = f"初始回答：{answer}\n\n追问回答：{followup_answer}"

        # 检查回答质量 - 只检测明显敷衍的回答
        answer_length = len(answer.strip())
        is_short_answer = answer_length < 5
        is_vague_or_empty = answer.strip() in ['无', '没有', '不知道', '暂无', '好', '很好', '不错', '还行', '可以', '是的', '对', '嗯', '呃', '...', '。', '空白', '', '随便', '无所谓']

        # 答非所问检测 - 只针对特别明显的情况
        irrelevant_keywords = ['不会', '学过的', '忘记了']
        is_irrelevant = answer.strip() in ['不会', '不会的', '忘记了', '学过的', '没学过'] or (len(answer.strip()) < 20 and any(kw in answer for kw in ['不会', '忘记了']))

        # 如果是敷衍或答非所问的回答，使用严格评估
        if is_vague_or_empty or is_short_answer or is_irrelevant:
            return {
                "scores": {
                    "relevance": 0 if is_vague_or_empty else 1,
                    "accuracy": 1,
                    "depth": 0 if is_vague_or_empty else 1,
                    "completeness": 0 if is_vague_or_empty else 1,
                    "expression": 1,
                    "evidence": 0 if is_vague_or_empty else 1
                },
                "overall_score": 0.5 if is_vague_or_empty else 1.0,
                "strengths": [],
                "weaknesses": ["回答敷衍或空白", "缺乏有价值信息"],
                "feedback": "回答过于简单、敷衍或答非所问，无法有效评估候选人的真实能力水平。请结合具体项目经验和技术细节进行回答。",
                "suggestions": ["结合具体项目经验回答", "深入展开技术细节", "说明解决问题的具体方法"]
            }

        prompt = f"""你是一位专业、公正的面试评估专家。请客观评估以下面试回答，给予合理分数。

职位类型：{job_type}
问题：{question}
回答：{combined_answer}

候选人背景：
- 技术栈：{', '.join(resume_analysis.get('skills', {}).get('technical', []))}
- 工作经验：{resume_analysis.get('experience_years', 0)}年
- 项目经验：{[p.get('description', '') for p in resume_analysis.get('projects', [])]}

评分标准（客观评分，0-5分）：
0分：完全错误、敷衍、答非所问
1分：回答极不完整，只有几个字
2分：回答过于简单，有基本概念但缺乏深度
3分：回答基本合格，有一定内容但不深入
4分：回答良好，能结合实际经验，有一定深度
5分：回答优秀，有独到见解，有具体项目/案例支撑

请以JSON格式返回：
{{
    "scores": {{
        "relevance": 分数(0-5),
        "accuracy": 分数(0-5),
        "depth": 分数(0-5),
        "completeness": 分数(0-5),
        "expression": 分数(0-5),
        "evidence": 分数(0-5)
    }},
    "overall_score": 综合评分（0-5分，保留1位小数）,
    "strengths": ["优点1", "优点2"],
    "weaknesses": ["缺点1", "缺点2"],
    "feedback": "详细反馈（20字以上）",
    "suggestions": ["改进建议1", "改进建议2"]
}}"""

        response = self.chat(prompt, temperature=0.5)
        if response:
            try:
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    result = json.loads(json_match.group())
                    scores = result.get('scores', {})
                    if scores:
                        result['overall_score'] = round(sum(scores.values()) / len(scores), 1)
                    return result
            except (json.JSONDecodeError, ValueError):
                pass

        return self._default_evaluation()

    def _default_evaluation(self) -> Dict:
        return {
            "scores": {
                "relevance": 2,
                "accuracy": 2,
                "depth": 2,
                "completeness": 2,
                "expression": 2,
                "evidence": 2
            },
            "overall_score": 2.0,
            "strengths": ["态度认真"],
            "weaknesses": ["内容较为简单", "缺乏深入展开"],
            "feedback": "回答有一定内容，但缺乏深度和具体项目经验支撑。建议结合实际项目经验详细展开回答。",
            "suggestions": ["增加项目案例", "深入技术细节", "补充解决问题的具体方法"]
        }


class DialogueManagerAgent(BaseAgent):
    """对话管理代理 - 控制面试流程"""

    def __init__(self):
        super().__init__(
            "面试对话管理专家",
            """你是一位专业的面试对话管理专家，负责：
            1. 控制面试节奏和流程
            2. 判断是否继续追问或进入下一问题
            3. 监控候选人状态和表现
            4. 决定何时结束面试

            你要确保面试高效、专业、公平。"""
        )

    def should_continue_interview(self, current_question: str, current_answer: str,
                                  current_evaluation: Dict, all_answers: List[Dict],
                                  total_questions: int) -> Dict:
        """判断是否继续面试"""
        answered_count = len(all_answers)
        scores = [a.get('evaluation', {}).get('overall_score', 3) for a in all_answers]
        avg_score = sum(scores) / len(scores) if scores else 3.0

        prompt = f"""请评估当前面试状态，决定下一步行动：

面试进度：已回答 {answered_count}/{total_questions} 题
当前问题：{current_question[:100]}...
当前回答：{current_answer[:100]}...
当前评估：{current_evaluation.get('overall_score', 0)}分
历史平均分：{avg_score:.1f}分

请判断：
1. 是否需要追问（如果当前回答不够深入）
2. 是否可以进入下一问题
3. 是否应该结束面试（如果表现明显不合格或已足够优秀）

请以JSON格式返回：
{{
    "action": "continue/followup/end",
    "reason": "判断理由",
    "encouragement": "给候选人的鼓励性话语（如果需要）",
    "warning": "给候选人的提醒（如果需要）"
}}"""

        response = self.chat(prompt, temperature=0.3)
        if response:
            try:
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    return json.loads(json_match.group())
            except (json.JSONDecodeError, ValueError):
                pass

        return {"action": "continue" if answered_count < total_questions else "end", "reason": "默认决策"}

    def generate_interview_summary(self, all_evaluations: List[Dict], resume_analysis: Dict,
                                   job_type: str) -> Dict:
        """生成面试总结报告"""
        if not all_evaluations:
            return {"error": "没有评估数据"}

        scores = [e.get('overall_score', 0) for e in all_evaluations]
        avg_score = sum(scores) / len(scores) if scores else 0

        # 收集所有优点和缺点
        all_strengths = []
        all_weaknesses = []
        for e in all_evaluations:
            all_strengths.extend(e.get('strengths', []))
            all_weaknesses.extend(e.get('weaknesses', []))

        # 统计各维度得分
        dimensions = ['relevance', 'accuracy', 'depth', 'completeness', 'expression', 'evidence']
        dimension_scores = {}
        for dim in dimensions:
            dim_scores = [e.get('scores', {}).get(dim, 0) for e in all_evaluations if e.get('scores', {}).get(dim)]
            dimension_scores[dim] = round(sum(dim_scores) / len(dim_scores), 1) if dim_scores else 0

        prompt = f"""基于以下面试评估，生成一份综合面试报告：

职位类型：{job_type}
候选人背景：技术栈 {', '.join(resume_analysis.get('skills', {}).get('technical', []))}

面试表现：
- 平均分：{avg_score:.1f}/5
- 各维度得分：{dimension_scores}
- 回答的问题：{[e.get('question', '')[:50] for e in all_evaluations]}

优点汇总：{', '.join(set(all_strengths[:5]))}
缺点汇总：{', '.join(set(all_weaknesses[:5]))}

请生成一份专业的面试报告，包括：
1. 综合评价（100字以上）
2. 录用建议（强烈推荐/推荐/待定/不推荐）
3. 薪资建议范围
4. 后续培养建议

请以JSON格式返回：
{{
    "summary": "综合评价（100字以上）",
    "recommendation": "强烈推荐/推荐/待定/不推荐",
    "recommendation_reason": "推荐理由",
    "salary_suggestion": "薪资建议",
    "training_suggestions": ["建议1", "建议2", "建议3"],
    "strengths_summary": ["突出优点1", "突出优点2", "突出优点3"],
    "areas_for_improvement": ["需改进1", "需改进2", "需改进3"]
}}"""

        response = self.chat(prompt, temperature=0.3)
        if response:
            try:
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    return json.loads(json_match.group())
            except (json.JSONDecodeError, ValueError):
                pass

        return {
            "summary": f"候选人在{job_type}岗位的面试中表现中等，平均得分{avg_score:.1f}分。",
            "recommendation": "待定",
            "recommendation_reason": "需要更多项目经验来证明能力",
            "salary_suggestion": "15K-20K",
            "training_suggestions": ["加强项目实践", "深入技术原理", "提升表达技巧"],
            "strengths_summary": ["基础扎实", "学习能力强"],
            "areas_for_improvement": ["项目经验", "技术深度"]
        }


class VoiceProcessingAgent:
    """语音处理代理 - 处理语音识别"""

    def __init__(self):
        from services.voice_service import VoiceService
        self.voice_service = VoiceService()

    def process_audio_answer(self, audio_file: str) -> Optional[str]:
        """处理语音回答"""
        return self.voice_service.speech_to_text(audio_file)


class CollaborationCoordinator:
    """多智能体协作协调器 - 实现真正的智能体协作"""

    def __init__(self):
        self.resume_agent = ResumeAnalysisAgent()
        self.question_agent = QuestionGenerationAgent()
        self.followup_agent = FollowUpQuestionAgent()
        self.evaluation_agent = AnswerEvaluationAgent()
        self.dialogue_agent = DialogueManagerAgent()
        self.voice_agent = VoiceProcessingAgent()

    def start_interview(self, resume_analysis: Dict, job_type: str, num_questions: int = 5) -> Dict:
        """启动面试：生成初始问题列表"""
        questions = self.question_agent.generate_questions(
            resume_analysis, job_type, num_questions
        )
        return {
            "questions": questions,
            "current_index": 0,
            "answers": [],
            "status": "in_progress"
        }

    def process_answer(self, question: Dict, answer: str, resume_analysis: Dict,
                      interview_state: Dict) -> Dict:
        """处理回答：评估 + 可能的追问 + 决定下一步"""
        # 评估当前回答
        evaluation = self.evaluation_agent.evaluate_answer(
            question['question'], answer,
            resume_analysis.get('job_preference', '软件工程师'),
            resume_analysis
        )

        # 检查是否需要追问
        followup_question = self.followup_agent.generate_followup(
            question['question'], answer, resume_analysis
        )

        # 记录回答
        answer_record = {
            "question": question['question'],
            "answer": answer,
            "evaluation": evaluation,
            "followup_question": followup_question
        }

        # 更新面试状态
        interview_state['answers'].append(answer_record)
        interview_state['current_index'] += 1

        # 对话管理决策
        decision = self.dialogue_agent.should_continue_interview(
            question['question'], answer, evaluation,
            interview_state['answers'],
            len(interview_state['questions'])
        )

        return {
            "evaluation": evaluation,
            "followup_question": followup_question,
            "decision": decision,
            "interview_state": interview_state
        }

    def generate_final_report(self, interview_state: Dict, resume_analysis: Dict,
                              job_type: str) -> Dict:
        """生成最终面试报告"""
        evaluations = [a['evaluation'] for a in interview_state['answers']]
        return self.dialogue_agent.generate_interview_summary(
            evaluations, resume_analysis, job_type
        )


# 全局协作协调器
collaboration_coordinator = CollaborationCoordinator()
