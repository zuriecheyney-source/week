# 多角色协作智能体系统

基于 LangGraph 构建的智能客服系统，实现多智能体协作处理客户问题。

## 演示视频

[演示视频.mp4](./演示视频.mp4)

<video src="./演示视频.mp4" controls width="720"></video>

## 项目概述

本项目实现了一个完整的多智能体客服系统，包含三个专业角色的智能体：

- **接待员智能体**：初步接待和信息收集
- **问题分析师智能体**：深度问题分析和调查
- **解决方案专家智能体**：专家级解决方案生成

## 核心功能

### 多智能体协作
- **3个专业角色**：接待员、问题分析师、解决方案专家
- **动态路由**：基于问题复杂度和类型的智能路由
- **状态管理**：统一的AgentState在智能体间传递数据
- **条件决策**：智能化的工作流决策和切换

### 外部工具集成
- **知识库工具**：本地知识库搜索和管理
- **网络搜索工具**：支持DuckDuckGo和SerpApi搜索
- **内容提取**：URL内容获取和解析

### 记忆持久化
- **会话管理**：多会话支持和隔离
- **对话历史**：完整的消息记录和检索
- **智能体状态**：状态持久化和恢复
- **重要性评分**：智能记忆保留策略

### 智能路由系统
- **动态决策**：基于多个因素的路由决策
- **学习优化**：基于历史数据的路由优化
- **人机协同**：高风险场景的人工介入

## 系统架构

```
用户输入 → LangGraph工作流 → 智能体协作
    ↓
接待员 → 问题分析师 → 解决方案专家
    ↓
记忆存储 ← 外部工具 ← 路由决策
```

## 安装说明

### 环境要求
- Python 3.8+
- OpenAI API Key

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd week1
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，添加你的 OpenAI API Key
```

5. **创建必要目录**
```bash
mkdir -p data
```

## 使用方法

### 交互式运行

```bash
# 推荐：运行多场景系统（自动识别/可手动切换场景）
python -m src.multi_scenario_main

```


### 示例对话

**用户**: "我无法登录我的账户"

**系统响应**:
```
Agent Path: receptionist → problem_analyst → solution_expert

📊 Analysis Results:
  Category: authentication
  Severity: medium
  Keywords: login, account, authentication
  Confidence: 0.85

💡 Solution:
  Type: password_reset
  Estimated Time: 5-10 minutes
  Confidence: 0.92
  
  Steps:
    1. 访问密码重置页面
    2. 输入注册邮箱
    3. 检查重置邮件
    4. 创建新密码
    5. 使用新密码登录
```

### 编程接口使用

```python
import asyncio
from src.main import CustomerServiceSystem

async def main():
    system = CustomerServiceSystem()
    
    # 开始会话
    session_id = await system.start_interactive_session()
    
    # 处理查询
    results = await system.handle_customer_query(
        session_id, 
        "我的订阅被重复收费了"
    )
    
    # 显示结果
    system.display_results(results)
    
    await system.cleanup()

asyncio.run(main())
```

## 项目结构

```
week1/
├── src/
│   ├── __init__.py
│   ├── main.py                 # 主程序入口
│   ├── models/
│   │   ├── __init__.py
│   │   └── state.py           # 数据模型定义
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py      # 智能体基类
│   │   ├── receptionist.py     # 接待员智能体
│   │   ├── problem_analyst.py # 问题分析师智能体
│   │   └── solution_expert.py # 解决方案专家智能体
│   ├── workflow/
│   │   ├── __init__.py
│   │   ├── graph.py           # LangGraph工作流
│   │   └── router.py          # 动态路由系统
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── knowledge_base.py  # 知识库工具
│   │   └── web_search.py      # 网络搜索工具
│   └── memory/
│       ├── __init__.py
│       └── memory_store.py    # 记忆存储系统
├── docs/
│   ├── architecture.md        # 系统架构文档
│   └── api_reference.md       # API参考文档
├── data/                      # 数据存储目录
├── requirements.txt           # Python依赖
├── .env.example              # 环境变量示例
└── README.md                 # 项目说明
```

## 配置说明

### 环境变量

在 `.env` 文件中配置以下变量：

```bash
# 必需
OPENAI_API_KEY=your_openai_api_key_here

