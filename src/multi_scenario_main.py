"""
多场景智能体系统主程序
"""
import asyncio
import uuid
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.markdown import Markdown

from src.utils.runtime import configure_stdio

from src.multi_scenario_manager import MultiScenarioManager, ScenarioType
from src.models.state import MessageType


class MultiScenarioSystem:
    """多场景智能体系统主类"""
    
    def __init__(self):
        configure_stdio()
        self.console = Console(markup=False, emoji=False)

        # 加载环境变量（必须早于manager/agents初始化，否则会读到旧环境变量）
        load_dotenv()

        self.manager = MultiScenarioManager()
        
        # 验证环境
        self._validate_environment()
    
    def _safe_print(self, message: str, style: str = None):
        """安全的打印函数，防止Rich标记错误"""
        try:
            if style:
                # 使用Rich的style参数而不是标记
                self.console.print(message, style=style)
            else:
                self.console.print(message)
        except Exception:
            # 如果Rich格式化失败，使用普通打印
            print(message)
    
    def _validate_environment(self):
        """验证环境配置"""
        required_vars = ["OPENAI_API_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            self._safe_print(f"Error: Missing environment variables: {missing_vars}", "red")
            self._safe_print("Please set up your .env file with required variables", "yellow")
            raise EnvironmentError(f"Missing environment variables: {missing_vars}")
    
    async def start_session(self) -> str:
        """启动多场景会话"""
        session_id = str(uuid.uuid4())
        
        self.console.print(Panel(
            Text("Multi-Scenario Intelligent Agent System", style="bold blue"),
            subtitle="5 Professional Scenarios Powered by LangGraph"
        ))
        
        self.console.print("\nMulti-Scenario Session Started!", style="green")
        self.console.print(f"Session ID: {session_id}", style="dim")
        
        return session_id
    
    async def show_available_scenarios(self):
        """显示可用场景"""
        scenarios = await self.manager.get_available_scenarios()
        
        table = Table(title="Available Scenarios")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Agents", style="green")
        table.add_column("Features", style="yellow")
        
        for scenario in scenarios:
            features_text = ", ".join(scenario["features"][:2]) + "..."
            table.add_row(
                scenario["id"],
                scenario["name"],
                scenario["description"],
                features_text
            )
        
        self.console.print(table)
    
    async def process_request(self, session_id: str, message: str, scenario: Optional[str] = None) -> Dict[str, Any]:
        """处理用户请求"""
        try:
            # 如果指定了场景，转换为枚举
            target_scenario = None
            if scenario:
                try:
                    target_scenario = ScenarioType(scenario)
                except ValueError:
                    try:
                        self._safe_print(f"Invalid scenario: {scenario}", "red")
                    except:
                        print(f"Invalid scenario: {scenario}")
                    return {"error": f"Invalid scenario: {scenario}"}
            
            # 处理请求
            result = await self.manager.process_request(session_id, message, target_scenario)
            
            return result
            
        except Exception as e:
            try:
                self._safe_print(f"Error processing request: {e}", "red")
            except:
                print(f"Error processing request: {e}")
            return {"error": str(e), "session_id": session_id}
    
    def display_result(self, result: Dict[str, Any]):
        """显示处理结果"""
        if "error" in result:
            try:
                self._safe_print(f"Error: {result['error']}", "red")
            except:
                print(f"Error: {result['error']}")
            return
        
        scenario = result.get("scenario", "unknown")
        self.console.print(f"\nScenario: {scenario}", style="bold blue")

        answer = result.get("answer")
        if isinstance(answer, str) and answer.strip():
            self.console.print(Panel(Markdown(answer), title="Answer", border_style="green"))
            return
        
        # 根据场景显示不同的结果格式
        if scenario == "customer_service":
            self._display_customer_service_result(result)
        elif scenario == "education":
            self._display_education_result(result)
        elif scenario == "medical":
            self._display_medical_result(result)
        elif scenario == "financial":
            self._display_financial_result(result)
        elif scenario == "content_creation":
            self._display_content_creation_result(result)
        else:
            self._display_generic_result(result)
    
    def _display_customer_service_result(self, result: Dict[str, Any]):
        """显示客服系统结果"""
        agent_path = result.get("agent_path", [])
        if agent_path:
            self.console.print(f"Agent Path: {' -> '.join(agent_path)}", style="cyan")
        
        analysis = result.get("analysis", {})
        if analysis:
            self.console.print(f"Analysis: {analysis.get('complexity', 'N/A')}", style="yellow")
        
        solution = result.get("solution", {})
        if solution:
            self.console.print(f"Solution: {solution.get('type', 'N/A')}", style="green")
    
    def _display_education_result(self, result: Dict[str, Any]):
        """显示教育系统结果"""
        needs = result.get("student_needs", {})
        if needs:
            self.console.print(f"Learning Goal: {needs.get('learning_goal', 'N/A')}", style="cyan")
        
        courses = result.get("course_recommendations", [])
        if courses:
            self.console.print(f"Recommended Courses: {len(courses)} courses", style="yellow")
        
        plan = result.get("learning_plan", {})
        if plan:
            self.console.print(f"Learning Plan: {plan.get('total_duration', 'N/A')}", style="green")
    
    def _display_medical_result(self, result: Dict[str, Any]):
        """显示医疗系统结果"""
        symptoms = result.get("symptoms", {})
        if symptoms:
            self.console.print(f"Symptoms: {symptoms.get('symptom_type', 'N/A')}", style="cyan")
        
        urgency = result.get("urgency", {})
        if urgency:
            self.console.print(f"Urgency: {urgency.get('level', 'N/A')}", style="red")
        
        diagnoses = result.get("diagnoses", [])
        if diagnoses:
            self.console.print(f"Possible Diagnoses: {len(diagnoses)} possibilities", style="yellow")
        
        health_plan = result.get("health_plan", {})
        if health_plan:
            self.console.print("Health Plan: Available", style="green")
    
    def _display_financial_result(self, result: Dict[str, Any]):
        """显示金融系统结果"""
        profile = result.get("client_profile", {})
        if profile:
            self.console.print(f"Financial Goal: {profile.get('financial_goal', 'N/A')}", style="cyan")
        
        risk = result.get("risk_profile", {})
        if risk:
            self.console.print(f"Risk Level: {risk.get('risk_tolerance', 'N/A')}", style="yellow")
        
        strategy = result.get("investment_strategy", {})
        if strategy:
            self.console.print(f"Strategy: {strategy.get('strategy_name', 'N/A')}", style="green")
    
    def _display_content_creation_result(self, result: Dict[str, Any]):
        """显示内容创作结果"""
        analysis = result.get("content_analysis", {})
        if analysis:
            self.console.print(f"Content Type: {analysis.get('content_type', 'N/A')}", style="cyan")
        
        strategy = result.get("topic_strategy", {})
        if strategy:
            self.console.print(f"Primary Topic: {strategy.get('primary_topic', 'N/A')}", style="yellow")
        
        outline = result.get("content_outline", {})
        if outline:
            self.console.print(f"Content Outline: {outline.get('title', 'N/A')}", style="green")
        
        review = result.get("quality_review", {})
        if review:
            score = review.get('overall_score', 0)
            self.console.print(f"Quality Score: {score}/10", style="magenta")
    
    def _display_generic_result(self, result: Dict[str, Any]):
        """显示通用结果"""
        self.console.print("Request processed successfully", style="green")
        
        # 显示对话历史
        conversation = result.get("conversation", [])
        if conversation:
            self.console.print("\nConversation Summary:", style="bold")
            for i, msg in enumerate(conversation[-3:], 1):  # 显示最后3条
                self.console.print(f"  {i}. {msg[:100]}...")
    
    async def run_interactive_mode(self):
        """运行交互模式"""
        session_id = await self.start_session()
        
        # 显示可用场景
        await self.show_available_scenarios()
        
        self.console.print("\nCommands:", style="yellow")
        self.console.print("  help - Show this help", style="bold")
        self.console.print("  scenarios - Show available scenarios", style="bold")
        self.console.print("  scenario <type> - Switch to specific scenario", style="bold")
        self.console.print("  quit - Exit the system", style="bold")
        self.console.print("\nAvailable Scenarios:", style="bold")
        self.console.print("  customer_service, education, medical, financial, content_creation")
        
        current_scenario = None
        
        while True:
            try:
                # 获取用户输入
                self.console.print("\nYour request: ", style="bold blue", end="")
                user_input = self.console.input().strip()
                
                if not user_input:
                    continue
                
                # 处理命令
                if user_input.lower() in ['quit', 'exit', 'q']:
                    self.console.print("Goodbye!", style="green")
                    break
                
                if user_input.lower() == 'help':
                    await self._show_help()
                    continue
                
                if user_input.lower() == 'scenarios':
                    await self.show_available_scenarios()
                    continue
                
                if user_input.lower().startswith('scenario '):
                    scenario_name = user_input[9:].strip()
                    try:
                        current_scenario = ScenarioType(scenario_name)
                        switch_result = await self.manager.switch_scenario(session_id, current_scenario)
                        self.console.print(f"{switch_result['message']}", style="green")
                    except ValueError:
                        try:
                            self._safe_print(f"Invalid scenario: {scenario_name}", "red")
                        except:
                            print(f"Invalid scenario: {scenario_name}")
                        continue
                
                # 处理普通请求
                self.console.print("Processing your request...", style="dim")
                result = await self.process_request(session_id, user_input, current_scenario)
                self.display_result(result)
                
            except KeyboardInterrupt:
                self.console.print("\nGoodbye!", style="green")
                break
            except Exception as e:
                try:
                    self._safe_print(f"Unexpected error: {str(e)}", "red")
                except:
                    # 如果Rich格式化失败，使用普通打印
                    print(f"Unexpected error: {str(e)}")
    
    async def _show_help(self):
        """显示帮助信息"""
        help_text = """
Multi-Scenario Intelligent Agent System Help

COMMANDS:
  help                    - Show this help message
  scenarios               - List all available scenarios
  scenario <type>         - Switch to specific scenario
  quit                    - Exit the system

AVAILABLE SCENARIOS:
  customer_service         - Smart customer service system
  education               - Education tutoring system  
  medical                 - Medical consultation system
  financial               - Financial advisory system
  content_creation        - Content creation system

EXAMPLES:
  "I need help with my account"           # Auto-detects customer_service
  "scenario education I want to learn Python"  # Force education scenario
  "scenario medical I have a headache"    # Force medical scenario
  "scenario financial investment advice"   # Force financial scenario
  "scenario content blog post about AI"     # Force content creation

FEATURES:
  - Automatic scenario detection
  - Multi-agent collaboration
  - Memory persistence
  - Dynamic routing
  - External tool integration
        """
        
        self.console.print(help_text)
    
    async def cleanup(self):
        """清理资源"""
        await self.manager.cleanup_all()


async def main():
    """主函数"""
    system = MultiScenarioSystem()
    
    try:
        await system.run_interactive_mode()
    finally:
        await system.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
