"""
Receptionist Agent - First point of contact for customer queries
"""
import sys
from pathlib import Path
from typing import Optional
import re
import uuid

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.models.state import AgentState, AgentRole, AnalysisResult, MessageType, Message, Solution
from src.agents.base_agent import BaseAgent


class ReceptionistAgent(BaseAgent):
    """Receptionist agent that handles initial customer interactions"""
    
    def __init__(self):
        super().__init__(AgentRole.RECEPTIONIST)
    
    def _get_system_prompt(self) -> str:
        return """You are a professional customer service receptionist. Your role is to:

1. Greet customers warmly and professionally
2. Understand the initial customer query
3. Gather basic information about the issue
4. Categorize the problem type (technical, billing, general inquiry, complaint, etc.)
5. Assess urgency level (low, medium, high, critical)
6. Prepare the query for handoff to the appropriate specialist

Your responses should be:
- Friendly and welcoming
- Clear and concise
- Professional but approachable
- Focused on information gathering

Always end your interaction by explaining that you'll connect them to the right specialist."""

    async def process(self, state: AgentState) -> AgentState:
        """Process customer query and prepare for handoff"""
        state = self.set_current_agent(state)
        
        if not state.customer_query:
            # Handle new customer query
            welcome_message = await self._generate_welcome_message()
            state = self.add_message_to_history(state, welcome_message)
            
            # For demo purposes, we'll simulate we have the query
            if state.conversation_history and len(state.conversation_history) > 1:
                user_message = state.conversation_history[-2].content
                state.customer_query = await self._process_initial_query(user_message)
        
        if state.customer_query:
            # Analyze and categorize the query
            analysis = await self._analyze_query(state.customer_query.original_message)
            
            # Add analysis to state
            state.analysis_result = analysis
            state.metadata["receptionist_notes"] = analysis.analysis_summary
            
            # Create handoff message
            handoff_msg = self.create_handoff_message(
                analysis.recommended_agent, 
                f"Query categorized as {analysis.category} with {analysis.severity} severity"
            )
            state = self.add_message_to_history(
                state, 
                handoff_msg, 
                MessageType.HANDOFF,
                analysis.recommended_agent.value
            )
            state.handoff_reason = f"Category: {analysis.category}, Severity: {analysis.severity}"
        
        return state
    
    async def _generate_welcome_message(self) -> str:
        """Generate a welcome message"""
        prompt = "Generate a warm, professional welcome message for a customer service chat."
        return await self.call_llm(prompt)
    
    async def _process_initial_query(self, message: str) -> 'CustomerQuery':
        """Process the initial customer query"""
        from src.models.state import CustomerQuery
        
        prompt = f"""
        Extract and summarize the customer's issue from this message:
        "{message}"
        
        Provide:
        1. Brief summary of the issue
        2. Initial category guess
        3. Urgency assessment
        """
        
        response = await self.call_llm(prompt)
        
        return CustomerQuery(
            query_id=str(uuid.uuid4()),
            original_message=message,
            category=response.split("Category:")[1].split("\n")[0].strip() if "Category:" in response else "general",
            priority=response.split("Urgency:")[1].strip() if "Urgency:" in response else "medium"
        )
    
    async def _analyze_query(self, message: str) -> AnalysisResult:
        """Analyze the query to determine routing"""
        from src.models.state import AnalysisResult
        
        prompt = f"""
        Analyze this customer query and provide routing information:
        "{message}"
        
        Respond with:
        Category: [technical|billing|general|complaint|account|product]
        Severity: [low|medium|high|critical]
        Keywords: [keyword1, keyword2, keyword3]
        Sentiment: [positive|neutral|negative]
        Confidence: [0.0-1.0]
        Summary: [brief analysis summary]
        Recommended Agent: [receptionist|problem_analyst|solution_expert]
        """
        
        response = await self.call_llm(prompt)
        
        # Parse the response
        category = self._extract_field(response, "Category")
        severity = self._extract_field(response, "Severity")
        keywords = self._extract_list_field(response, "Keywords")
        sentiment = self._extract_field(response, "Sentiment")
        confidence = self._safe_float(self._extract_field(response, "Confidence", "0.8"))
        summary = self._extract_field(response, "Summary")
        recommended_agent_str = self._extract_field(response, "Recommended Agent", "problem_analyst")
        
        # Map recommended agent to enum
        agent_mapping = {
            "problem_analyst": AgentRole.PROBLEM_ANALYST,
            "solution_expert": AgentRole.SOLUTION_EXPERT,
            "receptionist": AgentRole.RECEPTIONIST
        }
        recommended_agent = agent_mapping.get(recommended_agent_str, AgentRole.PROBLEM_ANALYST)
        
        return AnalysisResult(
            query_id=str(uuid.uuid4()),
            category=category,
            severity=severity,
            keywords=keywords,
            sentiment=sentiment,
            confidence_score=confidence,
            analysis_summary=summary,
            recommended_agent=recommended_agent
        )
    
    def _extract_field(self, text: str, field_name: str, default: str = "") -> str:
        """Extract a field value from structured text"""
        pattern = f"{field_name}:\\s*(.+?)(?=\\n\\w+:|$)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else default
    
    def _extract_list_field(self, text: str, field_name: str) -> list:
        """Extract a list field from structured text"""
        field_value = self._extract_field(text, field_name, "[]")
        # Remove brackets and split by comma
        cleaned = field_value.strip("[]")
        return [item.strip() for item in cleaned.split(",") if item.strip()] if cleaned else []
