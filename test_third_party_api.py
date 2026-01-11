"""
测试第三方OpenAI API配置
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 加载环境变量
load_dotenv()

def test_api_config():
    """测试API配置"""
    print("Testing Third-Party OpenAI API Configuration")
    print("=" * 50)
    
    # 检查环境变量
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    
    print(f"API Key: {'✅ Set' if api_key else '❌ Missing'}")
    print(f"Base URL: {'✅ Set' if base_url else '❌ Missing'}")
    
    if base_url:
        print(f"Base URL: {base_url}")
    
    if not api_key:
        print("\n❌ Error: OPENAI_API_KEY not found")
        print("Please set up your .env file:")
        print("OPENAI_API_KEY=your_third_party_api_key")
        print("OPENAI_BASE_URL=https://your-api-provider.com/v1")
        return False
    
    # 测试导入
    try:
        from src.agents.base_agent import BaseAgent
        from src.models.state import AgentRole
        print("✅ Import successful")
        
        # 创建测试智能体
        class TestAgent(BaseAgent):
            def _get_system_prompt(self) -> str:
                return "You are a test agent."
            
            async def process(self, state):
                return state
        
        agent = TestAgent(AgentRole.RECEPTIONIST)
        print("✅ Agent creation successful")
        
        # 检查LLM配置
        print(f"LLM Model: {agent.llm.model}")
        print(f"LLM Temperature: {agent.llm.temperature}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_simple_scenario():
    """测试简单场景"""
    print("\nTesting Simple Scenario")
    print("=" * 30)
    
    try:
        from src.scenarios.customer_service import CustomerServiceSystem
        print("✅ Customer service system import successful")
        
        # 创建系统实例
        system = CustomerServiceSystem()
        print("✅ System creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Third-Party API Test")
    print("=" * 50)
    
    # 测试API配置
    api_ok = test_api_config()
    
    if api_ok:
        # 测试场景
        scenario_ok = test_simple_scenario()
        
        if scenario_ok:
            print("\n🎉 All tests passed! Your third-party API is configured correctly.")
            print("\nYou can now run:")
            print("python -m src.multi_scenario_main")
        else:
            print("\n⚠️  API config OK, but scenario test failed")
    else:
        print("\n❌ Please fix your API configuration first")
        print("\nSteps:")
        print("1. Copy .env.example to .env")
        print("2. Add your third-party API key and URL")
        print("3. Run this test again")
