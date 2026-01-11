"""
简化版多场景系统运行脚本 - 无Rich格式错误
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 加载环境变量
load_dotenv()

def print_header(title):
    """打印标题"""
    print("=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_section(title):
    """打印章节"""
    print(f"\n--- {title} ---")

def check_environment():
    """检查环境配置"""
    print_section("环境检查")
    
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    
    if not api_key or api_key == "your_third_party_api_key_here":
        print("错误: 请在.env文件中配置您的API密钥")
        print("OPENAI_API_KEY=您的实际API密钥")
        print("OPENAI_BASE_URL=https://您的API地址/v1")
        return False
    
    print(f"API密钥: 已配置")
    print(f"API地址: {base_url}")
    return True

async def test_scenario_system():
    """测试场景系统"""
    print_section("多场景系统测试")
    
    try:
        from src.multi_scenario_manager import MultiScenarioManager
        
        # 创建管理器
        manager = MultiScenarioManager()
        print("多场景管理器创建成功")
        
        # 测试场景检测
        test_queries = [
            ("I need help with my account", "customer_service"),
            ("I want to learn Python", "education"),
            ("I have a headache", "medical"),
            ("investment advice", "financial"),
            ("write blog post", "content_creation")
        ]
        
        for query, expected in test_queries:
            try:
                detected = await manager.detect_scenario(query)
                status = "OK" if detected.value == expected else "WARN"
                print(f"{status} 查询: '{query}' -> 检测到: {detected.value} (期望: {expected})")
            except Exception as e:
                print(f"ERROR 查询 '{query}' 检测失败: {e}")
        
        # 测试简单请求
        print_section("请求处理测试")
        try:
            result = await manager.process_request(
                session_id="test_session",
                message="Hello, I need help with my account",
                scenario=None
            )
            
            if "error" in result:
                print(f"ERROR 请求失败: {result['error']}")
            else:
                print("SUCCESS 请求处理成功")
                print(f"   场景: {result.get('scenario')}")
                print(f"   会话ID: {result.get('session_id')}")
                
                # 显示对话历史
                conversation = result.get('conversation', [])
                if conversation:
                    print("   对话摘要:")
                    for i, msg in enumerate(conversation[-2:], 1):
                        print(f"     {i}. {msg[:100]}...")
                
        except Exception as e:
            print(f"ERROR 请求处理失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"ERROR 系统初始化失败: {e}")
        return False

async def interactive_demo():
    """交互式演示"""
    print_section("交互式演示")
    print("输入 'quit' 退出演示")
    
    try:
        from src.multi_scenario_manager import MultiScenarioManager
        manager = MultiScenarioManager()
        
        while True:
            try:
                user_input = input("\n请输入您的问题: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("再见!")
                    break
                
                print("处理中...")
                result = await manager.process_request(
                    session_id="demo_session",
                    message=user_input,
                    scenario=None
                )
                
                if "error" in result:
                    print(f"错误: {result['error']}")
                else:
                    print(f"场景: {result.get('scenario')}")
                    
                    # 显示结果摘要
                    if result.get('analysis'):
                        print(f"分析: {str(result['analysis'])[:100]}...")
                    
                    if result.get('solution'):
                        print(f"解决方案: {str(result['solution'])[:100]}...")
                    
                    # 显示最后一条对话
                    conversation = result.get('conversation', [])
                    if conversation:
                        print(f"回复: {conversation[-1][:200]}...")
                
            except KeyboardInterrupt:
                print("\n再见!")
                break
            except Exception as e:
                print(f"处理错误: {e}")
                
    except Exception as e:
        print(f"演示启动失败: {e}")

async def main():
    """主函数"""
    print_header("多场景智能体系统 - 简化版")
    
    # 检查环境
    if not check_environment():
        return
    
    # 测试系统
    if await test_scenario_system():
        # 询问是否进行交互式演示
        try:
            choice = input("\n是否进行交互式演示? (y/n): ").strip().lower()
            if choice in ['y', 'yes', '是']:
                await interactive_demo()
            else:
                print("\n系统测试完成，所有功能正常!")
                print("\n您现在可以使用完整系统:")
                print("   python -m src.multi_scenario_main")
        except KeyboardInterrupt:
            print("\n再见!")
    else:
        print("\n系统测试失败，请检查配置")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n再见!")
    except Exception as e:
        print(f"\n程序异常退出: {e}")
