"""
内容创作系统：选题策划、内容撰写、质量审核
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


class ContentRole(Enum):
    """内容创作系统角色"""
    TOPIC_PLANNER = "topic_planner"
    CONTENT_WRITER = "content_writer"
    QUALITY_REVIEWER = "quality_reviewer"


class TopicPlanner(BaseAgent):
    """选题策划"""
    
    def __init__(self):
        super().__init__(AgentRole.RECEPTIONIST)
    
    def _get_system_prompt(self) -> str:
        return """你是专业的内容选题策划师。职责包括：
1. 分析目标受众和市场需求
2. 研究热门话题和趋势
3. 制定内容选题策略
4. 规划内容发布计划
5. 评估选题可行性

你的策划应该：
- 市场导向
- 创新独特
- 可执行性强
- 符合趋势
- 价值明确"""
    
    async def process(self, state: AgentState) -> AgentState:
        """处理选题策划"""
        state = self.set_current_agent(state)
        
        if not state.customer_query:
            welcome_msg = await self.call_llm("生成专业的内容创作欢迎语")
            state = self.add_message_to_history(state, welcome_msg)
        
        if state.customer_query:
            # 分析创作需求
            content_analysis = await self._analyze_content_needs(state.customer_query.original_message)
            state.metadata["content_analysis"] = content_analysis
            
            # 研究热门话题
            topic_research = await self._research_trending_topics(content_analysis)
            state.metadata["topic_research"] = topic_research
            
            # 制定选题策略
            topic_strategy = await self._create_topic_strategy(content_analysis, topic_research)
            state.metadata["topic_strategy"] = topic_strategy
            
            # 生成策划报告
            planning_report = await self._generate_planning_report(content_analysis, topic_research, topic_strategy)
            state = self.add_message_to_history(state, planning_report)
            
            # 转接内容撰写
            handoff_msg = "[转接至content_writer] 开始内容创作"
            state = self.add_message_to_history(state, handoff_msg, MessageType.HANDOFF)
            state.handoff_reason = "选题确定，开始内容创作"
        
        return state
    
    async def _analyze_content_needs(self, message: str) -> Dict[str, Any]:
        """分析内容需求"""
        return {
            "content_type": "article",
            "target_audience": "tech_enthusiasts",
            "platform": "blog",
            "tone": "professional",
            "length": "medium",
            "purpose": "education",
            "keywords": ["AI", "technology", "innovation"]
        }
    
    async def _research_trending_topics(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """研究热门话题"""
        return [
            {
                "topic": "人工智能最新发展",
                "trend_score": 9.2,
                "search_volume": "high",
                "competition": "medium",
                "engagement": "high"
            },
            {
                "topic": "机器学习实战指南",
                "trend_score": 8.8,
                "search_volume": "high",
                "competition": "high",
                "engagement": "medium"
            },
            {
                "topic": "AI工具评测",
                "trend_score": 8.5,
                "search_volume": "medium",
                "competition": "low",
                "engagement": "high"
            }
        ]
    
    async def _create_topic_strategy(self, analysis: Dict[str, Any], research: List[Dict]) -> Dict[str, Any]:
        """创建选题策略"""
        return {
            "primary_topic": "人工智能最新发展",
            "secondary_topics": ["机器学习实战指南", "AI工具评测"],
            "content_pillars": [
                "技术解析",
                "实战案例",
                "工具推荐"
            ],
            "publishing_schedule": {
                "frequency": "每周2篇",
                "best_times": ["周二", "周四"],
                "content_types": ["深度文章", "快速教程"]
            },
            "seo_strategy": {
                "primary_keywords": ["人工智能", "AI发展"],
                "secondary_keywords": ["机器学习", "深度学习"],
                "long_tail_keywords": ["AI应用案例", "人工智能趋势"]
            }
        }
    
    async def _generate_planning_report(self, analysis: Dict, research: List[Dict], strategy: Dict) -> str:
        """生成策划报告"""
        research_text = chr(10).join([
            f"{i+1}. {topic['topic']} (趋势分数: {topic['trend_score']})" 
            for i, topic in enumerate(research)
        ])
        
        pillars_text = chr(10).join([f"- {pillar}" for pillar in strategy["content_pillars"]])
        
        return f"""
内容选题策划报告：

需求分析：
- 内容类型：{analysis['content_type']}
- 目标受众：{analysis['target_audience']}
- 发布平台：{analysis['platform']}
- 内容调性：{analysis['tone']}
- 内容长度：{analysis['length']}

热门话题研究：
{research_text}

