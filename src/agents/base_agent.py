"""
Base agent class for all agents in the system
"""
import sys
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Optional, Tuple

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.models.state import AgentState, AgentRole, MessageType, Message
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import os


class BaseAgent(ABC):
    """Base class for all agents in the multi-agent system"""
    
    def __init__(self, role: AgentRole):
        self.role = role
        
        # 支持第三方OpenAI API
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = self._sanitize_base_url(os.getenv("OPENAI_BASE_URL"))
        model = os.getenv("OPENAI_MODEL") or os.getenv("MODEL")
        fallback_models_raw = os.getenv("OPENAI_FALLBACK_MODELS") or ""
        self.fallback_models = [m.strip() for m in fallback_models_raw.split(",") if m.strip()]
        temperature_str = os.getenv("OPENAI_TEMPERATURE")
        try:
            temperature = float(temperature_str) if temperature_str is not None else 0.7
        except ValueError:
            temperature = 0.7

        self.model_name = model or "gpt-3.5-turbo"
        
        self.llm = self._create_llm(self.model_name, api_key=api_key, base_url=base_url, temperature=temperature)
        self.system_prompt = self._get_system_prompt()

    def _sanitize_base_url(self, base_url: Optional[str]) -> Optional[str]:
        if not base_url:
            return base_url
        # Allow users to keep inline comments in .env, e.g. "https://xx/v1  # comment"
        cleaned = base_url.split("#", 1)[0].strip()
        return cleaned or None

    def _create_llm(
        self,
        model_name: str,
        *,
        api_key: Optional[str],
        base_url: Optional[str],
        temperature: float,
    ) -> ChatOpenAI:
        """Create ChatOpenAI with compatibility across langchain_openai versions."""

        # Newer langchain_openai prefers api_key/base_url.
        # Older versions used openai_api_key/openai_api_base.
        candidates = []

        cfg_new = {
            "model": model_name,
            "temperature": temperature,
        }
        if api_key:
            cfg_new["api_key"] = api_key
        if base_url:
            cfg_new["base_url"] = base_url
        candidates.append(cfg_new)

        cfg_old = {
            "model": model_name,
            "temperature": temperature,
        }
        if api_key:
            cfg_old["openai_api_key"] = api_key
        if base_url:
            cfg_old["openai_api_base"] = base_url
        candidates.append(cfg_old)

        last_err: Optional[Exception] = None
        for cfg in candidates:
            try:
                return ChatOpenAI(**cfg)
            except TypeError as e:
                last_err = e
                continue

        # If we get here, the installed langchain_openai has an unexpected signature.
        raise last_err or RuntimeError("Failed to initialize ChatOpenAI")

    def _build_llm(self, model_name: str) -> ChatOpenAI:
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = self._sanitize_base_url(os.getenv("OPENAI_BASE_URL"))
        temperature_str = os.getenv("OPENAI_TEMPERATURE")
        try:
            temperature = float(temperature_str) if temperature_str is not None else 0.7
        except ValueError:
            temperature = 0.7

        return self._create_llm(model_name, api_key=api_key, base_url=base_url, temperature=temperature)

    def _is_model_forbidden_error(self, exc: Exception) -> bool:
        msg = str(exc)
        return (
            "Error code: 403" in msg
            or "无权访问模型" in msg
            or "doesn't have access" in msg
            or "not have access" in msg
        )
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Get the system prompt for this agent"""
        pass
    
    @abstractmethod
    async def process(self, state: AgentState) -> AgentState:
        """Process the state and return updated state"""
        pass
    
    def add_message_to_history(
        self, 
        state: AgentState, 
        content: str, 
        message_type: MessageType = MessageType.AGENT_RESPONSE,
        sender: Optional[str] = None
    ) -> AgentState:
        """Add a message to conversation history"""
        import uuid
        
        message = Message(
            id=str(uuid.uuid4()),
            type=message_type,
            sender=sender or self.role.value,
            content=content,
            metadata={"agent_role": self.role.value}
        )
        
        state.conversation_history.append(message)
        return state
    
    def set_current_agent(self, state: AgentState) -> AgentState:
        """Set this agent as the current agent in the state"""
        state.current_agent = self.role
        return state
    
    async def call_llm(self, prompt: str, **kwargs) -> str:
        """Call the language model with a prompt"""
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt),
        ]

        def _is_transient_error(exc: Exception) -> bool:
            msg = str(exc).lower()
            return (
                "timeout" in msg
                or "timed out" in msg
                or "connection" in msg
                or "connect" in msg
                or "temporarily" in msg
                or "502" in msg
                or "503" in msg
                or "504" in msg
            )

        try:
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            # One retry for transient failures (network / gateway)
            if _is_transient_error(e):
                try:
                    response = await self.llm.ainvoke(messages)
                    return response.content
                except Exception:
                    pass

            # Auto fallback when the token is forbidden to access the configured model.
            if self._is_model_forbidden_error(e) and self.fallback_models:
                last_error = e
                for fallback_model in self.fallback_models:
                    try:
                        fallback_llm = self._build_llm(fallback_model)
                        response = await fallback_llm.ainvoke(messages)
                        # Switch permanently for subsequent calls
                        self.llm = fallback_llm
                        self.model_name = fallback_model
                        return response.content
                    except Exception as e2:
                        last_error = e2
                raise last_error

            if self._is_model_forbidden_error(e):
                raise RuntimeError(
                    f"Model access forbidden. model={self.model_name}, fallbacks={self.fallback_models}. Original error: {e}"
                )

            raise
    
    def should_handoff(self, state: AgentState) -> Tuple[bool, Optional[AgentRole], str]:
        """Determine if handoff is needed and to which agent"""
        return False, None, ""
    
    def create_handoff_message(self, target_agent: AgentRole, reason: str) -> str:
        """Create a handoff message"""
        return f"[HANDOFF_TO_{target_agent.value.upper()}] Reason: {reason}"
    
    def _safe_float(self, value_str: str, default: float = 0.8) -> float:
        """Safely convert string to float, handling markdown formatting"""
        try:
            import re
            # Find numbers in the string
            match = re.search(r'(\d+\.?\d*)', value_str.replace('**', ''))
            if match:
                return float(match.group(1))
            return default
        except (ValueError, AttributeError):
            return default
