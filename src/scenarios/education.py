"""
教育辅导系统：课程顾问、学习规划师、作业批改助手
"""
import json
import re
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


class EducationRole(Enum):
    """教育系统角色"""
    COURSE_ADVISOR = "course_advisor"
    LEARNING_PLANNER = "learning_planner"
    HOMEWORK_GRADER = "homework_grader"


class CourseAdvisor(BaseAgent):
    """课程顾问"""
    
    def __init__(self):
        super().__init__(AgentRole.RECEPTIONIST)
    
    def _get_system_prompt(self) -> str:
        return """你是专业的课程顾问。职责包括：
1. 了解学生学习需求和目标
2. 评估学生当前水平
3. 推荐适合的课程
4. 制定学习方向建议
5. 提供课程选择指导

你的建议应该：
- 基于学生实际情况
- 考虑学习目标
- 提供多种选择
- 说明课程特点
- 给出明确建议"""
    
    async def process(self, state: AgentState) -> AgentState:
        """处理课程咨询"""
        state = self.set_current_agent(state)
        
        if not state.customer_query:
            welcome_msg = await self.call_llm("生成专业的教育咨询欢迎语")
            state = self.add_message_to_history(state, welcome_msg)
        
        if state.customer_query:
            # 分析学生需求
            needs_analysis = await self._analyze_student_needs(state.customer_query.original_message)
            state.metadata["student_needs"] = needs_analysis
            
            # 推荐课程
            recommendations = await self._recommend_courses(needs_analysis)
            state.metadata["course_recommendations"] = recommendations
            
            # 生成咨询报告
            report = await self._generate_advisor_report(needs_analysis, recommendations)
            state = self.add_message_to_history(state, report)
            
            # 决定是否需要学习规划师
            if needs_analysis["complexity"] == "high":
                handoff_msg = "[转接至learning_planner] 需要制定详细学习计划"
                state = self.add_message_to_history(state, handoff_msg, MessageType.HANDOFF)
                state.handoff_reason = "复杂学习需求需要专业规划"
        
        return state
    
    async def _analyze_student_needs(self, message: str) -> Dict[str, Any]:
        """分析学生需求"""
        subject, grade = self._infer_subject_and_grade(message)
        return {
            "subject": subject,
            "grade": grade,
            "learning_goal": "exam_prep" if any(k in message for k in ["高考", "期末", "月考", "考试", "提分"]) else "skill_upgrade",
            "current_level": "intermediate",
            "time_commitment": "part_time",
            "budget": "low",
            "preference": "mixed",
            "complexity": "high" if any(k in message for k in ["规划", "计划", "系统", "长期"]) else "medium"
        }

    def _infer_subject_and_grade(self, message: str) -> (str, str):
        msg = message.lower()
        subject_map = [
            ("C语言", ["c语言", "c language", "c 程序", "c语言程序设计"]),
            ("编程", ["编程", "程序设计", "写代码", "coding", "代码", "开发"]),
            ("语文", ["语文", "作文", "阅读", "文言文", "古诗", "名著"]),
            ("英语", ["英语", "english", "单词", "词汇", "语法", "阅读理解", "完形", "听力", "写作", "翻译"]),
            ("数学", ["数学", "math", "函数", "几何", "数列", "导数", "概率"]),
            ("物理", ["物理", "力学", "电磁", "光学", "热学"]),
            ("化学", ["化学", "有机", "无机", "化学反应", "实验"]),
            ("生物", ["生物", "遗传", "细胞", "生态"]),
            ("历史", ["历史", "史纲", "史实"]),
            ("地理", ["地理", "气候", "地形", "人口", "区域"]),
            ("政治", ["政治", "思政", "哲学", "经济", "法律"]),
        ]
        subject = "综合"
        for s, kws in subject_map:
            if any(k in msg for k in kws):
                subject = s
                break

        grade = "未指定"
        m = re.search(r"(高一|高二|高三|初一|初二|初三)", message)
        if m:
            grade = m.group(1)
        return subject, grade
    
    async def _recommend_courses(self, needs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """推荐课程"""
        subject = needs.get("subject") or "综合"
        grade = needs.get("grade") or "未指定"
        base = {
            "level": needs.get("current_level", "intermediate"),
            "duration": "12周",
            "price": needs.get("budget", "low"),
            "format": "online",
        }

        if subject == "C语言":
            return [
                {
                    **base,
                    "name": "C语言入门到进阶（语法+指针+项目）",
                    "features": ["语法基础", "指针与内存", "调试与工具链", "数据结构入门", "小项目实战"],
                }
            ]

        if subject == "编程":
            return [
                {
                    **base,
                    "name": "编程入门学习路径（基础语法+算法+项目）",
                    "features": ["语法基础", "调试", "算法与数据结构", "项目实践"],
                }
            ]

        if subject == "语文":
            return [
                {
                    **base,
                    "name": f"{grade}语文系统提升（阅读+古诗文+作文）",
                    "features": ["阅读方法", "文言文", "作文素材与结构", "真题训练"],
                }
            ]
        if subject == "英语":
            return [
                {
                    **base,
                    "name": f"{grade}英语提分计划（词汇+语法+阅读+写作）",
                    "features": ["词汇循环", "语法梳理", "阅读/完形", "写作模板", "听力训练"],
                }
            ]
        if subject == "数学":
            return [
                {
                    **base,
                    "name": f"{grade}数学专项突破（专题+刷题+错题本）",
                    "features": ["核心专题", "题型归纳", "错题复盘", "周测评估"],
                }
            ]

        return [
            {
                **base,
                "name": f"{grade}{subject}学习规划与提升",
                "features": ["薄弱点诊断", "知识点梳理", "练习与复盘", "阶段测评"],
            }
        ]
    
    async def _generate_advisor_report(self, needs: Dict[str, Any], courses: List[Dict]) -> str:
        """生成咨询报告"""
        return f"""
学习需求分析：
- 学习目标：{needs['learning_goal']}
- 当前水平：{needs['current_level']}
- 时间投入：{needs['time_commitment']}
- 预算范围：{needs['budget']}
- 学习偏好：{needs['preference']}

推荐课程：
{chr(10).join([f"{i+1}. {course['name']} - {course['duration']} - {course['price']}预算" for i, course in enumerate(courses)])}

建议：根据您的需求，建议选择第一个课程作为入门，后续可考虑进阶课程。
        """


class LearningPlanner(BaseAgent):
    """学习规划师"""
    
    def __init__(self):
        super().__init__(AgentRole.PROBLEM_ANALYST)
    
    def _get_system_prompt(self) -> str:
        return """你是专业的学习规划师。职责包括：
1. 制定详细学习计划
2. 设计学习路径
3. 安排学习时间表
4. 设定学习里程碑
5. 提供学习建议

你的规划应该：
- 科学合理
- 可执行性强
- 循序渐进
- 目标明确
- 便于跟踪"""
    
    async def process(self, state: AgentState) -> AgentState:
        """制定学习计划"""
        state = self.set_current_agent(state)
        
        if state.customer_query:
            # 获取学生需求
            student_needs = state.metadata.get("student_needs", {})
            
            # 制定学习计划
            learning_plan = await self._create_learning_plan(student_needs, state.customer_query.original_message)
            state.metadata["learning_plan"] = learning_plan
            
            # 生成详细规划
            plan_details = await self._generate_plan_details(learning_plan)
            state = self.add_message_to_history(state, plan_details)
            
            # 如果有作业需求，转接作业批改助手
            if "作业" in state.customer_query.original_message or "练习" in state.customer_query.original_message:
                handoff_msg = "[转接至homework_grader] 需要作业批改服务"
                state = self.add_message_to_history(state, handoff_msg, MessageType.HANDOFF)
                state.handoff_reason = "需要作业批改和反馈"
        
        return state
    
    async def _create_learning_plan(self, needs: Dict[str, Any], raw_message: str) -> Dict[str, Any]:
        """创建学习计划"""
        subject = needs.get("subject") or "综合"
        grade = needs.get("grade") or "未指定"
        goal = needs.get("learning_goal") or "skill_upgrade"

        def _parse_weekly_hours(text: str) -> int:
            # Defaults to 10 hours/week if not specified
            if not text:
                return 10
            # 每天X小时
            m = re.search(r"每天\s*(\d+(?:\.\d+)?)\s*小时", text)
            if m:
                return max(1, int(round(float(m.group(1)) * 7)))
            # 每天X分钟
            m = re.search(r"每天\s*(\d+)\s*分钟", text)
            if m:
                return max(1, int(round(int(m.group(1)) * 7 / 60)))
            # 每周X小时
            m = re.search(r"每周\s*(\d+(?:\.\d+)?)\s*小时", text)
            if m:
                return max(1, int(round(float(m.group(1)))))
            return 10

        def _parse_target_delta(text: str) -> str:
            # 提高15分 / 提分15
            if not text:
                return ""
            m = re.search(r"(?:提高|提分)\s*(\d+)\s*分", text)
            if m:
                return m.group(0)
            return ""

        def _plan_text_blob(plan_dict: Dict[str, Any]) -> str:
            parts = []
            for k in ["focus_areas", "resources", "assessment"]:
                v = plan_dict.get(k)
                if isinstance(v, list):
                    parts.extend([str(x) for x in v])
            ms = plan_dict.get("milestones")
            if isinstance(ms, list):
                for item in ms:
                    if isinstance(item, dict):
                        parts.append(str(item.get("goal", "")))
            ds = plan_dict.get("daily_schedule")
            if isinstance(ds, dict):
                parts.extend([str(x) for x in ds.values()])
            return "\n".join([p for p in parts if p])

        def _is_plan_valid(plan_dict: Dict[str, Any]) -> bool:
            if not isinstance(plan_dict, dict):
                return False
            required = ["total_duration", "weekly_hours", "milestones", "daily_schedule", "resources"]
            if any(k not in plan_dict for k in required):
                return False
            if not isinstance(plan_dict.get("milestones"), list):
                return False
            if not isinstance(plan_dict.get("daily_schedule"), dict):
                return False
            if not isinstance(plan_dict.get("resources"), list):
                return False
            return True

        def _is_subject_consistent(plan_dict: Dict[str, Any], expected_subject: str) -> bool:
            text = _plan_text_blob(plan_dict)
            if not text:
                return True
            # quick negative heuristics for common mix-ups
            if expected_subject == "英语":
                bad = ["古诗", "文言文", "古诗文", "现代文", "语文", "作文素材"]
                good = ["词汇", "单词", "语法", "阅读", "完形", "听力", "写作", "翻译"]
                if any(b in text for b in bad) and not any(g in text for g in good):
                    return False
            if expected_subject == "语文":
                bad = ["单词", "词汇", "语法", "听力", "完形", "英文", "英语"]
                good = ["文言文", "古诗", "阅读", "作文", "现代文"]
                if any(b in text for b in bad) and not any(g in text for g in good):
                    return False
            return True

        weekly_hours = _parse_weekly_hours(raw_message)
        target_delta = _parse_target_delta(raw_message)

        prompt = f"""
请为学生制定一个可执行的学习计划。

学生信息：
- 学科：{subject}（必须严格围绕该学科，不要输出其它学科内容）
- 年级：{grade}
- 目标：{goal}{('，目标：' + target_delta) if target_delta else ''}
- 每周可投入时间：约{weekly_hours}小时（请让计划的weekly_hours与此大致一致）

请输出严格JSON（不要markdown），字段：
{{
  "total_duration": "12周",
  "weekly_hours": {weekly_hours},
  "focus_areas": ["..."],
  "milestones": [{{"week": 2, "goal": "..."}}],
  "daily_schedule": {{"周一": "...", "周二": "...", "周三": "...", "周四": "...", "周五": "...", "周六": "...", "周日": "..."}},
  "resources": ["..."],
  "assessment": ["..."],
  "notes": "..."
}}
"""

        def _extract_json(text: str) -> Dict[str, Any]:
            try:
                return json.loads(text)
            except Exception:
                pass
            try:
                start = text.find("{")
                end = text.rfind("}")
                if start != -1 and end != -1 and end > start:
                    return json.loads(text[start : end + 1])
            except Exception:
                pass
            return {}

        try:
            raw = await self.call_llm(prompt)
            plan = _extract_json(raw)
        except Exception:
            plan = {}

        if plan and _is_plan_valid(plan) and _is_subject_consistent(plan, subject):
            # honor parsed time budget
            plan["weekly_hours"] = weekly_hours
            return plan

        if subject == "C语言":
            return {
                "total_duration": "12周",
                "weekly_hours": weekly_hours,
                "focus_areas": ["C语法基础", "指针与内存", "函数与模块化", "数组/字符串", "结构体/文件IO", "调试与工具链", "数据结构与算法入门", "小项目"],
                "milestones": [
                    {"week": 2, "goal": "环境搭建 + 基本语法（变量/分支/循环/函数）"},
                    {"week": 4, "goal": "数组/字符串 + 指针基础（能读懂指针表达式）"},
                    {"week": 6, "goal": "指针进阶 + 内存模型 + 结构体 + 常见坑"},
                    {"week": 8, "goal": "文件IO + 模块化 + 用gdb/IDE调试定位问题"},
                    {"week": 10, "goal": "数据结构入门（栈/队列/链表）+ 简单算法题"},
                    {"week": 12, "goal": "完成1-2个小项目 + 总结常见错误与代码规范"},
                ],
                "daily_schedule": {
                    "周一": "语法学习 40分钟 + 小练习 30分钟",
                    "周二": "指针/数组专项 60分钟 + 手写代码 30分钟",
                    "周三": "刷2-3道基础题（IO/字符串/循环）60分钟 + 复盘 20分钟",
                    "周四": "结构体/函数/模块化 60分钟 + 重构练习 30分钟",
                    "周五": "调试训练（断点/单步/变量）40分钟 + 错误总结 20分钟",
                    "周六": "项目推进 120分钟（需求→实现→测试）",
                    "周日": "回顾总结 40分钟 + 下周预习 30分钟",
                },
                "resources": ["K&R《C程序设计语言》或同等教材", "菜鸟教程/CS自学指南相关章节", "在线判题（洛谷/牛客/LeetCode简单题）", "gdb/VSCode调试教程"],
                "assessment": ["每周完成一组练习题并复盘", "每两周做一次小测（30-45分钟）", "第8周起每周至少一次调试练习"],
                "notes": "C语言关键是指针与内存模型。不要只看不写：每个知识点至少配套3-5个小练习，错误要写进‘坑点清单’。",
            }

        if subject == "语文":
            return {
                "total_duration": "12周",
                "weekly_hours": weekly_hours,
                "focus_areas": ["现代文阅读", "文言文与古诗词", "作文", "基础知识与积累"],
                "milestones": [
                    {"week": 2, "goal": "建立阅读与作文素材体系"},
                    {"week": 6, "goal": "完成文言文高频实词虚词与题型训练"},
                    {"week": 10, "goal": "真题套卷训练与稳定得分点"},
                    {"week": 12, "goal": "查漏补缺与冲刺复盘"},
                ],
                "daily_schedule": {
                    "周一": "阅读理解方法训练 40分钟 + 错题整理 20分钟",
                    "周二": "文言文/古诗词 40分钟 + 课内背诵 20分钟",
                    "周三": "作文素材积累 30分钟 + 仿写/段落训练 30分钟",
                    "周四": "基础知识（病句/成语/衔接）40分钟 + 小测 20分钟",
                    "周五": "阅读/文言专项 40分钟 + 复盘 20分钟",
                    "周六": "整卷/专项训练 60分钟",
                    "周日": "错题回顾 30分钟 + 预习下周 30分钟",
                },
                "resources": ["课本与课堂笔记", "历年真题/模拟题", "作文素材本", "错题本"],
                "assessment": ["每周一次小测", "每两周一次作文精改", "每周一套阅读/文言专项"],
                "notes": "先建立稳定得分点（文言+基础+阅读方法），作文按结构模板+素材积累持续提升。",
            }

        if subject == "英语":
            return {
                "total_duration": "12周",
                "weekly_hours": weekly_hours,
                "focus_areas": ["词汇", "语法", "阅读/完形", "听力", "写作/翻译"],
                "milestones": [
                    {"week": 2, "goal": "建立词汇循环与核心语法清单"},
                    {"week": 6, "goal": "阅读/完形速度与正确率提升"},
                    {"week": 10, "goal": "写作模板与句型库成型，套卷训练"},
                    {"week": 12, "goal": "查漏补缺与冲刺"},
                ],
                "daily_schedule": {
                    "周一": "单词 25分钟 + 语法 35分钟",
                    "周二": "阅读理解 1篇 + 复盘 40分钟",
                    "周三": "完形/七选五 1篇 + 复盘 40分钟",
                    "周四": "听力 20分钟 + 精听 20分钟 + 语法巩固 20分钟",
                    "周五": "写作 1个段落/框架练习 + 句型积累 40分钟",
                    "周六": "套题半套/专项训练 60分钟",
                    "周日": "错题回顾 30分钟 + 单词复盘 30分钟",
                },
                "resources": ["高考词汇表/校本词汇", "真题阅读", "听力材料", "写作范文与模板"],
                "assessment": ["每周词汇测", "每周1套阅读/完形", "每两周1篇作文精改", "每周1套卷"],
                "notes": "词汇每天不断，阅读/完形用真题+复盘；写作用模板+句型库逐步扩充。",
            }

        return {
            "total_duration": "12周",
            "weekly_hours": weekly_hours,
            "focus_areas": ["基础知识", "核心题型", "错题复盘", "阶段测评"],
            "milestones": [
                {"week": 2, "goal": "明确薄弱点与学习节奏"},
                {"week": 6, "goal": "完成核心知识点梳理"},
                {"week": 10, "goal": "套题训练与稳定发挥"},
                {"week": 12, "goal": "查漏补缺与总结"},
            ],
            "daily_schedule": {
                "周一": "基础知识 40分钟",
                "周二": "专项训练 60分钟",
                "周三": "错题复盘 45分钟",
                "周四": "专项训练 60分钟",
                "周五": "小测 30分钟 + 复盘 30分钟",
                "周六": "套题/专项训练 60分钟",
                "周日": "整理计划与错题回顾 60分钟",
            },
            "resources": ["课本与笔记", "真题/模拟题", "错题本"],
            "assessment": ["每周小测", "每两周一次阶段测评"],
            "notes": "先稳基础，再做专项与套题，复盘优先于刷题量。",
        }
    
    async def _generate_plan_details(self, plan: Dict[str, Any]) -> str:
        """生成计划详情"""
        milestones_text = chr(10).join([
            f"第{m['week']}周：{m['goal']}" for m in plan["milestones"]
        ])
        
        schedule_text = chr(10).join([
            f"{day}：{activity}" for day, activity in plan["daily_schedule"].items()
        ])

        focus_areas = plan.get("focus_areas") or []
        focus_text = "\n".join([f"- {a}" for a in focus_areas]) if focus_areas else ""

        assessment = plan.get("assessment") or []
        assessment_text = "\n".join([f"- {a}" for a in assessment]) if assessment else ""

        notes = plan.get("notes") or ""
        
        return f"""
个性化学习计划：

总时长：{plan['total_duration']}
每周学习：{plan['weekly_hours']}小时

重点模块：
{focus_text}

学习里程碑：
{milestones_text}

每日安排：
{schedule_text}

学习资源：
{chr(10).join([f"- {resource}" for resource in plan['resources']])}

评估方式：
{assessment_text}

补充说明：
{notes}

跟踪建议：建议每周进行学习总结，及时调整计划。
        """


class HomeworkGrader(BaseAgent):
    """作业批改助手"""
    
    def __init__(self):
        super().__init__(AgentRole.SOLUTION_EXPERT)
    
    def _get_system_prompt(self) -> str:
        return """你是专业的作业批改助手。职责包括：
1. 批改学生作业
2. 提供详细反馈
3. 指出错误和改进点
4. 给出学习建议
5. 评估学习进度

你的批改应该：
- 准确公正
- 详细具体
- 建设性强
- 鼓励为主
- 有助于提高"""
    
    async def process(self, state: AgentState) -> AgentState:
        """批改作业"""
        state = self.set_current_agent(state)
        
        if state.customer_query:
            # 分析作业内容
            homework_analysis = await self._analyze_homework(state.customer_query.original_message)
            state.metadata["homework_analysis"] = homework_analysis
            
            # 生成批改报告
            grading_report = await self._generate_grading_report(homework_analysis)
            state = self.add_message_to_history(state, grading_report)
        
        return state
    
    async def _analyze_homework(self, message: str) -> Dict[str, Any]:
        """分析作业"""
        return {
            "subject": "编程",
            "type": "代码作业",
            "completion_rate": 0.8,
            "correctness": 0.75,
            "code_quality": 0.7,
            "creativity": 0.8,
            "issues": ["逻辑错误", "代码规范", "注释不足"],
            "strengths": ["思路清晰", "功能完整", "创新性"]
        }
    
    async def _generate_grading_report(self, analysis: Dict[str, Any]) -> str:
        """生成批改报告"""
        return f"""
作业批改报告：

科目：{analysis['subject']}
类型：{analysis['type']}

评分详情：
- 完成度：{analysis['completion_rate']*100:.0f}%
- 正确性：{analysis['correctness']*100:.0f}%
- 代码质量：{analysis['code_quality']*100:.0f}%
- 创新性：{analysis['creativity']*100:.0f}%

主要问题：
{chr(10).join([f"- {issue}" for issue in analysis['issues']])}

优点亮点：
{chr(10).join([f"- {strength}" for strength in analysis['strengths']])}

改进建议：
1. 加强逻辑思维训练
2. 注意代码规范和风格
3. 增加代码注释
4. 多做类似练习

总体评价：作业完成情况良好，建议在代码质量方面继续提升。
        """


class EducationSystem:
    """教育辅导系统"""
    
    def __init__(self):
        self.memory_store = MemoryStore()
        self.course_advisor = CourseAdvisor()
        self.learning_planner = LearningPlanner()
        self.homework_grader = HomeworkGrader()
    
    async def process_education_request(self, session_id: str, message: str) -> Dict[str, Any]:
        """处理教育请求"""
        from src.models.state import CustomerQuery, Message
        import uuid
        
        customer_query = CustomerQuery(
            query_id=str(uuid.uuid4()),
            original_message=message,
            category="education",
            priority="medium"
        )
        
        user_message = Message(
            id=str(uuid.uuid4()),
            type=MessageType.USER_QUERY,
            sender="student",
            content=message
        )
        
        state = AgentState(
            customer_query=customer_query,
            conversation_history=[user_message]
        )

        state = await self.course_advisor.process(state)
        state = await self.learning_planner.process(state)

        homework_keywords = ["作业", "练习", "批改", "改作业", "题", "解题", "答案", "讲题"]
        if any(k in message for k in homework_keywords):
            state = await self.homework_grader.process(state)

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

        result_metadata = state.metadata or {}
        result_history = state.conversation_history or []

        return {
            "session_id": session_id,
            "original_request": message,
            "student_needs": result_metadata.get("student_needs"),
            "course_recommendations": result_metadata.get("course_recommendations"),
            "learning_plan": result_metadata.get("learning_plan"),
            "homework_feedback": result_metadata.get("homework_analysis"),
            "conversation": [getattr(msg, "content", str(msg)) for msg in result_history],
            "answer": _extract_answer(result_history)
        }
    
    async def cleanup(self):
        """清理资源"""
        await self.memory_store.close()
