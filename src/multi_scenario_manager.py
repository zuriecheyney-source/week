"""
多场景智能体系统管理器
"""
import sys
from pathlib import Path
from typing import Dict, Any, List
from enum import Enum

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.scenarios.customer_service import CustomerServiceSystem
from src.scenarios.education import EducationSystem
from src.scenarios.medical import MedicalSystem
from src.scenarios.financial import FinancialSystem
from src.scenarios.content_creation import ContentCreationSystem


class ScenarioType(Enum):
    """场景类型"""
    CUSTOMER_SERVICE = "customer_service"
    EDUCATION = "education"
    MEDICAL = "medical"
    FINANCIAL = "financial"
    CONTENT_CREATION = "content_creation"


class MultiScenarioManager:
    """多场景智能体系统管理器"""
    
    def __init__(self):
        self.systems = {
            ScenarioType.CUSTOMER_SERVICE: CustomerServiceSystem(),
            ScenarioType.EDUCATION: EducationSystem(),
            ScenarioType.MEDICAL: MedicalSystem(),
            ScenarioType.FINANCIAL: FinancialSystem(),
            ScenarioType.CONTENT_CREATION: ContentCreationSystem()
        }
    
    async def detect_scenario(self, message: str) -> ScenarioType:
        """自动检测用户意图对应的场景"""
        message_lower = message.lower()
        
        # 关键词映射
        scenario_keywords = {
            ScenarioType.CUSTOMER_SERVICE: [
                "客服", "服务", "投诉", "售后", "帮助", "问题", "账户", "登录", "收费"
            ],
            ScenarioType.EDUCATION: [
                "学习", "学", "教育", "课程", "培训", "作业", "考试", "辅导", "教学", "规划", "英语", "数学"
            ],
            ScenarioType.MEDICAL: [
                "医疗", "健康", "症状", "疾病", "治疗", "诊断", "医生", "医院", "药物"
            ],
            ScenarioType.FINANCIAL: [
                "金融", "投资", "理财", "股票", "基金", "保险", "贷款", "银行", "财富"
            ],
            ScenarioType.CONTENT_CREATION: [
                "内容", "创作", "写作", "文章", "视频", "文案", "策划", "审核"
            ]
        }
        
        # 计算每个场景的匹配分数
        scenario_scores = {}
        for scenario, keywords in scenario_keywords.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            scenario_scores[scenario] = score
        
        # 返回得分最高的场景
        if scenario_scores:
            best_scenario = max(scenario_scores, key=scenario_scores.get)
            if scenario_scores[best_scenario] > 0:
                return best_scenario
        
        # 默认返回客服场景
        return ScenarioType.CUSTOMER_SERVICE
    
    async def process_request(self, session_id: str, message: str, scenario: ScenarioType = None) -> Dict[str, Any]:
        """处理用户请求"""
        # 自动检测场景
        if scenario is None:
            scenario = await self.detect_scenario(message)
        
        # 获取对应的系统
        system = self.systems[scenario]
        
        # 根据场景调用不同的处理方法
        if scenario == ScenarioType.CUSTOMER_SERVICE:
            result = await system.process_customer_inquiry(session_id, message)
        elif scenario == ScenarioType.EDUCATION:
            result = await system.process_education_request(session_id, message)
        elif scenario == ScenarioType.MEDICAL:
            result = await system.process_medical_consultation(session_id, message)
        elif scenario == ScenarioType.FINANCIAL:
            result = await system.process_financial_consultation(session_id, message)
        elif scenario == ScenarioType.CONTENT_CREATION:
            result = await system.process_content_creation(session_id, message)
        else:
            result = {"error": "Unknown scenario", "session_id": session_id}
        
        # 添加场景信息
        result["scenario"] = scenario.value
        result["scenario_detected"] = True
        
        return result
    
    async def get_available_scenarios(self) -> List[Dict[str, Any]]:
        """获取所有可用场景"""
        return [
            {
                "id": ScenarioType.CUSTOMER_SERVICE.value,
                "name": "智能客服系统",
                "description": "接待员、问题分析师、解决方案专家",
                "features": ["问题分类", "深度分析", "专家解决", "记忆持久化"]
            },
            {
                "id": ScenarioType.EDUCATION.value,
                "name": "教育辅导系统", 
                "description": "课程顾问、学习规划师、作业批改助手",
                "features": ["课程推荐", "学习规划", "作业批改", "个性化辅导"]
            },
            {
                "id": ScenarioType.MEDICAL.value,
                "name": "医疗咨询系统",
                "description": "问诊助手、诊断分析师、健康建议专家",
                "features": ["症状分析", "诊断建议", "健康指导", "风险评估"]
            },
            {
                "id": ScenarioType.FINANCIAL.value,
                "name": "金融顾问系统",
                "description": "客户经理、风险分析师、投资顾问",
                "features": ["客户分析", "风险评估", "投资建议", "资产配置"]
            },
            {
                "id": ScenarioType.CONTENT_CREATION.value,
                "name": "内容创作系统",
                "description": "选题策划、内容撰写、质量审核",
                "features": ["选题策划", "内容创作", "质量审核", "SEO优化"]
            }
        ]
    
    async def switch_scenario(self, session_id: str, new_scenario: ScenarioType) -> Dict[str, Any]:
        """切换场景"""
        return {
            "session_id": session_id,
            "action": "scenario_switched",
            "previous_scenario": None,
            "new_scenario": new_scenario.value,
            "message": f"已切换到{new_scenario.value}场景",
            "status": "success"
        }
    
    async def get_scenario_status(self, scenario: ScenarioType) -> Dict[str, Any]:
        """获取场景状态"""
        system = self.systems[scenario]
        
        return {
            "scenario": scenario.value,
            "status": "active",
            "agents": len(system.__dict__.keys()) - 1,  # 减去memory_store
            "memory_store": "active" if hasattr(system, 'memory_store') else "inactive"
        }
    
    async def cleanup_all(self):
        """清理所有系统资源"""
        for system in self.systems.values():
            await system.cleanup()
    
    def get_scenario_info(self, scenario: ScenarioType) -> Dict[str, Any]:
        """获取场景详细信息"""
        info = {
            ScenarioType.CUSTOMER_SERVICE: {
                "agents": ["接待员", "问题分析师", "解决方案专家"],
                "workflow": "接待→分析→解决",
                "use_cases": ["客户咨询", "问题处理", "售后服务"],
                "technologies": ["LangGraph", "OpenAI", "SQLite"]
            },
            ScenarioType.EDUCATION: {
                "agents": ["课程顾问", "学习规划师", "作业批改助手"],
                "workflow": "咨询→规划→批改",
                "use_cases": ["课程推荐", "学习计划", "作业辅导"],
                "technologies": ["LangGraph", "OpenAI", "知识库"]
            },
            ScenarioType.MEDICAL: {
                "agents": ["问诊助手", "诊断分析师", "健康建议专家"],
                "workflow": "问诊→诊断→建议",
                "use_cases": ["症状咨询", "诊断分析", "健康指导"],
                "technologies": ["LangGraph", "OpenAI", "医疗知识库"]
            },
            ScenarioType.FINANCIAL: {
                "agents": ["客户经理", "风险分析师", "投资顾问"],
                "workflow": "客户→风险→投资",
                "use_cases": ["理财咨询", "风险评估", "投资建议"],
                "technologies": ["LangGraph", "OpenAI", "金融数据"]
            },
            ScenarioType.CONTENT_CREATION: {
                "agents": ["选题策划", "内容撰写", "质量审核"],
                "workflow": "策划→撰写→审核",
                "use_cases": ["内容策划", "文章创作", "质量审核"],
                "technologies": ["LangGraph", "OpenAI", "SEO工具"]
            }
        }
        
        return info.get(scenario, {"error": "Unknown scenario"})



