from services.multi_agent_system import (
    ResumeAnalysisAgent,
    QuestionGenerationAgent,
    AnswerEvaluationAgent,
    DialogueManagerAgent,
    VoiceProcessingAgent,
    FollowUpQuestionAgent,
    CollaborationCoordinator
)
from services.resume_parser import parse_resume
from typing import Dict, List, Optional

class AgentManager:
    """多智能体管理器 - 协调各智能体工作"""

    def __init__(self):
        self.resume_agent = ResumeAnalysisAgent()
        self.question_agent = QuestionGenerationAgent()
        self.evaluation_agent = AnswerEvaluationAgent()
        self.followup_agent = FollowUpQuestionAgent()
        self.dialogue_agent = DialogueManagerAgent()
        self.voice_agent = VoiceProcessingAgent()
        self.coordinator = CollaborationCoordinator()

    def process_resume(self, file_path: str) -> Dict[str, any]:
        """处理简历：解析 + 深度分析"""
        content, success = parse_resume(file_path)
        if not success:
            raise Exception(f"简历解析失败: {content}")

        # AI深度分析简历
        analysis = self.resume_agent.analyze_resume(content)

        return {
            "content": content,
            "analysis": analysis
        }

    def generate_interview_questions(self, resume_analysis: Dict, job_type: str,
                                   num: int = 5, interview_history: List[Dict] = None) -> List[Dict]:
        """生成面试问题（带元数据）"""
        return self.question_agent.generate_questions(resume_analysis, job_type, num, interview_history)

    def evaluate_answer(self, question: str, answer: str, job_type: str,
                       resume_analysis: Dict, followup_answer: str = None) -> Dict:
        """评估答案（支持追问回答）"""
        return self.evaluation_agent.evaluate_answer(question, answer, job_type, resume_analysis, followup_answer)

    def generate_followup(self, question: str, answer: str, resume_analysis: Dict) -> Optional[str]:
        """生成追问"""
        return self.followup_agent.generate_followup(question, answer, resume_analysis)

    def process_voice_answer(self, audio_file: str) -> Optional[str]:
        """处理语音回答"""
        return self.voice_agent.process_audio_answer(audio_file)

    def should_continue_interview(self, current_question: str, current_answer: str,
                                  current_evaluation: Dict, all_answers: List[Dict],
                                  total_questions: int) -> Dict:
        """判断是否继续面试"""
        return self.dialogue_agent.should_continue_interview(
            current_question, current_answer, current_evaluation,
            all_answers, total_questions
        )

    def start_interview(self, resume_analysis: Dict, job_type: str, num_questions: int = 5) -> Dict:
        """启动面试会话"""
        return self.coordinator.start_interview(resume_analysis, job_type, num_questions)

    def process_interview_answer(self, question: Dict, answer: str,
                               resume_analysis: Dict, interview_state: Dict) -> Dict:
        """处理面试回答（协作模式）"""
        return self.coordinator.process_answer(question, answer, resume_analysis, interview_state)

    def generate_interview_report(self, interview_state: Dict, resume_analysis: Dict, job_type: str) -> Dict:
        """生成面试报告"""
        return self.coordinator.generate_final_report(interview_state, resume_analysis, job_type)

# 全局代理管理器实例
agent_manager = AgentManager()
