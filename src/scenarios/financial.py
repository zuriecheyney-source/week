"""
金融顾问系统：客户经理、风险分析师、投资顾问
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


class FinancialRole(Enum):
    """金融系统角色"""
    ACCOUNT_MANAGER = "account_manager"
    RISK_ANALYST = "risk_analyst"
    INVESTMENT_ADVISOR = "investment_advisor"


class AccountManager(BaseAgent):
    """客户经理"""
    
    def __init__(self):
        super().__init__(AgentRole.RECEPTIONIST)
    
    def _get_system_prompt(self) -> str:
        return """你是专业的客户经理。职责包括：
1. 了解客户财务状况和需求
2. 评估客户风险承受能力
3. 提供基础理财建议
4. 介绍金融产品和服务
5. 维护客户关系

你的服务应该：
- 专业可靠
- 客户至上
- 风险可控
- 量身定制
- 长期跟踪"""
    
    async def process(self, state: AgentState) -> AgentState:
        """处理客户咨询"""
        state = self.set_current_agent(state)
        
        if not state.customer_query:
            welcome_msg = await self.call_llm("生成专业的金融咨询欢迎语")
            state = self.add_message_to_history(state, welcome_msg)
        
        if state.customer_query:
            # 分析客户需求
            client_analysis = await self._analyze_client_needs(state.customer_query.original_message)
            state.metadata["client_analysis"] = client_analysis
            
            # 评估风险承受能力
            risk_profile = await self._assess_risk_profile(client_analysis)
            state.metadata["risk_profile"] = risk_profile
            
            # 生成客户报告
            client_report = await self._generate_client_report(client_analysis, risk_profile)
            state = self.add_message_to_history(state, client_report)
            
            # 决定后续处理
            if client_analysis["complexity"] == "high":
                handoff_msg = "[转接至risk_analyst] 需要专业风险评估"
                state = self.add_message_to_history(state, handoff_msg, MessageType.HANDOFF)
                state.handoff_reason = "复杂需求需要风险评估"
            elif "投资" in state.customer_query.original_message:
                handoff_msg = "[转接至investment_advisor] 需要投资建议"
                state = self.add_message_to_history(state, handoff_msg, MessageType.HANDOFF)
                state.handoff_reason = "客户需要投资指导"
        
        return state
    
    async def _analyze_client_needs(self, message: str) -> Dict[str, Any]:
        """分析客户需求"""
        return {
            "financial_goal": "wealth_growth",
            "investment_amount": "medium",
            "time_horizon": "medium_term",
            "liquidity_needs": "moderate",
            "experience_level": "intermediate",
            "complexity": "medium"
        }
    
    async def _assess_risk_profile(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """评估风险承受能力"""
        return {
            "risk_tolerance": "moderate",
            "risk_capacity": "medium",
            "investment_objective": "balanced_growth",
            "volatility_acceptance": "medium",
            "loss_tolerance": "moderate"
        }
    
    async def _generate_client_report(self, analysis: Dict[str, Any], risk: Dict[str, Any]) -> str:
        """生成客户报告"""
        return f"""
客户需求分析：

财务目标：{analysis['financial_goal']}
投资金额：{analysis['investment_amount']}
投资期限：{analysis['time_horizon']}
流动性需求：{analysis['liquidity_needs']}
经验水平：{analysis['experience_level']}

风险评估：
风险承受能力：{risk['risk_tolerance']}
风险承受度：{risk['risk_capacity']}
投资目标：{risk['investment_objective']}
波动接受度：{risk['volatility_acceptance']}

初步建议：
根据您的风险承受能力和投资目标，建议采用平衡型投资策略，兼顾收益和风险。

后续服务：
1. 如需详细风险评估，将转接风险分析师
2. 如需具体投资建议，将转接投资顾问
3. 我们将提供持续的客户服务
        """


class RiskAnalyst(BaseAgent):
    """风险分析师"""
    
    def __init__(self):
        super().__init__(AgentRole.PROBLEM_ANALYST)
    
    def _get_system_prompt(self) -> str:
        return """你是专业的风险分析师。职责包括：
1. 全面评估投资风险
2. 分析市场风险因素
3. 制定风险控制策略
4. 监控投资组合风险
5. 提供风险管理建议

