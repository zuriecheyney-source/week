"""
简化版测试运行脚本
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

def check_env():
    """检查环境配置"""
    print("Environment Check:")
    print(f"OPENAI_API_KEY: {'Set' if os.getenv('OPENAI_API_KEY') else 'Missing'}")
    print(f"OPENAI_BASE_URL: {os.getenv('OPENAI_BASE_URL', 'Not set')}")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_third_party_api_key_here":
        print("\n❌ Please configure your API key in .env file:")
        print("OPENAI_API_KEY=your_actual_api_key")
        print("OPENAI_BASE_URL=https://your-api-provider.com/v1")
        return False
    
    return True

async def test_basic_import():
    """测试基础导入"""
    try:
        from src.multi_scenario_manager import MultiScenarioManager
        print("MultiScenarioManager import successful")
        
        manager = MultiScenarioManager()
        print("Manager creation successful")
        
        # 测试场景检测
        scenario = await manager.detect_scenario("I need help with my account")
        print(f"Scenario detection: {scenario.value}")
        
        return True
    except Exception as e:
        print(f"Import/test failed: {e}")
        return False

async def test_simple_request():
    """测试简单请求"""
    try:
        from src.multi_scenario_manager import MultiScenarioManager
        
        manager = MultiScenarioManager()
        
        # 测试客服场景
        result = await manager.process_request(
            session_id="test_session",
            message="Hello, I need help",
            scenario=None
        )
        
        if "error" in result:
            print(f"Request failed: {result['error']}")
            return False
        else:
            print("Request processed successfully")
            print(f"Scenario: {result.get('scenario')}")
            return True
            
    except Exception as e:
        print(f"Request test failed: {e}")
        return False

async def main():
    """主测试函数"""
    print("Simple Multi-Scenario System Test")
    print("=" * 50)
    
    # 检查环境
    if not check_env():
        return
    
    print("\n1. Testing basic import...")
    import_ok = await test_basic_import()
    
    if import_ok:
        print("\n2. Testing simple request...")
        request_ok = await test_simple_request()
        
        if request_ok:
            print("\nAll tests passed!")
            print("\nYou can now run the full system:")
            print("python -m src.multi_scenario_main")
        else:
            print("\nImport OK but request failed")
    else:
        print("\nBasic import failed")

if __name__ == "__main__":
    asyncio.run(main())
