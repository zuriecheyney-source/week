"""
智能客服系统：接待员、问题分析师、解决方案专家
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
from src.memory.memory_store import MemoryStore
from src.tools.knowledge_base import KnowledgeBaseTool
from src.tools.web_search import WebSearchTool


class CustomerServiceRole(Enum):
    """客服系统角色"""
    RECEPTIONIST = "receptionist"
    PROBLEM_ANALYST = "problem_analyst"
    SOLUTION_EXPERT = "solution_expert"


class CustomerServiceReceptionist(BaseAgent):
    """客服接待员"""
    
    def __init__(self):
        super().__init__(AgentRole.RECEPTIONIST)
    
    def _get_system_prompt(self) -> str:
        return """你是专业的客服接待员。职责包括：
1. 热情接待客户
2. 收集基本信息
3. 问题分类和优先级评估
4. 智能路由到合适专家
5. 提供初步安抚和指导

你的回复应该：
- 友好专业
- 清晰简洁
- 关注客户需求
- 提供明确指引
- 及时转接专家"""
    
    async def process(self, state: AgentState) -> AgentState:
        """处理客户咨询"""
        state = self.set_current_agent(state)
        
        if not state.customer_query:
            # 模拟接待新客户
            welcome_msg = await self.call_llm("生成一个专业的客服欢迎语")
            state = self.add_message_to_history(state, welcome_msg)
        
        if state.customer_query:
            # 分析问题并路由
            analysis = await self._analyze_customer_issue(state.customer_query.original_message)
            state.metadata["receptionist_analysis"] = analysis
            
            # 决定路由
            if analysis["severity"] in ["high", "critical"]:
                target_agent = CustomerServiceRole.SOLUTION_EXPERT.value
                reason = f"高严重性问题：{analysis['category']}"
            else:
                target_agent = CustomerServiceRole.PROBLEM_ANALYST.value
                reason = f"标准问题分析：{analysis['category']}"
            
            handoff_msg = f"[转接至{target_agent}] 原因：{reason}"
            state = self.add_message_to_history(state, handoff_msg, MessageType.HANDOFF)
            state.handoff_reason = reason
        
        return state
    
    async def _analyze_customer_issue(self, message: str) -> Dict[str, Any]:
        """分析客户问题"""
        prompt = f"""
        分析客户问题并分类：
        "{message}"
        
        返回JSON格式：
        {{
            "category": "technical|billing|account|general",
            "severity": "low|medium|high|critical",
            "keywords": ["关键词1", "关键词2"],
            "sentiment": "positive|neutral|negative",
            "urgency": "low|medium|high|critical"
        }}
        """

        # 简单解析（实际应用中应使用JSON解析）
        return {
            "category": "technical" if "技术" in message or "错误" in message else "general",
            "severity": "medium",
            "keywords": ["客服", "咨询"],
            "sentiment": "neutral",
            "urgency": "medium"
        }


class CustomerServiceAnalyst(BaseAgent):
    """客服问题分析师"""
    
    def __init__(self):
        super().__init__(AgentRole.PROBLEM_ANALYST)
    
    def _get_system_prompt(self) -> str:
        return """你是专业的问题分析师。职责包括：
1. 深度分析客户问题
2. 识别根本原因
3. 评估问题影响范围
4. 制定解决方案策略
5. 决定是否需要专家介入

你的分析应该：
- 系统全面
- 逻辑清晰
- 数据驱动
- 注重细节
- 提供可行建议"""
    
    async def process(self, state: AgentState) -> AgentState:
        """深度分析问题"""
        state = self.set_current_agent(state)
        
        if state.customer_query:
            # 进行深度分析
            analysis = await self._deep_analysis(state.customer_query.original_message)
            state.metadata["analyst_deep_analysis"] = analysis
            
            # 生成分析报告
            report = await self._generate_analysis_report(analysis)
            state = self.add_message_to_history(state, report)
            
            # 决定是否需要专家介入
            if analysis["complexity"] == "high" or analysis["impact"] == "wide":
                handoff_msg = "[转接至solution_expert] 需要专家深度解决方案"
                state = self.add_message_to_history(state, handoff_msg, MessageType.HANDOFF)
                state.handoff_reason = "复杂问题需要专家处理"
        
        return state
    
    async def _deep_analysis(self, message: str) -> Dict[str, Any]:
        """深度分析问题"""
        prompt = f"""
        对客户问题进行深度分析：
        "{message}"
        
        分析维度：
        1. 问题复杂度：simple|medium|complex
        2. 影响范围：individual|team|wide|enterprise
        3. 解决难度：easy|medium|hard|expert
        4. 时间紧迫度：low|medium|high|urgent
        5. 资源需求：low|medium|high
        """

        return {
            "complexity": "medium",
            "impact": "team",
            "difficulty": "medium",
            "urgency": "medium",
            "resources": "medium"
        }
    
    async def _generate_analysis_report(self, analysis: Dict[str, Any]) -> str:
        """生成分析报告"""
        return f"""
