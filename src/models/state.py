"""
State management and data models for the multi-agent system
"""
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class AgentRole(Enum):
    """Agent roles in the system"""
    RECEPTIONIST = "receptionist"
    PROBLEM_ANALYST = "problem_analyst"
    SOLUTION_EXPERT = "solution_expert"


class MessageType(Enum):
    """Message types in conversation"""
    USER_QUERY = "user_query"
    AGENT_RESPONSE = "agent_response"
    HANDOFF = "handoff"
    SYSTEM_NOTIFICATION = "system_notification"


class Message(BaseModel):
    """Message in conversation history"""
    id: str
    type: MessageType
    sender: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CustomerQuery(BaseModel):
    """Customer query information"""
    query_id: str
    original_message: str
    category: Optional[str] = None
    priority: str = "medium"
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.now)


class AnalysisResult(BaseModel):
    """Analysis result from problem analyst"""
    query_id: str
    category: str
    severity: str
    keywords: List[str] = Field(default_factory=list)
    sentiment: str = "neutral"
    confidence_score: float = 0.0
    analysis_summary: str
    recommended_agent: AgentRole
    created_at: datetime = Field(default_factory=datetime.now)


class Solution(BaseModel):
    """Solution provided by solution expert"""
    query_id: str
    solution_type: str
    steps: List[str] = Field(default_factory=list)
    resources: List[str] = Field(default_factory=list)
    confidence_score: float = 0.0
    estimated_resolution_time: Optional[str] = None
    follow_up_required: bool = False
    created_at: datetime = Field(default_factory=datetime.now)


class MemoryEntry(BaseModel):
    """Memory entry for persistent storage"""
    session_id: str
    agent_role: AgentRole
    message_type: MessageType
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    importance_score: float = 0.5


class AgentState(BaseModel):
    """Main state object passed between agents"""
    customer_query: Optional[CustomerQuery] = None
    analysis_result: Optional[AnalysisResult] = None
    solution: Optional[Solution] = None
    conversation_history: List[Message] = Field(default_factory=list)
    current_agent: Optional[AgentRole] = None
    handoff_reason: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True
