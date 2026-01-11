# API 参考文档

## 核心类和接口

### AgentState

状态管理核心类，用于在智能体间传递数据。

```python
class AgentState(BaseModel):
    customer_query: Optional[CustomerQuery] = None
    analysis_result: Optional[AnalysisResult] = None
    solution: Optional[Solution] = None
    conversation_history: List[Message] = Field(default_factory=list)
    current_agent: Optional[AgentRole] = None
    handoff_reason: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

**属性说明:**
- `customer_query`: 客户查询信息
- `analysis_result`: 问题分析结果
- `solution`: 解决方案
- `conversation_history`: 对话历史记录
- `current_agent`: 当前处理的智能体
- `handoff_reason`: 交接原因
- `metadata`: 附加元数据

### BaseAgent

所有智能体的基类，定义通用接口。

```python
class BaseAgent(ABC):
    def __init__(self, role: AgentRole)
    
    @abstractmethod
    def _get_system_prompt(self) -> str
    
    @abstractmethod
    async def process(self, state: AgentState) -> AgentState
    
    async def call_llm(self, prompt: str, **kwargs) -> str
    
    def add_message_to_history(self, state: AgentState, content: str, 
                              message_type: MessageType = MessageType.AGENT_RESPONSE,
                              sender: Optional[str] = None) -> AgentState
```

**方法说明:**
- `_get_system_prompt()`: 获取系统提示词
- `process()`: 处理状态并返回更新后的状态
- `call_llm()`: 调用语言模型
- `add_message_to_history()`: 添加消息到历史记录

### ReceptionistAgent

接待员智能体，处理初始客户交互。

```python
class ReceptionistAgent(BaseAgent):
    async def process(self, state: AgentState) -> AgentState
    
    async def _generate_welcome_message(self) -> str
    
    async def _process_initial_query(self, message: str) -> CustomerQuery
    
    async def _analyze_query(self, message: str) -> AnalysisResult
```

**功能特性:**
- 热情专业的问候
- 问题分类和优先级评估
- 智能路由决策
- 信息收集和整理

### ProblemAnalystAgent

问题分析师智能体，进行深度问题分析。

```python
class ProblemAnalystAgent(BaseAgent):
    async def process(self, state: AgentState) -> AgentState
    
    async def _conduct_detailed_investigation(self, state: AgentState) -> Dict[str, Any]
    
    async def _create_detailed_analysis(self, query: CustomerQuery, 
                                      investigation: Dict[str, Any]) -> AnalysisResult
    
    def _determine_handoff(self, analysis: AnalysisResult) -> tuple
```

**功能特性:**
- 深度问题调查
- 根本原因分析
- 影响评估
- 交接决策

### SolutionExpertAgent

解决方案专家智能体，提供专家级解决方案。

```python
class SolutionExpertAgent(BaseAgent):
    async def process(self, state: AgentState) -> AgentState
    
    async def _develop_comprehensive_solution(self, state: AgentState) -> Solution
    
    async def _validate_solution(self, solution: Solution, state: AgentState) -> Dict[str, Any]
    
    async def _create_follow_up_plan(self, solution: Solution) -> Dict[str, Any]
```

**功能特性:**
- 综合解决方案开发
- 方案验证和风险评估
- 详细步骤指导
- 跟进计划制定

## 工作流系统

### MultiAgentWorkflow

多智能体工作流编排器。

```python
class MultiAgentWorkflow:
    def __init__(self, memory_store: MemoryStore, session_id: str)
    
    async def run_workflow(self, initial_state: AgentState) -> AgentState
    
    async def get_session_history(self) -> Dict[str, Any]
    
    async def cleanup(self)
```

**使用示例:**
```python
# 创建工作流
workflow = MultiAgentWorkflow(memory_store, session_id)

# 运行工作流
initial_state = create_initial_state(user_query)
final_state = await workflow.run_workflow(initial_state)

# 获取历史记录
history = await workflow.get_session_history()
```

### RoutingEngine

动态路由引擎。

```python
class RoutingEngine:
    async def make_routing_decision(self, state: AgentState, 
                                  current_agent: AgentRole) -> Tuple[RoutingDecision, AgentRole, str]
    
    async def get_routing_explanation(self, decision: RoutingDecision, 
                                    confidence: float, reason: str) -> str
    
    async def optimize_routing_rules(self, performance_data: Dict[str, Any])
```

**路由决策类型:**
- `CONTINUE_CURRENT`: 继续当前智能体处理
- `HANDOFF_TO_ANALYST`: 交接给问题分析师
- `HANDOFF_TO_EXPERT`: 交接给解决方案专家
- `ESCALATE`: 升级处理
- `END_CONVERSATION`: 结束对话

## 记忆系统

### MemoryStore

持久化记忆存储。

```python
class MemoryStore:
    def __init__(self, db_path: str = "data/agent_memory.db")
    
    async def add_memory_entry(self, entry: MemoryEntry) -> bool
    
    async def get_memory_entries(self, session_id: str, 
                               agent_role: Optional[AgentRole] = None,
                               limit: int = 50,
                               min_importance: float = 0.0) -> List[MemoryEntry]
    
    async def search_memories(self, session_id: str, query: str,
                           agent_role: Optional[AgentRole] = None,
                           limit: int = 10) -> List[MemoryEntry]
    
    async def get_session_summary(self, session_id: str) -> Dict[str, Any]
    
    async def cleanup_old_memories(self, days_to_keep: int = 30) -> int
