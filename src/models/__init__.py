"""
Data models for the multi-agent system
"""

from .state import (
    AgentState, 
    AgentRole, 
    MessageType, 
    Message, 
    CustomerQuery, 
    AnalysisResult, 
    Solution, 
    MemoryEntry
)

__all__ = [
    "AgentState",
    "AgentRole", 
    "MessageType",
    "Message",
    "CustomerQuery",
    "AnalysisResult", 
    "Solution",
    "MemoryEntry"
]
