"""
最终运行脚本
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
    print("=" * 50)
    print(f" {title}")
    print("=" * 50)

async def main():
    print_header("多场景智能体系统")
    
    # 检查环境
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_third_party_api_key_here":
        print("错误: 请在.env文件中配置您的API密钥")
        return
    
    print(f"API地址: {os.getenv('OPENAI_BASE_URL', '默认')}")
    
    try:
        from src.multi_scenario_manager import MultiScenarioManager
        manager = MultiScenarioManager()
        print("系统初始化成功!")
        
        print("\n可用场景:")
        scenarios = await manager.get_available_scenarios()
        for scenario in scenarios:
            print(f"  - {scenario['id']}: {scenario['name']}")
        
        print("\n测试请求:")
        result = await manager.process_request(
            session_id="demo",
            message="Hello, I need help with my account",
            scenario=None
        )
        
        if "error" in result:
            print(f"错误: {result['error']}")
        else:
            print(f"场景: {result.get('scenario')}")
            print("请求处理成功!")
        
        print("\n系统运行正常!")
        print("您现在可以使用交互式模式:")
        print("python -m src.multi_scenario_main")
        
    except Exception as e:
        print(f"系统启动失败: {e}")

if __name__ == "__main__":
    asyncio.run(main())