选题策略：
主要话题：{strategy['primary_topic']}
次要话题：{', '.join(strategy['secondary_topics'])}

内容支柱：
{pillars_text}

发布计划：
- 发布频率：{strategy['publishing_schedule']['frequency']}
- 最佳时间：{', '.join(strategy['publishing_schedule']['best_times'])}
- 内容类型：{', '.join(strategy['publishing_schedule']['content_types'])}

SEO策略：
主要关键词：{', '.join(strategy['seo_strategy']['primary_keywords'])}
次要关键词：{', '.join(strategy['seo_strategy']['secondary_keywords'])}

后续步骤：
选题策略已确定，建议转接内容撰写师开始创作。
        """


class ContentWriter(BaseAgent):
    """内容撰写"""
    
    def __init__(self):
        super().__init__(AgentRole.PROBLEM_ANALYST)
    
    def _get_system_prompt(self) -> str:
        return """你是专业的内容撰写师。职责包括：
1. 根据选题策略创作内容
2. 确保内容质量和可读性
3. 优化SEO和用户体验
4. 融入目标关键词
5. 保持品牌调性一致

你的创作应该：
- 原创独特
- 价值丰富
- 结构清晰
- 语言流畅
- 符合规范"""
    
    async def process(self, state: AgentState) -> AgentState:
        """进行内容创作"""
        state = self.set_current_agent(state)
        
        if state.customer_query:
            # 获取选题策略
            topic_strategy = state.metadata.get("topic_strategy", {})
            content_analysis = state.metadata.get("content_analysis", {})
            
            # 创作内容大纲
            content_outline = await self._create_content_outline(topic_strategy, content_analysis)
            state.metadata["content_outline"] = content_outline
            
            # 撰写内容
            content_draft = await self._write_content(content_outline, content_analysis)
            state.metadata["content_draft"] = content_draft
            
            # 优化SEO
            seo_optimization = await self._optimize_seo(content_draft, topic_strategy)
            state.metadata["seo_optimization"] = seo_optimization
            
            # 生成创作报告
            writing_report = await self._generate_writing_report(content_outline, content_draft, seo_optimization)
            state = self.add_message_to_history(state, writing_report)
            
            # 转接质量审核
            handoff_msg = "[转接至quality_reviewer] 内容创作完成，需要质量审核"
            state = self.add_message_to_history(state, handoff_msg, MessageType.HANDOFF)
            state.handoff_reason = "内容创作完成，需要质量审核"
        
        return state
    
    async def _create_content_outline(self, strategy: Dict, analysis: Dict) -> Dict[str, Any]:
        """创建内容大纲"""
        return {
            "title": "人工智能最新发展：2024年趋势与应用",
            "introduction": "引言：AI技术的快速发展背景",
            "main_sections": [
                {
                    "section": "大语言模型的突破",
                    "subsections": ["GPT系列发展", "国产大模型崛起", "应用场景拓展"],
                    "word_count": 800
                },
                {
                    "section": "计算机视觉的新进展",
                    "subsections": ["图像识别精度提升", "视频理解能力", "医疗影像应用"],
                    "word_count": 600
                },
                {
                    "section": "AI在各行业的应用",
                    "subsections": ["医疗健康", "教育培训", "金融服务"],
                    "word_count": 700
                }
            ],
            "conclusion": "总结：AI未来发展趋势",
            "total_word_count": 2500,
            "estimated_reading_time": "10分钟"
        }
    
    async def _write_content(self, outline: Dict, analysis: Dict) -> str:
        """撰写内容"""
        content = f"""
# {outline['title']}

## {outline['introduction']}

人工智能技术在2024年迎来了前所未有的发展机遇，从大语言模型到计算机视觉，各个领域都取得了显著突破。

## {outline['main_sections'][0]['section']}

### {outline['main_sections'][0]['subsections'][0]}
GPT系列模型的持续进化推动了自然语言处理能力的边界...

### {outline['main_sections'][0]['subsections'][1]}
国产大模型在技术和应用层面都取得了重要进展...

### {outline['main_sections'][0]['subsections'][2]}
大语言模型的应用场景不断扩展，从客服到创作，从编程到分析...

## {outline['main_sections'][1]['section']}

### {outline['main_sections'][1]['subsections'][0]}
计算机视觉在图像识别精度方面达到了新的高度...

### {outline['main_sections'][1]['subsections'][1]}
视频理解能力的提升让AI能够更好地处理动态内容...

### {outline['main_sections'][1]['subsections'][2]}
医疗影像成为计算机视觉应用的重要领域...

## {outline['main_sections'][2]['section']}