# 可选
DATABASE_URL=sqlite:///./agent_memory.db
DEBUG=True
LOG_LEVEL=INFO
SERPAPI_KEY=your_serpapi_key  # 高级网络搜索功能
```

### 智能体配置

每个智能体都可以独立配置：

```python
# 自定义模型
receptionist = ReceptionistAgent()
analyst = ProblemAnalystAgent()
expert = SolutionExpertAgent()

# 自定义工具
kb_tool = KnowledgeBaseTool("path/to/kb.json")
web_tool = WebSearchTool(api_key="your_key")
```

## 测试示例

### 测试不同类型的问题

1. **技术问题**
   ```
   "系统显示错误代码500"
   "API集成失败"
   "数据导出功能不工作"
   ```

2. **账单问题**
   ```
   "我被重复收费了"
   "如何更新支付方式"
   "我想取消订阅"
   ```

3. **账户问题**
   ```
   "我无法重置密码"
   "账户被锁定了"
   "如何修改个人信息"
   ```

4. **复杂问题**
   ```
   "需要将你们的API集成到我们的企业系统中"
   "我们的数据安全合规要求"
   "定制化开发需求"
   ```

## 监控和调试

### 查看会话历史

```python
# 在交互模式中输入 'history' 命令
# 或编程方式访问
summary = await memory_store.get_session_summary(session_id)
print(summary)
```

### 调试模式

设置环境变量启用调试：
```bash
DEBUG=True
LOG_LEVEL=DEBUG
```

### 性能监控

系统提供详细的性能指标：
- 智能体处理时间
- 路由决策统计
- 工具使用情况
- 记忆存储效率

## 扩展开发

### 添加新的智能体

1. 继承 `BaseAgent` 类
2. 实现 `_get_system_prompt()` 方法
3. 实现 `process()` 方法
4. 在工作流中注册新节点

```python
class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentRole.CUSTOM)
    
    def _get_system_prompt(self) -> str:
        return "你是定制化智能体..."
    
    async def process(self, state: AgentState) -> AgentState:
        # 实现处理逻辑
        return state
```

### 添加新工具

1. 创建工具类
2. 实现异步方法
3. 在智能体中集成工具

```python
class CustomTool:
    async def custom_operation(self, query: str) -> Dict[str, Any]:
        # 实现工具逻辑
        return result
```

### 自定义路由规则

```python
# 在 router.py 中添加新规则
routing_rules = {
    "custom_rules": {
        "conditions": ["custom_condition"],
        "action": "route_to_custom_agent"
    }
}
```

## 故障排除

### 常见问题

1. **API Key错误**
   ```
   错误: Missing environment variables: ['OPENAI_API_KEY']
   解决: 检查 .env 文件中的 API Key 配置
   ```

2. **数据库错误**
   ```
   错误: sqlite3.OperationalError: no such table
   解决: 删除 data/ 目录下的数据库文件，重新运行
   ```

3. **依赖冲突**
   ```
   错误: version conflict
   解决: 使用虚拟环境，确保依赖版本正确
   ```

### 日志分析

系统日志包含：
- 智能体处理状态
- 路由决策过程
- 工具调用结果
- 错误详细信息

## 性能优化

### 内存管理
- 定期清理旧记忆数据
- 设置合适的保留策略
- 监控数据库大小

### 并发处理
- 使用异步操作提高性能
- 连接池优化数据库访问
- 缓存常用搜索结果

## 安全考虑

- API密钥安全存储
- 输入数据验证和清理
- 错误信息安全处理
- 会话数据隔离

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。

## 支持

如有问题或建议，请：
- 提交 Issue
- 查看文档
- 联系开发团队

---

**注意**: 这是一个演示项目，用于展示多智能体系统的设计和实现。在生产环境中使用前，请进行充分的测试和安全评估。