你的分析应该：
- 科学严谨
- 数据驱动
- 全面系统
- 客观准确
- 风险可控"""
    
    async def process(self, state: AgentState) -> AgentState:
        """进行风险分析"""
        state = self.set_current_agent(state)
        
        if state.customer_query:
            # 获取客户信息
            client_analysis = state.metadata.get("client_analysis", {})
            risk_profile = state.metadata.get("risk_profile", {})
            
            # 深度风险分析
            risk_analysis = await self._deep_risk_analysis(client_analysis, risk_profile)
            state.metadata["risk_analysis"] = risk_analysis
            
            # 风险评估
            risk_assessment = await self._comprehensive_risk_assessment(risk_analysis)
            state.metadata["risk_assessment"] = risk_assessment
            
            # 生成风险报告
            risk_report = await self._generate_risk_report(risk_analysis, risk_assessment)
            state = self.add_message_to_history(state, risk_report)
            
            # 转接投资顾问
            handoff_msg = "[转接至investment_advisor] 基于风险评估制定投资策略"
            state = self.add_message_to_history(state, handoff_msg, MessageType.HANDOFF)
            state.handoff_reason = "需要基于风险分析的投资建议"
        
        return state
    
    async def _deep_risk_analysis(self, client: Dict, risk: Dict) -> Dict[str, Any]:
        """深度风险分析"""
        return {
            "market_risk": {
                "level": "medium",
                "factors": ["利率风险", "市场波动", "政策变化"],
                "impact": "moderate"
            },
            "credit_risk": {
                "level": "low",
                "factors": ["违约风险", "信用评级变化"],
                "impact": "low"
            },
            "liquidity_risk": {
                "level": "medium",
                "factors": ["流动性不足", "市场深度"],
                "impact": "moderate"
            },
            "operational_risk": {
                "level": "low",
                "factors": ["系统风险", "人为错误"],
                "impact": "low"
            }
        }
    
    async def _comprehensive_risk_assessment(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """综合风险评估"""
        return {
            "overall_risk_level": "medium",
            "risk_score": 6.5,
            "main_risks": ["市场风险", "流动性风险"],
            "risk_mitigation": [
                "分散投资",
                "设置止损",
                "定期调整",
                "风险监控"
            ],
            "recommended_allocation": {
                "stocks": "40%",
                "bonds": "30%",
                "cash": "20%",
                "alternatives": "10%"
            }
        }
    
    async def _generate_risk_report(self, analysis: Dict[str, Any], assessment: Dict[str, Any]) -> str:
        """生成风险报告"""
        return f"""
全面风险评估报告：

风险分析：
市场风险：{analysis['market_risk']['level']} - {', '.join(analysis['market_risk']['factors'])}
信用风险：{analysis['credit_risk']['level']} - {', '.join(analysis['credit_risk']['factors'])}
流动性风险：{analysis['liquidity_risk']['level']} - {', '.join(analysis['liquidity_risk']['factors'])}
操作风险：{analysis['operational_risk']['level']} - {', '.join(analysis['operational_risk']['factors'])}

综合评估：
总体风险等级：{assessment['overall_risk_level']}
风险评分：{assessment['risk_score']}/10
主要风险：{', '.join(assessment['main_risks'])}

风险缓释措施：
{chr(10).join([f"- {measure}" for measure in assessment['risk_mitigation']])}

推荐资产配置：
股票：{assessment['recommended_allocation']['stocks']}
债券：{assessment['recommended_allocation']['bonds']}
现金：{assessment['recommended_allocation']['cash']}
另类投资：{assessment['recommended_allocation']['alternatives']}

后续建议：
基于风险分析，建议转接投资顾问制定具体投资策略。
        """


class InvestmentAdvisor(BaseAgent):
    """投资顾问"""
    
    def __init__(self):
        super().__init__(AgentRole.SOLUTION_EXPERT)
    
    def _get_system_prompt(self) -> str:
        return """你是专业的投资顾问。职责包括：
1. 制定个性化投资策略
2. 推荐具体投资产品
3. 设计投资组合
4. 提供市场分析
5. 制定投资计划