```

**使用示例:**
```python
# 创建记忆存储
memory_store = MemoryStore()

# 添加记忆条目
entry = MemoryEntry(
    session_id="session_123",
    agent_role=AgentRole.RECEPTIONIST,
    message_type=MessageType.AGENT_RESPONSE,
    content="Welcome to our service!",
    importance_score=0.8
)
await memory_store.add_memory_entry(entry)

# 搜索记忆
results = await memory_store.search_memories("session_123", "welcome")

# 获取会话摘要
summary = await memory_store.get_session_summary("session_123")
```

## 外部工具

### KnowledgeBaseTool

本地知识库搜索工具。

```python
class KnowledgeBaseTool:
    def __init__(self, kb_path: str = "data/knowledge_base.json")
    
    async def search_knowledge_base(self, query: str, 
                                  category: Optional[str] = None, 
                                  limit: int = 5) -> List[Dict[str, Any]]
    
    async def get_article_by_id(self, article_id: str) -> Optional[Dict[str, Any]]
    
    async def add_article(self, title: str, content: str, 
                         category: str, keywords: List[str]) -> str
    
    async def get_categories(self) -> List[str]
```

**使用示例:**
```python
# 创建知识库工具
kb_tool = KnowledgeBaseTool()

# 搜索文章
results = await kb_tool.search_knowledge_base("login issues", "technical")

# 获取特定文章
article = await kb_tool.get_article_by_id("kb_001")

# 添加新文章
article_id = await kb_tool.add_article(
    title="New Feature Guide",
    content="Detailed feature documentation...",
    category="technical",
    keywords=["feature", "guide", "tutorial"]
)
```

### WebSearchTool

网络搜索工具。

```python
class WebSearchTool:
    def __init__(self)
    
    async def search_web(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]
    
    async def get_url_content(self, url: str) -> Optional[str]
    
    async def search_and_extract(self, query: str, 
                                max_content_length: int = 2000) -> Dict[str, Any]
    
    async def close(self)
```

**搜索提供商支持:**
- `mock`: 模拟搜索（测试用）
- `duckduckgo`: DuckDuckGo 搜索
- `serpapi`: SerpApi 搜索（需要 API 密钥）

**使用示例:**
```python
# 创建网络搜索工具
web_tool = WebSearchTool()

# 搜索网络
results = await web_tool.search_web("Python async programming", 10)

# 获取 URL 内容
content = await web_tool.get_url_content("https://example.com/article")

# 搜索并提取内容
result = await web_tool.search_and_extract("machine learning tutorials")
```

## 主系统接口

### CustomerServiceSystem

主系统类，提供完整的客户服务功能。

```python
class CustomerServiceSystem:
    def __init__(self)
    
    async def start_interactive_session(self) -> str
    
    async def handle_customer_query(self, session_id: str, query: str) -> Dict[str, Any]
    
    async def run_interactive_mode(self)
    
    def display_results(self, results: Dict[str, Any])
    
    async def cleanup(self)
```

**使用示例:**
```python
# 创建系统实例
system = CustomerServiceSystem()

# 启动交互式会话
session_id = await system.start_interactive_session()

# 处理客户查询
results = await system.handle_customer_query(session_id, "I can't log in")

# 显示结果
system.display_results(results)

# 清理资源
await system.cleanup()
```

## 数据模型

### 枚举类型

```python
class AgentRole(Enum):
    RECEPTIONIST = "receptionist"
    PROBLEM_ANALYST = "problem_analyst"
    SOLUTION_EXPERT = "solution_expert"

class MessageType(Enum):
    USER_QUERY = "user_query"
    AGENT_RESPONSE = "agent_response"
    HANDOFF = "handoff"
    SYSTEM_NOTIFICATION = "system_notification"
```

### Pydantic 模型

所有数据模型都基于 Pydantic，提供类型安全和数据验证。

```python
# 示例：创建客户查询
query = CustomerQuery(
    query_id="query_123",
    original_message="I need help with my account",
    category="account",
    priority="medium",
    status="pending"
)

# 示例：创建分析结果
analysis = AnalysisResult(
    query_id="query_123",
    category="account",
    severity="medium",
    keywords=["account", "help", "access"],
    sentiment="neutral",
    confidence_score=0.85,
    analysis_summary="Customer needs account assistance",
    recommended_agent=AgentRole.PROBLEM_ANALYST
)
```

## 错误处理

### 异常类型

```python
class EnvironmentError(Exception):
    """环境变量配置错误"""
    pass

class WorkflowError(Exception):
    """工作流执行错误"""
    pass

class MemoryError(Exception):
    """记忆存储错误"""
    pass
```

### 错误处理模式

```python
try:
    results = await system.handle_customer_query(session_id, query)
except EnvironmentError as e:
    print(f"Configuration error: {e}")
except WorkflowError as e:
    print(f"Workflow error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## 配置管理

### 环境变量

```bash
# .env 文件
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./agent_memory.db
DEBUG=True
LOG_LEVEL=INFO
SEARCH_PROVIDER=mock
SERPAPI_KEY=your_serpapi_key
```

### 配置加载

```python
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取配置
api_key = os.getenv("OPENAI_API_KEY")
db_url = os.getenv("DATABASE_URL")
debug = os.getenv("DEBUG", "False").lower() == "true"
```

---

此 API 参考文档提供了完整的接口说明和使用示例，帮助开发者快速理解和使用多智能体系统的各项功能。
