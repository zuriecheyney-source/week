"""
LangGraph workflow for multi-agent collaboration
"""
import sys
from pathlib import Path
from typing import Dict, Any, Literal
from enum import Enum
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.models.state import AgentState, AgentRole, Message
from src.agents.receptionist import ReceptionistAgent
from src.agents.problem_analyst import ProblemAnalystAgent
from src.agents.solution_expert import SolutionExpertAgent
from src.memory.memory_store import MemoryStore
from src.tools.knowledge_base import KnowledgeBaseTool
from src.tools.web_search import WebSearchTool
from datetime import datetime

class MultiAgentWorkflow:
    """LangGraph workflow for multi-agent customer service system"""
    
    def __init__(self, memory_store: MemoryStore, session_id: str):
        self.memory_store = memory_store
        self.session_id = session_id
        
        # Initialize agents
        self.receptionist = ReceptionistAgent()
        self.problem_analyst = ProblemAnalystAgent()
        self.solution_expert = SolutionExpertAgent()
        
        # Initialize tools
        self.knowledge_base = KnowledgeBaseTool()
        self.web_search = WebSearchTool()
        
        # Initialize LangGraph
        self.graph = self._build_graph()
        
        # Checkpoint saver for persistence
        self.checkpointer = MemorySaver()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes (agents)
        workflow.add_node("receptionist", self._receptionist_node)
        workflow.add_node("problem_analyst", self._problem_analyst_node)
        workflow.add_node("solution_expert", self._solution_expert_node)
        
        # Add conditional edges (routing logic)
        workflow.add_conditional_edges(
            "receptionist",
            self._route_from_receptionist,
            {
                "problem_analyst": "problem_analyst",
                "solution_expert": "solution_expert",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "problem_analyst",
            self._route_from_problem_analyst,
            {
                "solution_expert": "solution_expert",
                "end": END
            }
        )
        
        # Solution expert always ends the workflow
        workflow.add_edge("solution_expert", END)
        
        # Set entry point
        workflow.set_entry_point("receptionist")
        
        return workflow.compile()
    
    async def _receptionist_node(self, state: AgentState) -> AgentState:
        """Receptionist agent node"""
        print("Receptionist Agent processing...")
        
        # Save current state to memory
        await self._save_state_to_memory(state, AgentRole.RECEPTIONIST)
        
        # Process with receptionist
        updated_state = await self.receptionist.process(state)
        
        # Save updated state
        await self._save_state_to_memory(updated_state, AgentRole.RECEPTIONIST)
        
        return updated_state
    
    async def _problem_analyst_node(self, state: AgentState) -> AgentState:
        """Problem analyst agent node"""
        print("Problem Analyst Agent processing...")
        
        # Save current state to memory
        await self._save_state_to_memory(state, AgentRole.PROBLEM_ANALYST)
        
        # Process with problem analyst
        updated_state = await self.problem_analyst.process(state)
        
        # Save updated state
        await self._save_state_to_memory(updated_state, AgentRole.PROBLEM_ANALYST)
        
        return updated_state
    
    async def _solution_expert_node(self, state: AgentState) -> AgentState:
        """Solution expert agent node"""
        print("Solution Expert Agent processing...")
        
        # Save current state to memory
        await self._save_state_to_memory(state, AgentRole.SOLUTION_EXPERT)
        
        # Process with solution expert
        updated_state = await self.solution_expert.process(state)
        
        # Save updated state
        await self._save_state_to_memory(updated_state, AgentRole.SOLUTION_EXPERT)
        
        return updated_state
    
    def _route_from_receptionist(self, state: AgentState) -> Literal["problem_analyst", "solution_expert", "end"]:
        """Route decision from receptionist"""
        if state.handoff_reason:
            if "solution_expert" in state.handoff_reason.lower():
                return "solution_expert"
            elif "problem_analyst" in state.handoff_reason.lower():
                return "problem_analyst"
        
        # Default routing based on analysis
        if state.analysis_result:
            recommended = state.analysis_result.recommended_agent
            if recommended == AgentRole.SOLUTION_EXPERT:
                return "solution_expert"
            elif recommended == AgentRole.PROBLEM_ANALYST:
                return "problem_analyst"
        
        # Default to problem analyst
        return "problem_analyst"
    
    def _route_from_problem_analyst(self, state: AgentState) -> Literal["solution_expert", "end"]:
        """Route decision from problem analyst"""
        if state.handoff_reason and "solution_expert" in state.handoff_reason.lower():
            return "solution_expert"
        
        # If solution is already provided, end workflow
        if state.solution:
            return "end"
        
        # Check if problem analyst provided complete solution
        last_message = state.conversation_history[-1] if state.conversation_history else None
        if last_message and last_message.sender == AgentRole.PROBLEM_ANALYST.value:
            # Check if message contains solution steps
            content = last_message.content.lower()
            if any(keyword in content for keyword in ["step", "solution", "resolve", "fix"]):
                return "end"
        
        # Default to solution expert for complex issues
        return "solution_expert"
    
    async def run_workflow(self, initial_state: AgentState) -> AgentState:
        """Run the complete workflow"""
        print(f"Starting multi-agent workflow for session: {self.session_id}")
        
        try:
            # Run the graph
            config = {"configurable": {"thread_id": self.session_id}}
            result = await self.graph.ainvoke(initial_state, config=config)
            
            print("Workflow completed successfully")
            return result
            
        except Exception as e:
            print(f"Workflow error: {e}")
            # Return the state with error information
            initial_state.metadata["error"] = str(e)
            return initial_state
    
    async def _save_state_to_memory(self, state: AgentState, agent_role: AgentRole):
        """Save agent state to memory store"""
        try:
            # Save conversation messages
            for message in state.conversation_history:
                from src.models.state import MemoryEntry
                
                memory_entry = MemoryEntry(
                    session_id=self.session_id,
                    agent_role=agent_role,
                    message_type=message.type,
                    content=message.content,
                    metadata=message.metadata or {},
                    timestamp=datetime.now()
                )
                
                await self.memory_store.add_memory_entry(memory_entry)
                
            # Save agent state data
            state_data = {
                "customer_query": state.customer_query.dict() if state.customer_query else None,
                "analysis_result": state.analysis_result.dict() if state.analysis_result else None,
                "solution": state.solution.dict() if state.solution else None,
                "current_agent": state.current_agent.value if state.current_agent else None,
                "handoff_reason": state.handoff_reason,
                "metadata": state.metadata
            }
            
            # Handle datetime and Enum serialization
            def to_jsonable(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                if isinstance(obj, Enum):
                    return obj.value
                if isinstance(obj, dict):
                    return {k: to_jsonable(v) for k, v in obj.items()}
                if isinstance(obj, list):
                    return [to_jsonable(item) for item in obj]
                return obj
            
            state_data = to_jsonable(state_data)
            
            await self.memory_store.save_agent_state(self.session_id, agent_role, state_data)
            
        except Exception as e:
            print(f"Error saving to memory: {e}")
    
    async def get_session_history(self) -> Dict[str, Any]:
        """Get session history and summary"""
        return await self.memory_store.get_session_summary(self.session_id)
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.web_search.close()
        await self.memory_store.close()
