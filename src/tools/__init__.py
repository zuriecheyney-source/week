"""
External tools for the multi-agent system
"""

from .knowledge_base import KnowledgeBaseTool
from .web_search import WebSearchTool

__all__ = [
    "KnowledgeBaseTool",
    "WebSearchTool"
]
