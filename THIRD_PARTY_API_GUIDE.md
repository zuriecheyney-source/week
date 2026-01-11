# 第三方OpenAI API配置指南

## 🚀 快速配置

### 1. 设置环境变量

编辑 `.env` 文件，配置您的第三方API：

```bash
# 替换为您的API密钥
OPENAI_API_KEY=your_actual_api_key_here

# 替换为您的API地址
OPENAI_BASE_URL=https://your-api-provider.com/v1
```

### 2. 常见第三方API提供商

#### ChatAnywhere
```bash
OPENAI_API_KEY=sk-your-key-here
OPENAI_BASE_URL=https://api.chatanywhere.com.cn/v1
```

#### OpenAI代理服务
```bash
OPENAI_API_KEY=sk-your-key-here
OPENAI_BASE_URL=https://api.openai-proxy.com/v1
```

#### 自建API服务
```bash
OPENAI_API_KEY=sk-your-key-here
OPENAI_BASE_URL=https://your-custom-domain.com/v1
```

### 3. 验证配置

运行测试脚本验证配置：

```bash
python test_third_party_api.py
```

## 🔧 详细配置说明

### 环境变量说明

| 变量名 | 必需 | 说明 | 示例 |
|--------|------|------|------|
| `OPENAI_API_KEY` | ✅ | API密钥 | `sk-xxxxxxxxxx` |
| `OPENAI_BASE_URL` | ✅ | API地址 | `https://api.example.com/v1` |
| `DATABASE_URL` | ❌ | 数据库地址 | `sqlite:///./agent_memory.db` |
| `DEBUG` | ❌ | 调试模式 | `True` |
| `LOG_LEVEL` | ❌ | 日志级别 | `INFO` |

### API地址格式

第三方API地址通常遵循以下格式：
```
https://your-provider-domain.com/v1
```

确保地址以 `/v1` 结尾，这是OpenAI API的标准路径。

## 🧪 测试和验证

### 1. 基础连接测试

```python
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")

print(f"API Key: {'Set' if api_key else 'Missing'}")
print(f"Base URL: {base_url}")
```

### 2. 智能体测试

```python
from src.agents.base_agent import BaseAgent
from src.models.state import AgentRole

class TestAgent(BaseAgent):
    def _get_system_prompt(self) -> str:
        return "Test agent"
    
    async def process(self, state):
        return state

agent = TestAgent(AgentRole.RECEPTIONIST)
print("Agent created successfully")
```

### 3. 完整系统测试

```bash
# 测试多场景系统
python -m src.multi_scenario_main

# 测试演示脚本
python examples/multi_scenario_demo.py
```

## 🚨 常见问题

### 问题1: API密钥无效
**错误**: `Invalid API key`
**解决**: 
- 检查API密钥是否正确
- 确认密钥格式（通常以`sk-`开头）
- 联系API提供商确认密钥状态

### 问题2: API地址无法访问
**错误**: `Connection refused` 或 `Timeout`
**解决**:
- 检查网络连接
- 确认API地址正确
- 测试API地址是否可访问：`curl https://your-api.com/v1/models`

### 问题3: 模型不支持
**错误**: `Model not found`
**解决**:
- 确认第三方API支持`gpt-3.5-turbo`模型
- 如需其他模型，修改`base_agent.py`中的模型名称

### 问题4: 请求频率限制
**错误**: `Rate limit exceeded`
**解决**:
- 检查API提供商的频率限制
- 在代码中添加请求间隔
- 升级API套餐

## 🔍 调试模式

启用调试模式获取更多信息：

```bash
# 在.env文件中设置
DEBUG=True
LOG_LEVEL=DEBUG
```

或在代码中临时启用：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 配置示例

### 完整的.env文件示例

```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_BASE_URL=https://api.chatanywhere.com.cn/v1

# Database Configuration  
DATABASE_URL=sqlite:///./agent_memory.db

# System Configuration
DEBUG=True
LOG_LEVEL=INFO

# Optional: Search Configuration
SERPAPI_KEY=your_serpapi_key_here
SEARCH_PROVIDER=mock
```

### 自定义模型配置

如果需要使用不同的模型，修改`src/agents/base_agent.py`：

```python
llm_config = {
    "model": "gpt-4",  # 或其他支持的模型
    "temperature": 0.7,
    "openai_api_key": api_key
}
```

## 🎯 下一步

配置完成后，您可以：

1. **运行基础测试**：`python test_third_party_api.py`
2. **启动多场景系统**：`python -m src.multi_scenario_main`
3. **查看演示**：`python examples/multi_scenario_demo.py`
4. **阅读完整文档**：`README_MULTI_SCENARIO.md`

## 📞 获取帮助

如果遇到问题：

1. 检查本指南的常见问题部分
2. 运行测试脚本查看详细错误信息
3. 确认网络连接和API地址可访问性
4. 联系您的API提供商获取技术支持

---

**注意**: 请妥善保管您的API密钥，不要将其提交到版本控制系统或分享给他人。