你的建议应该：
- 专业权威
- 量身定制
- 收益风险平衡
- 长期稳健
- 合规合法"""
    
    async def process(self, state: AgentState) -> AgentState:
        """提供投资建议"""
        state = self.set_current_agent(state)
        
        if state.customer_query:
            # 获取客户和风险信息
            client_analysis = state.metadata.get("client_analysis", {})
            risk_assessment = state.metadata.get("risk_assessment", {})
            
            # 制定投资策略
            investment_strategy = await self._create_investment_strategy(client_analysis, risk_assessment)
            state.metadata["investment_strategy"] = investment_strategy
            
            # 推荐投资产品
            product_recommendations = await self._recommend_investment_products(investment_strategy)
            state.metadata["product_recommendations"] = product_recommendations
            
            # 生成投资报告
            investment_report = await self._generate_investment_report(investment_strategy, product_recommendations)
            state = self.add_message_to_history(state, investment_report)
        
        return state
    
    async def _create_investment_strategy(self, client: Dict, risk: Dict) -> Dict[str, Any]:
        """创建投资策略"""
        return {
            "strategy_name": "平衡增长策略",
            "investment_objective": "长期稳健增值",
            "time_horizon": "3-5年",
            "expected_return": "8-12%年化",
            "risk_level": "中等",
            "asset_allocation": {
                "equity": 40,
                "fixed_income": 30,
                "cash": 20,
                "alternatives": 10
            },
            "rebalancing_frequency": "季度",
            "review_schedule": "半年"
        }
    
    async def _recommend_investment_products(self, strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """推荐投资产品"""
        return [
            {
                "category": "股票型基金",
                "product_name": "稳健成长混合基金",
                "risk_level": "中高",
                "expected_return": "10-15%",
                "min_investment": "1000元",
                "features": ["分散投资", "专业管理", "流动性好"]
            },
            {
                "category": "债券型基金",
                "product_name": "稳健收益债券基金",
                "risk_level": "低",
                "expected_return": "4-6%",
                "min_investment": "1000元",
                "features": ["收益稳定", "风险较低", "适合保守投资"]
            },
            {
                "category": "货币基金",
                "product_name": "活期理财货币基金",
                "risk_level": "极低",
                "expected_return": "2-3%",
                "min_investment": "1元",
                "features": ["流动性极高", "风险极低", "随存随取"]
            }
        ]
    
    async def _generate_investment_report(self, strategy: Dict[str, Any], products: List[Dict]) -> str:
        """生成投资报告"""
        products_text = chr(10).join([
            f"{i+1}. {p['product_name']} - {p['category']} - 预期收益{p['expected_return']}" 
            for i, p in enumerate(products)
        ])
        
        allocation_text = chr(10).join([
            f"{asset}: {percentage}%" for asset, percentage in strategy["asset_allocation"].items()
        ])
        
        return f"""
个性化投资策略报告：

投资策略：{strategy['strategy_name']}
投资目标：{strategy['investment_objective']}
投资期限：{strategy['time_horizon']}
预期收益：{strategy['expected_return']}
风险等级：{strategy['risk_level']}

资产配置：
{allocation_text}

推荐投资产品：
{products_text}

投资计划：
- 再平衡频率：{strategy['rebalancing_frequency']}
- 审查安排：{strategy['review_schedule']}

执行建议：
1. 按照资产配置比例逐步建仓
2. 定期检查投资组合表现
3. 根据市场变化适时调整
4. 保持长期投资心态

风险提示：
投资有风险，过往业绩不代表未来表现。请根据自身情况谨慎投资。

后续服务：
我们将提供持续的投资跟踪和调整服务，确保投资目标实现。
        """


class FinancialSystem:
    """金融顾问系统"""
    
    def __init__(self):
        self.memory_store = MemoryStore()
        self.account_manager = AccountManager()
        self.risk_analyst = RiskAnalyst()
        self.investment_advisor = InvestmentAdvisor()
    
    async def process_financial_consultation(self, session_id: str, message: str) -> Dict[str, Any]:
        """处理金融咨询"""
        from src.models.state import CustomerQuery, Message
        import uuid
        
        customer_query = CustomerQuery(
            query_id=str(uuid.uuid4()),
            original_message=message,
            category="financial",
            priority="medium"
        )
        
        user_message = Message(
            id=str(uuid.uuid4()),
            type=MessageType.USER_QUERY,
            sender="client",
            content=message
        )
        
        state = AgentState(
            customer_query=customer_query,
            conversation_history=[user_message]
        )

        state = await self.account_manager.process(state)
        state = await self.risk_analyst.process(state)
        state = await self.investment_advisor.process(state)

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
            "client_profile": metadata.get("client_analysis"),
            "risk_profile": metadata.get("risk_assessment"),
            "investment_strategy": metadata.get("investment_strategy"),
            "product_recommendations": metadata.get("product_recommendations"),
            "conversation": [getattr(msg, "content", str(msg)) for msg in history],
            "answer": _extract_answer(history)
        }
    
    async def cleanup(self):
        """清理资源"""
        await self.memory_store.close()