问题分析报告：
- 复杂度：{analysis['complexity']}
- 影响范围：{analysis['impact']}
- 解决难度：{analysis['difficulty']}
- 时间紧迫度：{analysis['urgency']}
- 资源需求：{analysis['resources']}

初步建议：根据分析结果，建议采用标准处理流程，如问题持续将升级至专家处理。
        """


class CustomerServiceExpert(BaseAgent):
    """客服解决方案专家"""
    
    def __init__(self):
        super().__init__(AgentRole.SOLUTION_EXPERT)
    
    def _get_system_prompt(self) -> str:
        return """你是资深的解决方案专家。职责包括：
1. 提供专家级解决方案
2. 制定详细实施步骤
3. 评估方案可行性
4. 提供备选方案
5. 制定跟进计划

你的解决方案应该：
- 专业权威
- 详细具体
- 可操作性强
- 考虑风险
- 提供资源支持"""
    
    async def process(self, state: AgentState) -> AgentState:
        """提供专家解决方案"""
        state = self.set_current_agent(state)
        
        if state.customer_query:
            # Keep structured solution for downstream consumers
            solution = await self._create_expert_solution(state.customer_query.original_message)
            state.metadata["expert_solution"] = solution

            tool_context = state.metadata.get("tool_context", {}) if state.metadata else {}
            kb_results = tool_context.get("knowledge_base", []) or []
            web_results = tool_context.get("web_search", []) or []

            kb_text = "\n".join(
                [
                    f"- {a.get('title', '')}: {a.get('content', '')}"
                    for a in kb_results
                ][:3]
            )

            web_text = "\n".join(
                [
                    f"- {r.get('title', '')} ({r.get('url', '')}): {r.get('snippet', '')}"
                    for r in web_results
                ][:3]
            )

            prompt = f"""
你正在处理一条客户咨询，请给出可执行、结构清晰的解决方案。

客户问题：{state.customer_query.original_message}

（可选）接待员信息：{state.metadata.get('receptionist_analysis') if state.metadata else None}
（可选）分析师信息：{state.metadata.get('analyst_deep_analysis') if state.metadata else None}

本地知识库命中：
{kb_text if kb_text else '无'}

联网检索结果：
{web_text if web_text else '无'}

要求：
1) 先给一句话结论
2) 给分步操作（3-7步）
3) 如果需要用户补充信息，列出需要问的3个问题
4) 风险/注意事项
"""

            final_answer = await self.call_llm(prompt)
            state.metadata["final_answer"] = final_answer
            state = self.add_message_to_history(state, final_answer)
         
        return state
    
    async def _create_expert_solution(self, message: str) -> Dict[str, Any]:
        """创建专家解决方案"""
        prompt = f"""
        为客户问题制定专家解决方案：
        "{message}"
        
        方案要素：
        1. 解决方案类型：immediate|temporary|permanent
        2. 实施步骤：详细步骤列表
        3. 预估时间：具体时间范围
        4. 成功概率：百分比
        5. 风险评估：潜在风险和缓解措施
        6. 资源需求：所需工具和人员
        """

        return {
            "type": "permanent",
            "steps": ["步骤1：问题确认", "步骤2：方案制定", "步骤3：实施解决", "步骤4：验证结果"],
            "estimated_time": "2-4小时",
            "success_rate": 0.85,
            "risks": ["实施风险", "时间风险"],
            "resources": ["技术支持", "系统权限"]
        }
    
    async def _generate_detailed_solution(self, solution: Dict[str, Any]) -> str:
        """生成详细解决方案"""
        return f"""
