"""
医疗咨询系统：问诊助手、诊断分析师、健康建议专家
"""
import sys
from pathlib import Path
from typing import Dict, Any, List
from enum import Enum

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.models.state import AgentState, AgentRole, MessageType, Message, CustomerQuery
from src.agents.base_agent import BaseAgent
from src.workflow.graph import MultiAgentWorkflow
from src.memory.memory_store import MemoryStore


class MedicalRole(Enum):
    """医疗系统角色"""
    TRIAGE_ASSISTANT = "triage_assistant"
    DIAGNOSTIC_ANALYST = "diagnostic_analyst"
    HEALTH_ADVISOR = "health_advisor"


class TriageAssistant(BaseAgent):
    """问诊助手"""
    
    def __init__(self):
        super().__init__(AgentRole.RECEPTIONIST)
    
    def _get_system_prompt(self) -> str:
        return """你是专业的医疗问诊助手。职责包括：
1. 初步了解患者症状
2. 评估紧急程度
3. 收集基本病史信息
4. 判断是否需要紧急处理
5. 引导至合适的医疗专家

重要提醒：
- 不能替代医生诊断
- 紧急情况建议立即就医
- 保护患者隐私
- 提供专业指导
- 强调就医重要性"""
    
    async def process(self, state: AgentState) -> AgentState:
        """处理问诊"""
        state = self.set_current_agent(state)
        
        if not state.customer_query:
            welcome_msg = await self.call_llm("生成专业的医疗咨询欢迎语，包含免责声明")
            state = self.add_message_to_history(state, welcome_msg)
        
        if state.customer_query:
            # 分析症状
            symptom_analysis = await self._analyze_symptoms(state.customer_query.original_message)
            state.metadata["symptom_analysis"] = symptom_analysis
            
            # 评估紧急程度
            urgency = await self._assess_urgency(symptom_analysis)
            state.metadata["urgency_assessment"] = urgency
            
            # 生成问诊报告
            triage_report = await self._generate_triage_report(symptom_analysis, urgency)
            state = self.add_message_to_history(state, triage_report)
            
            # 决定后续处理
            if urgency["level"] in ["high", "emergency"]:
                handoff_msg = "[转接至health_advisor] 紧急情况需要专家建议"
                state = self.add_message_to_history(state, handoff_msg, MessageType.HANDOFF)
                state.handoff_reason = "紧急情况需要专家处理"
            elif symptom_analysis["complexity"] == "high":
                handoff_msg = "[转接至diagnostic_analyst] 需要专业诊断分析"
                state = self.add_message_to_history(state, handoff_msg, MessageType.HANDOFF)
                state.handoff_reason = "复杂症状需要诊断分析"
        
        return state
    
    async def _analyze_symptoms(self, message: str) -> Dict[str, Any]:
        """分析症状"""
        prompt = f"""
        分析患者描述的症状：
        "{message}"
        
        分析维度：
        1. 症状类型：pain|fever|digestive|respiratory|skin|neurological|other
        2. 严重程度：mild|moderate|severe
        3. 持续时间：hours|days|weeks|months
        4. 影响程度：low|medium|high
        5. 伴随症状：相关症状列表
        """
        
        return {
            "symptom_type": "general",
            "severity": "moderate",
            "duration": "days",
            "impact": "medium",
            "accompanying_symptoms": ["头痛", "乏力"],
            "complexity": "medium"
        }
    
    async def _assess_urgency(self, symptoms: Dict[str, Any]) -> Dict[str, Any]:
        """评估紧急程度"""
        # 紧急症状关键词
        emergency_keywords = ["胸痛", "呼吸困难", "昏厥", "严重出血", "剧烈疼痛"]
        
        message = symptoms.get("message", "")
        is_emergency = any(keyword in message for keyword in emergency_keywords)
        
        if is_emergency:
            return {
                "level": "emergency",
                "recommendation": "立即就医",
                "time_frame": "立即",
                "action": "call_emergency"
            }
        elif symptoms["severity"] == "severe":
            return {
                "level": "high",
                "recommendation": "尽快就医",
                "time_frame": "24小时内",
                "action": "schedule_appointment"
            }
        else:
            return {
                "level": "medium",
                "recommendation": "常规就医",
                "time_frame": "3-5天内",
                "action": "consult_doctor"
            }
    
    async def _generate_triage_report(self, symptoms: Dict[str, Any], urgency: Dict[str, Any]) -> str:
        """生成问诊报告"""
        return f"""
初步问诊报告：

症状分析：
- 症状类型：{symptoms['symptom_type']}
- 严重程度：{symptoms['severity']}
- 持续时间：{symptoms['duration']}
- 影响程度：{symptoms['impact']}
- 伴随症状：{', '.join(symptoms['accompanying_symptoms'])}

紧急程度评估：
- 紧急级别：{urgency['level']}
- 建议行动：{urgency['recommendation']}
- 时间要求：{urgency['time_frame']}

重要提醒：
1. 此为初步评估，不能替代专业医生诊断
2. 如症状加重或出现紧急情况，请立即就医
3. 建议记录症状变化，便于医生诊断
4. 保持休息，避免剧烈活动
        """


