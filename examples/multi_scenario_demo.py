"""
多场景智能体系统演示脚本
"""
import asyncio
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.multi_scenario_manager import MultiScenarioManager, ScenarioType


async def demo_all_scenarios():
    """演示所有场景"""
    manager = MultiScenarioManager()
    
    print("Multi-Scenario Intelligent Agent System Demo")
    print("=" * 60)
    
    # 测试用例
    test_cases = [
        {
            "scenario": ScenarioType.CUSTOMER_SERVICE,
            "message": "I can't log into my account and was charged twice",
            "description": "智能客服系统测试"
        },
        {
            "scenario": ScenarioType.EDUCATION,
            "message": "I want to learn Python programming and need homework help",
            "description": "教育辅导系统测试"
        },
        {
            "scenario": ScenarioType.MEDICAL,
            "message": "I have headache and nausea for 3 days",
            "description": "医疗咨询系统测试"
        },
        {
            "scenario": ScenarioType.FINANCIAL,
            "message": "I want to invest money with moderate risk tolerance",
            "description": "金融顾问系统测试"
        },
        {
            "scenario": ScenarioType.CONTENT_CREATION,
            "message": "I need to create a blog post about artificial intelligence trends",
            "description": "内容创作系统测试"
        }
    ]
    
    session_id = "demo_session_001"
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nDemo {i}: {test_case['description']}")
        print(f"Scenario: {test_case['scenario'].value}")
        print(f"Message: {test_case['message']}")
        print("-" * 50)
        
        try:
            # 处理请求
            result = await manager.process_request(
                session_id, 
                test_case['message'], 
                test_case['scenario']
            )
            
            # 显示关键结果
            if "error" not in result:
                print(f"Scenario: {result.get('scenario', 'N/A')}")
                
                # 根据场景显示特定信息
                if test_case['scenario'] == ScenarioType.CUSTOMER_SERVICE:
                    agent_path = result.get("agent_path", [])
                    print(f"Agent Path: {' -> '.join(agent_path)}")
                    solution = result.get("solution", {})
                    if solution:
                        print(f"Solution Type: {solution.get('type', 'N/A')}")
                
                elif test_case['scenario'] == ScenarioType.EDUCATION:
                    needs = result.get("student_needs", {})
                    if needs:
                        print(f"Learning Goal: {needs.get('learning_goal', 'N/A')}")
                    courses = result.get("course_recommendations", [])
                    print(f"Recommended Courses: {len(courses)}")
                    plan = result.get("learning_plan", {})
                    if plan:
                        print(f"Learning Plan: {plan.get('total_duration', 'N/A')}")
                
                elif test_case['scenario'] == ScenarioType.MEDICAL:
                    urgency = result.get("urgency", {})
                    if urgency:
                        print(f"Urgency Level: {urgency.get('level', 'N/A')}")
                    diagnoses = result.get("diagnoses", [])
                    print(f"Possible Diagnoses: {len(diagnoses)}")
                    health_plan = result.get("health_plan", {})
                    if health_plan:
                        print(f"Health Plan: Available")
                
                elif test_case['scenario'] == ScenarioType.FINANCIAL:
                    profile = result.get("client_profile", {})
                    if profile:
                        print(f"Financial Goal: {profile.get('financial_goal', 'N/A')}")
                    risk = result.get("risk_profile", {})
                    if risk:
                        print(f"Risk Tolerance: {risk.get('risk_tolerance', 'N/A')}")
                    strategy = result.get("investment_strategy", {})
                    if strategy:
                        print(f"Investment Strategy: {strategy.get('strategy_name', 'N/A')}")
                
                elif test_case['scenario'] == ScenarioType.CONTENT_CREATION:
                    analysis = result.get("content_analysis", {})
                    if analysis:
                        print(f"Content Type: {analysis.get('content_type', 'N/A')}")
                    strategy = result.get("topic_strategy", {})
                    if strategy:
                        print(f"Primary Topic: {strategy.get('primary_topic', 'N/A')}")
                    outline = result.get("content_outline", {})
                    if outline:
                        print(f"Content Title: {outline.get('title', 'N/A')}")
                    review = result.get("quality_review", {})
                    if review:
                        score = review.get('overall_score', 0)
                        print(f"Quality Score: {score}/10")
                
                print("Request processed successfully")
                
            else:
                print(f"Error: {result['error']}")
        
        except Exception as e:
            print(f"Demo error: {e}")
        
        print("=" * 50)
    
    # 清理资源
    await manager.cleanup_all()
    print("\nAll demos completed successfully!")


async def demo_auto_detection():
    """演示自动场景检测"""
    manager = MultiScenarioManager()
    
    print("\nAuto-Detection Demo")
    print("=" * 30)
    
    test_messages = [
        "My account is locked",
        "I need help with math homework",
        "I have chest pain",
        "I want to invest in stocks",
        "Write an article about AI"
    ]
    
    session_id = "auto_detection_session"
    
    for message in test_messages:
        print(f"\nMessage: {message}")
        
        # 自动检测场景
        detected_scenario = await manager.detect_scenario(message)
        print(f"Detected Scenario: {detected_scenario.value}")
        
        # 处理请求
        result = await manager.process_request(session_id, message)
        print(f"Processing Result: {'Success' if 'error' not in result else 'Failed'}")
    
    await manager.cleanup_all()
    print("\nAuto-detection demo completed!")


async def demo_scenario_info():
    """演示场景信息"""
    manager = MultiScenarioManager()
    
    print("\nScenario Information Demo")
    print("=" * 35)
    
    # 获取所有场景信息
    scenarios = await manager.get_available_scenarios()
    
    for scenario in scenarios:
        print(f"\n{scenario['name']}")
        print(f"Description: {scenario['description']}")
        print(f"Features: {', '.join(scenario['features'])}")
        print("-" * 30)
    
    # 获取特定场景详细信息
    print("\nDetailed Scenario Information:")
    for scenario_type in ScenarioType:
        info = manager.get_scenario_info(scenario_type)
        if "error" not in info:
            print(f"\n{scenario_type.value}:")
            print(f"  Agents: {', '.join(info['agents'])}")
            print(f"  Workflow: {info['workflow']}")
            print(f"  Use Cases: {', '.join(info['use_cases'])}")
    
    await manager.cleanup_all()
    print("\nScenario info demo completed!")


async def main():
    """主演示函数"""
    print("Multi-Scenario Intelligent Agent System")
    print("Demo Script")
    print("=" * 50)
    
    # 检查环境
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment variables")
        print("Please set up your .env file")
        return
    
    # 选择演示模式
    print("\nChoose demo mode:")
    print("1. All scenarios demo")
    print("2. Auto-detection demo")
    print("3. Scenario information demo")
    print("4. All demos")
    
    try:
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            await demo_all_scenarios()
        elif choice == "2":
            await demo_auto_detection()
        elif choice == "3":
            await demo_scenario_info()
        elif choice == "4":
            await demo_scenario_info()
            print("\n" + "=" * 50)
            await demo_auto_detection()
            print("\n" + "=" * 50)
            await demo_all_scenarios()
        else:
            print("Invalid choice. Running all demos...")
            await demo_all_scenarios()
            
    except KeyboardInterrupt:
        print("\nDemo cancelled")
    except Exception as e:
        print(f"Demo error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