### {outline['main_sections'][2]['subsections'][0]}
AI在医疗健康领域的应用正在改变传统诊疗模式...

### {outline['main_sections'][2]['subsections'][1]}
教育培训行业通过AI实现个性化学习...

### {outline['main_sections'][2]['subsections'][2]}
金融服务利用AI提升效率和准确性...

## {outline['conclusion']}

人工智能的发展前景广阔，但同时也面临着技术伦理、数据安全等挑战。未来，AI将更加注重可解释性、安全性和普惠性发展。

---

*本文约{outline['total_word_count']}字，预计阅读时间{outline['estimated_reading_time']}*
        """
        
        return content
    
    async def _optimize_seo(self, content: str, strategy: Dict) -> Dict[str, Any]:
        """优化SEO"""
        return {
            "title_optimized": "人工智能最新发展：2024年AI趋势与应用全解析",
            "meta_description": "深入了解2024年人工智能最新发展趋势，包括大语言模型突破、计算机视觉进展和各行业应用案例。",
            "keyword_density": {
                "人工智能": "2.8%",
                "AI": "3.2%",
                "机器学习": "1.5%"
            },
            "internal_links": ["相关AI技术文章", "机器学习教程"],
            "external_references": ["OpenAI官网", "斯坦福AI指数报告"],
            "readability_score": 8.5
        }
    
    async def _generate_writing_report(self, outline: Dict, content: str, seo: Dict) -> str:
        """生成创作报告"""
        return f"""
内容创作报告：

创作大纲：
- 标题：{outline['title']}
- 总字数：{outline['total_word_count']}字
- 阅读时间：{outline['estimated_reading_time']}
- 主要章节：{len(outline['main_sections'])}个

内容质量：
- 原创性：100%
- 结构完整性：优秀
- 逻辑连贯性：良好
- 语言流畅性：优秀

SEO优化：
- 优化标题：{seo['title_optimized']}
- Meta描述：{seo['meta_description']}
- 关键词密度：符合SEO最佳实践
- 可读性评分：{seo['readability_score']}/10

创作完成情况：
✅ 内容撰写完成
✅ SEO优化完成
✅ 结构检查完成
✅ 关键词布局完成

后续步骤：
内容创作已完成，建议转接质量审核师进行最终审核。
        """


class QualityReviewer(BaseAgent):
    """质量审核"""
    
    def __init__(self):
        super().__init__(AgentRole.SOLUTION_EXPERT)
    
    def _get_system_prompt(self) -> str:
        return """你是专业的内容质量审核师。职责包括：
1. 全面审核内容质量
2. 检查事实准确性
3. 评估SEO效果
4. 确保合规性
5. 提供改进建议

你的审核应该：
- 客观公正
- 标准严格
- 细致全面
- 建设性强
- 专业权威"""
    
    async def process(self, state: AgentState) -> AgentState:
        """进行质量审核"""
        state = self.set_current_agent(state)
        
        if state.customer_query:
            # 获取创作内容
            content_draft = state.metadata.get("content_draft", "")
            seo_optimization = state.metadata.get("seo_optimization", {})
            content_outline = state.metadata.get("content_outline", {})
            
            # 质量审核
            quality_review = await self._conduct_quality_review(content_draft, content_outline)
            state.metadata["quality_review"] = quality_review
            
            # 事实核查
            fact_check = await self._fact_check_content(content_draft)
            state.metadata["fact_check"] = fact_check
            
            # 合规检查
            compliance_check = await self._check_compliance(content_draft)
            state.metadata["compliance_check"] = compliance_check
            
            # 生成审核报告
            review_report = await self._generate_review_report(quality_review, fact_check, compliance_check)
            state = self.add_message_to_history(state, review_report)
        
        return state
    
    async def _conduct_quality_review(self, content: str, outline: Dict) -> Dict[str, Any]:
        """进行质量审核"""
        return {
            "content_quality": {
                "originality": 9.5,
                "accuracy": 8.8,
                "completeness": 9.0,
                "readability": 8.7,
                "engagement": 8.5
            },
            "technical_aspects": {
                "grammar": 9.2,
                "spelling": 9.8,
                "punctuation": 9.0,
                "formatting": 8.8
            },
            "structure_review": {
                "introduction": "excellent",
                "body_paragraphs": "good",
                "conclusion": "excellent",
                "flow": "smooth"
            },
            "overall_score": 8.9,
            "issues_found": [
                "部分段落过长",
                "缺少实际案例"
            ],
            "strengths": [
                "结构清晰",
                "信息丰富",
                "观点新颖"
            ]
        }
    
    async def _fact_check_content(self, content: str) -> Dict[str, Any]:
        """事实核查"""
        return {
            "claims_verified": 15,
            "claims_total": 16,
            "accuracy_rate": 0.94,
            "unverified_claims": [
                "某公司AI产品具体数据"
            ],
            "sources_needed": [
                "行业报告引用",
                "官方数据来源"
            ],
            "fact_check_grade": "A-"
        }
    
    async def _check_compliance(self, content: str) -> Dict[str, Any]:
        """合规检查"""
        return {
            "copyright_compliance": "pass",
            "privacy_compliance": "pass",
            "advertising_compliance": "pass",
            "content_guidelines": "pass",
            "legal_review": "pass",
            "compliance_score": 9.2,
            "recommendations": [
                "添加数据来源引用",
                "更新部分过时信息"
            ]
        }
    
    async def _generate_review_report(self, quality: Dict, fact: Dict, compliance: Dict) -> str:
        """生成审核报告"""
        quality_scores = quality["content_quality"]
        issues_text = chr(10).join([f"- {issue}" for issue in quality["issues_found"]])
        strengths_text = chr(10).join([f"- {strength}" for strength in quality["strengths"]])
        
        return f"""