class DiagnosticAnalyst(BaseAgent):
    """诊断分析师"""
    
    def __init__(self):
        super().__init__(AgentRole.PROBLEM_ANALYST)
    
    def _get_system_prompt(self) -> str:
        return """你是专业的诊断分析师。职责包括：
1. 深度分析症状信息
2. 识别可能的疾病原因
3. 评估诊断可能性
4. 提供检查建议
5. 制定诊断思路

你的分析应该：
- 科学严谨
- 全面系统
- 逻辑清晰
- 基于证据
- 客观准确"""
    
    async def process(self, state: AgentState) -> AgentState:
        """进行诊断分析"""
        state = self.set_current_agent(state)
        
        if state.customer_query:
            # 深度症状分析
            deep_analysis = await self._deep_symptom_analysis(state.customer_query.original_message)
            state.metadata["deep_analysis"] = deep_analysis
            
            # 可能诊断
            possible_diagnoses = await self._identify_possible_diagnoses(deep_analysis)
            state.metadata["possible_diagnoses"] = possible_diagnoses
            
            # 检查建议
            exam_recommendations = await self._recommend_examinations(possible_diagnoses)
            state.metadata["exam_recommendations"] = exam_recommendations
            
            # 生成诊断报告
            diagnostic_report = await self._generate_diagnostic_report(deep_analysis, possible_diagnoses, exam_recommendations)
            state = self.add_message_to_history(state, diagnostic_report)
            
            # 转接健康建议专家
            handoff_msg = "[转接至health_advisor] 需要健康建议和治疗方案"
            state = self.add_message_to_history(state, handoff_msg, MessageType.HANDOFF)
            state.handoff_reason = "需要专业健康建议"
        
        return state
    
    async def _deep_symptom_analysis(self, message: str) -> Dict[str, Any]:
        """深度症状分析"""
        return {
            "primary_symptoms": ["头痛", "恶心"],
            "secondary_symptoms": ["乏力", "食欲不振"],
            "symptom_patterns": ["间歇性", "加重趋势"],
            "risk_factors": ["压力大", "作息不规律"],
            "medical_history": "无相关病史",
            "lifestyle_factors": ["久坐", "缺乏运动"]
        }
    
    async def _identify_possible_diagnoses(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """识别可能诊断"""
        return [
            {
                "condition": "紧张性头痛",
                "probability": 0.6,
                "evidence": ["头痛症状", "压力因素"],
                "severity": "mild"
            },
            {
                "condition": "偏头痛",
                "probability": 0.3,
                "evidence": ["头痛", "恶心"],
                "severity": "moderate"
            },
            {
                "condition": "颈椎病",
                "probability": 0.1,
                "evidence": ["头痛", "久坐因素"],
                "severity": "mild"
            }
        ]
    
    async def _recommend_examinations(self, diagnoses: List[Dict[str, Any]]) -> List[str]:
        """推荐检查项目"""
        return [
            "血压测量",
            "神经系统检查",
            "颈椎X光检查",
            "血常规检查",
            "头部CT（必要时）"
        ]
    
    async def _generate_diagnostic_report(self, analysis: Dict[str, Any], diagnoses: List[Dict], exams: List[str]) -> str:
        """生成诊断报告"""
        diagnoses_text = chr(10).join([
            f"{d['condition']}（可能性：{d['probability']*100:.0f}%）" for d in diagnoses
        ])
        
        exams_text = chr(10).join([f"- {exam}" for exam in exams])
        
        return f"""
诊断分析报告：

症状深度分析：
- 主要症状：{', '.join(analysis['primary_symptoms'])}
- 次要症状：{', '.join(analysis['secondary_symptoms'])}
- 症状模式：{', '.join(analysis['symptom_patterns'])}
- 风险因素：{', '.join(analysis['risk_factors'])}

可能诊断：
{diagnoses_text}

推荐检查：
{exams_text}

诊断思路：
1. 首先排除严重疾病
2. 根据检查结果确定诊断
3. 制定个性化治疗方案
4. 定期随访观察

注意事项：此分析仅供参考，最终诊断需由专业医生结合检查结果确定。
        """


class HealthAdvisor(BaseAgent):
    """健康建议专家"""
    
    def __init__(self):
        super().__init__(AgentRole.SOLUTION_EXPERT)
    
    def _get_system_prompt(self) -> str:
        return """你是专业的健康建议专家。职责包括：
1. 提供健康生活方式建议
2. 制定康复计划
3. 推荐预防措施
4. 指导用药安全
5. 提供营养建议

你的建议应该：
- 科学权威
- 个性化强
- 可操作性好
- 安全第一
- 全面系统"""
    
    async def process(self, state: AgentState) -> AgentState:
        """提供健康建议"""
        state = self.set_current_agent(state)
        
        if state.customer_query:
            # 获取诊断信息
            diagnoses = state.metadata.get("possible_diagnoses", [])
            urgency = state.metadata.get("urgency_assessment", {})
            
            # 制定健康计划
            health_plan = await self._create_health_plan(diagnoses, urgency)
            state.metadata["health_plan"] = health_plan
            
            # 生成建议报告
            advice_report = await self._generate_health_advice(health_plan)
            state = self.add_message_to_history(state, advice_report)
        
        return state
    
    async def _create_health_plan(self, diagnoses: List[Dict], urgency: Dict) -> Dict[str, Any]:
        """创建健康计划"""
        return {
            "immediate_actions": [
                "充分休息",
                "避免剧烈活动",
                "观察症状变化"
            ],
            "lifestyle_adjustments": [
                "规律作息",
                "适量运动",
                "压力管理",
                "均衡饮食"
            ],
            "dietary_recommendations": [
                "多喝水",
                "清淡饮食",
                "避免刺激性食物",
                "补充维生素"
            ],
            "exercise_plan": {
                "type": "轻度运动",
                "frequency": "每周3-4次",
                "duration": "30分钟",
                "activities": ["散步", "瑜伽", "太极"]
            },
            "follow_up_schedule": [
                {"time": "3天后", "action": "症状评估"},
                {"time": "1周后", "action": "复查建议"},
                {"time": "1月后", "action": "健康评估"}
            ]
        }
    
    async def _generate_health_advice(self, plan: Dict[str, Any]) -> str:
        """生成健康建议"""
        immediate_text = chr(10).join([f"- {action}" for action in plan["immediate_actions"]])
        lifestyle_text = chr(10).join([f"- {adjustment}" for adjustment in plan["lifestyle_adjustments"]])
        dietary_text = chr(10).join([f"- {recommendation}" for recommendation in plan["dietary_recommendations"]])
        follow_up_text = chr(10).join([f"{schedule['time']}：{schedule['action']}" for schedule in plan["follow_up_schedule"]])
        
        return f"""
个性化健康建议：

立即行动：
{immediate_text}

生活方式调整：
{lifestyle_text}

饮食建议：
{dietary_text}

运动计划：
- 运动类型：{plan['exercise_plan']['type']}
- 运动频率：{plan['exercise_plan']['frequency']}
- 运动时长：{plan['exercise_plan']['duration']}
- 推荐活动：{', '.join(plan['exercise_plan']['activities'])}

随访安排：
{follow_up_text}

重要提醒：
1. 如症状加重，请立即就医
2. 按医嘱用药，不可自行停药
3. 保持良好心态，有助于康复
4. 定期体检，预防疾病

免责声明：本建议仅供参考，具体治疗请遵医嘱。
        """


class MedicalSystem:
    """医疗咨询系统"""
    
    def __init__(self):
        self.memory_store = MemoryStore()
        self.triage_assistant = TriageAssistant()
        self.diagnostic_analyst = DiagnosticAnalyst()
        self.health_advisor = HealthAdvisor()
    
    async def process_medical_consultation(self, session_id: str, message: str) -> Dict[str, Any]:
        """处理医疗咨询"""
        from src.models.state import CustomerQuery, Message
        import uuid
        
        customer_query = CustomerQuery(
            query_id=str(uuid.uuid4()),
            original_message=message,
            category="medical",
            priority="high"
        )
        
        user_message = Message(
            id=str(uuid.uuid4()),
            type=MessageType.USER_QUERY,
            sender="patient",
            content=message
        )
        
        state = AgentState(
            customer_query=customer_query,
            conversation_history=[user_message]
        )

        state = await self.triage_assistant.process(state)
        state = await self.diagnostic_analyst.process(state)
        state = await self.health_advisor.process(state)

        def _extract_answer(history):
            for msg in reversed(history or []):
                if getattr(msg, "type", None) == MessageType.HANDOFF:
                    continue
                sender = getattr(msg, "sender", "")
                if sender in {"student", "patient", "client", "content_creator", "customer"}:
                    continue
                content = getattr(msg, "content", None)
                if content:
                    return content
            return ""

        metadata = state.metadata or {}
        history = state.conversation_history or []

        return {
            "session_id": session_id,
            "symptoms": metadata.get("symptom_analysis"),
            "urgency": metadata.get("urgency_assessment"),
            "diagnoses": metadata.get("possible_diagnoses"),
            "examinations": metadata.get("exam_recommendations"),
            "health_plan": metadata.get("health_plan"),
            "conversation": [getattr(msg, "content", str(msg)) for msg in history],
            "answer": _extract_answer(history)
        }
    
    async def cleanup(self):
        """清理资源"""
        await self.memory_store.close()