专家解决方案：

方案类型：{solution['type']}
预估时间：{solution['estimated_time']}
成功概率：{solution['success_rate']*100:.1f}%

详细步骤：
{chr(10).join([f"{i+1}. {step}" for i, step in enumerate(solution['steps'])])}

风险评估：
{chr(10).join([f"- {risk}" for risk in solution['risks']])}

所需资源：
{chr(10).join([f"- {resource}" for resource in solution['resources']])}

后续跟进：建议24小时内确认解决效果，如有问题及时联系。
        """


class CustomerServiceSystem:
    """智能客服系统"""
    
    def __init__(self):
        self.memory_store = MemoryStore()
        self.knowledge_base = KnowledgeBaseTool()
        self.web_search = WebSearchTool()
        self.receptionist = CustomerServiceReceptionist()
        self.analyst = CustomerServiceAnalyst()
        self.expert = CustomerServiceExpert()
    
    async def process_customer_inquiry(self, session_id: str, message: str) -> Dict[str, Any]:
        """处理客户咨询"""
        from src.models.state import CustomerQuery, Message
        import uuid
        
        # 创建客户查询
        customer_query = CustomerQuery(
            query_id=str(uuid.uuid4()),
            original_message=message,
            category="general",
            priority="medium"
        )
        
        # 创建初始状态
        user_message = Message(
            id=str(uuid.uuid4()),
            type=MessageType.USER_QUERY,
            sender="customer",
            content=message
        )
        
        state = AgentState(
            customer_query=customer_query,
            conversation_history=[user_message]
        )

        tool_errors: List[str] = []

        try:
            kb_results = await self.knowledge_base.search_knowledge_base(message, limit=3)
        except Exception as e:
            kb_results = []
            tool_errors.append(f"knowledge_base_error: {e}")

        try:
            web_results = []
            if not kb_results:
                web_results = await self.web_search.search_web(message, num_results=3)
        except Exception as e:
            web_results = []
            tool_errors.append(f"web_search_error: {e}")

        state.metadata["tool_context"] = {
            "knowledge_base": kb_results,
            "web_search": web_results,
            "tool_errors": tool_errors,
        }

        try:
            state = await self.receptionist.process(state)
        except Exception as e:
            state.metadata["receptionist_error"] = str(e)

        try:
            state = await self.analyst.process(state)
        except Exception as e:
            state.metadata["analyst_error"] = str(e)

        try:
            state = await self.expert.process(state)
        except Exception as e:
            expert_error = str(e)
            state.metadata["expert_error"] = expert_error

            # Fallback: still try to provide an answer so the客服功能不会“没了”
            try:
                fallback_prompt = f"""
你是智能客服解决方案专家。用户问题：{message}

请直接给出可执行的建议（分步），并列出你还需要问用户的3个澄清问题。
"""
                fallback_answer = await self.expert.call_llm(fallback_prompt)
            except Exception as e2:
                fallback_llm_error = str(e2)
                state.metadata["fallback_llm_error"] = fallback_llm_error

                # Provide a short, safe reason to help debugging without leaking secrets.
                reason = expert_error or fallback_llm_error
                reason = (reason or "").strip().replace("\n", " ")
                if len(reason) > 240:
                    reason = reason[:240] + "..."

                if reason:
                    fallback_answer = (
                        "抱歉，我现在无法调用模型来生成完整方案。"
                        f"（原因：{reason}）\n"
                        "你可以稍后重试，或补充更多信息（品牌/预算/用途/偏好）。"
                    )
                else:
                    fallback_answer = "抱歉，我现在无法调用模型来生成完整方案。请稍后重试，或补充更多信息（品牌/预算/用途/偏好）。"

            state.metadata["final_answer"] = fallback_answer
            state = self.expert.add_message_to_history(state, fallback_answer)

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
            "original_message": message,
            "agent_path": metadata.get("agent_path", []),
            "analysis": metadata.get("analyst_deep_analysis"),
            "solution": metadata.get("expert_solution"),
            "conversation": [getattr(msg, "content", str(msg)) for msg in history],
            "answer": _extract_answer(history)
        }
    
    async def cleanup(self):
        """清理资源"""
        await self.web_search.close()
        await self.memory_store.close()