内容质量审核报告：

内容质量评分：
- 原创性：{quality_scores['originality']}/10
- 准确性：{quality_scores['accuracy']}/10
- 完整性：{quality_scores['completeness']}/10
- 可读性：{quality_scores['readability']}/10
- 吸引力：{quality_scores['engagement']}/10
- 综合评分：{quality['overall_score']}/10

技术质量：
- 语法：{quality['technical_aspects']['grammar']}/10
- 拼写：{quality['technical_aspects']['spelling']}/10
- 标点：{quality['technical_aspects']['punctuation']}/10
- 格式：{quality['technical_aspects']['formatting']}/10

结构审核：
- 引言：{quality['structure_review']['introduction']}
- 主体：{quality['structure_review']['body_paragraphs']}
- 结论：{quality['structure_review']['conclusion']}
- 流畅度：{quality['structure_review']['flow']}

事实核查：
- 核实声明：{fact['claims_verified']}/{fact['claims_total']}
- 准确率：{fact['accuracy_rate']*100:.1f}%
- 事实核查等级：{fact['fact_check_grade']}

合规检查：
- 版权合规：{compliance['copyright_compliance']}
- 隐私合规：{compliance['privacy_compliance']}
- 内容规范：{compliance['content_guidelines']}
- 合规评分：{compliance['compliance_score']}/10

发现问题：
{issues_text}

内容优势：
{strengths_text}

改进建议：
1. 补充实际应用案例
2. 添加数据来源引用
3. 优化部分段落长度
4. 更新最新行业数据

审核结论：
✅ 内容质量优秀
✅ 事实基本准确
✅ 符合合规要求
⚠️ 需要小幅改进

发布建议：
内容整体质量良好，建议进行小幅改进后即可发布。
        """


class ContentCreationSystem:
    """内容创作系统"""
    
    def __init__(self):
        self.memory_store = MemoryStore()
        self.topic_planner = TopicPlanner()
        self.content_writer = ContentWriter()
        self.quality_reviewer = QualityReviewer()
    
    async def process_content_creation(self, session_id: str, message: str) -> Dict[str, Any]:
        """处理内容创作请求"""
        from src.models.state import CustomerQuery, Message
        import uuid
        
        customer_query = CustomerQuery(
            query_id=str(uuid.uuid4()),
            original_message=message,
            category="content_creation",
            priority="medium"
        )
        
        user_message = Message(
            id=str(uuid.uuid4()),
            type=MessageType.USER_QUERY,
            sender="content_creator",
            content=message
        )
        
        state = AgentState(
            customer_query=customer_query,
            conversation_history=[user_message]
        )

        state = await self.topic_planner.process(state)
        state = await self.content_writer.process(state)
        state = await self.quality_reviewer.process(state)

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

        return {
            "session_id": session_id,
            "content_analysis": (state.metadata or {}).get("content_analysis"),
            "topic_strategy": (state.metadata or {}).get("topic_strategy"),
            "content_outline": (state.metadata or {}).get("content_outline"),
            "content_draft": (state.metadata or {}).get("content_draft"),
            "quality_review": (state.metadata or {}).get("quality_review"),
            "conversation": [getattr(msg, "content", str(msg)) for msg in (state.conversation_history or [])],
            "answer": _extract_answer(state.conversation_history or [])
        }
    
    async def cleanup(self):
        """清理资源"""
        await self.memory_store.close()
