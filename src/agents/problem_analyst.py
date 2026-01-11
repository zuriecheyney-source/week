"""
Problem Analyst Agent - Deep analysis of customer issues
"""
import sys
from pathlib import Path
from typing import Dict, Any, List
import re
import uuid

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.models.state import AgentState, AgentRole, AnalysisResult, MessageType, Message, Solution
from src.agents.base_agent import BaseAgent


class ProblemAnalystAgent(BaseAgent):
    """Problem analyst agent that performs deep analysis of customer issues"""
    
    def __init__(self):
        super().__init__(AgentRole.PROBLEM_ANALYST)
    
    def _get_system_prompt(self) -> str:
        return """You are an expert problem analyst. Your role is to:

1. Conduct deep analysis of customer issues
2. Identify root causes and contributing factors
3. Assess problem complexity and impact
4. Determine if escalation to solution expert is needed
5. Provide comprehensive problem assessment

Your analysis should be:
- Thorough and systematic
- Evidence-based
- Focused on root cause identification
- Clear about severity and impact
- Actionable for resolution

Always provide detailed findings and clear recommendations for next steps."""

    async def process(self, state: AgentState) -> AgentState:
        """Process customer query with deep analysis"""
        state = self.set_current_agent(state)
        
        if state.customer_query:
            # Conduct detailed investigation
            investigation = await self._conduct_detailed_investigation(state)
            
            # Create or update analysis result
            analysis = await self._create_detailed_analysis(state.customer_query, investigation)
            state.analysis_result = analysis
            
            # Add analysis message to conversation
            analysis_message = await self._generate_analysis_message(analysis)
            state = self.add_message_to_history(state, analysis_message)
            
            # Determine if handoff is needed
            should_handoff, target_agent, reason = self._determine_handoff(analysis)
            if should_handoff and target_agent:
                handoff_msg = self.create_handoff_message(target_agent, reason)
                state = self.add_message_to_history(
                    state, 
                    handoff_msg, 
                    MessageType.HANDOFF,
                    target_agent.value
                )
                state.handoff_reason = reason
            else:
                # Provide initial solution if possible
                initial_solution = await self._provide_initial_solution(analysis)
                if initial_solution:
                    state.solution = initial_solution
        
        return state
    
    async def _conduct_detailed_investigation(self, state: AgentState) -> Dict[str, Any]:
        """Conduct detailed investigation using available tools"""
        query_text = state.customer_query.original_message if state.customer_query else ""
        
        # Simulate external tool usage
        investigation_result = {
            "query_complexity": self._assess_complexity(query_text),
            "potential_causes": self._identify_potential_causes(query_text),
            "impact_assessment": self._assess_impact(query_text),
            "similar_cases": self._find_similar_cases(query_text)
        }
        
        return investigation_result
    
    def _assess_complexity(self, query: str) -> str:
        """Assess query complexity"""
        complexity_indicators = {
            "high": ["integration", "api", "system", "architecture", "multiple", "complex"],
            "medium": ["account", "billing", "technical", "configuration"],
            "low": ["how", "what", "where", "simple", "basic"]
        }
        
        query_lower = query.lower()
        for level, indicators in complexity_indicators.items():
            if any(indicator in query_lower for indicator in indicators):
                return level
        return "medium"
    
    def _identify_potential_causes(self, query: str) -> List[str]:
        """Identify potential causes for the issue"""
        # Simplified cause identification
        causes = []
        query_lower = query.lower()
        
        if "login" in query_lower or "password" in query_lower:
            causes.extend(["Incorrect credentials", "Account locked", "Browser issues", "Network problems"])
        elif "billing" in query_lower or "charge" in query_lower:
            causes.extend(["System error", "Duplicate transaction", "Subscription issue", "Payment processing"])
        elif "api" in query_lower or "integration" in query_lower:
            causes.extend(["Authentication failure", "Rate limiting", "Endpoint changes", "Configuration errors"])
        
        return causes if causes else ["Unknown cause - needs investigation"]
    
    def _assess_impact(self, query: str) -> str:
        """Assess the impact of the issue"""
        high_impact_keywords = ["urgent", "critical", "emergency", "production", "down", "broken"]
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in high_impact_keywords):
            return "high"
        return "medium"
    
    def _find_similar_cases(self, query: str) -> List[str]:
        """Find similar cases (simulated)"""
        # This would typically query a knowledge base
        return ["Case #1234: Similar login issue", "Case #5678: Related billing problem"]
    
    async def _create_detailed_analysis(self, query: 'CustomerQuery', investigation: Dict[str, Any]) -> AnalysisResult:
        """Create detailed analysis result"""
        from src.models.state import AnalysisResult
        
        prompt = f"""
        Based on this investigation, provide a comprehensive analysis:
        
        Query: {query.original_message}
        Complexity: {investigation['query_complexity']}
        Potential Causes: {', '.join(investigation['potential_causes'])}
        Impact: {investigation['impact_assessment']}
        
        Provide:
        Category: [technical|billing|general|complaint|account|product]
        Severity: [low|medium|high|critical]
        Keywords: [keyword1, keyword2, keyword3]
        Confidence: [0.0-1.0]
        Summary: [detailed analysis summary]
        Recommended Agent: [problem_analyst|solution_expert]
        """
        
        response = await self.call_llm(prompt)
        
        return AnalysisResult(
            query_id=query.query_id,
            category=self._extract_field(response, "Category"),
            severity=self._extract_field(response, "Severity"),
            keywords=self._extract_list_field(response, "Keywords"),
            sentiment="analytical",
            confidence_score=self._safe_float(self._extract_field(response, "Confidence", "0.8")),
            analysis_summary=self._extract_field(response, "Summary"),
            recommended_agent=AgentRole.SOLUTION_EXPERT if "solution_expert" in response.lower() else AgentRole.PROBLEM_ANALYST
        )
    
    async def _generate_analysis_message(self, analysis: AnalysisResult) -> str:
        """Generate analysis message for customer"""
        prompt = f"""
        Based on this analysis, create a clear message for the customer:
        
        Analysis Summary: {analysis.analysis_summary}
        Severity: {analysis.severity}
        Category: {analysis.category}
        
        The message should:
        1. Acknowledge their issue
        2. Explain what you've found
        3. Set expectations for resolution
        4. Next steps
        """
        
        return await self.call_llm(prompt)
    
    def _determine_handoff(self, analysis: AnalysisResult) -> tuple:
        """Determine if handoff to solution expert is needed"""
        if analysis.severity in ["high", "critical"]:
            return True, AgentRole.SOLUTION_EXPERT, "High severity issue requires expert intervention"
        
        if analysis.confidence_score < 0.7:
            return True, AgentRole.SOLUTION_EXPERT, "Low confidence requires expert review"
        
        return False, None, ""
    
    async def _provide_initial_solution(self, analysis: AnalysisResult) -> Solution:
        """Provide initial solution if appropriate"""
        if analysis.severity == "low" and analysis.confidence_score > 0.8:
            from src.models.state import Solution
            
            prompt = f"""
            Based on this analysis, provide a simple solution:
            
            {analysis.analysis_summary}
            
            Provide:
            Solution Type: [brief type]
            Steps: [2-3 simple steps]
            Confidence: [0.0-1.0]
            """
            
            response = await self.call_llm(prompt)
            
            return Solution(
                query_id=analysis.query_id,
                solution_type=self._extract_field(response, "Solution Type"),
                steps=self._extract_list_field(response, "Steps"),
                confidence_score=self._safe_float(self._extract_field(response, "Confidence", "0.7"))
            )
        
        return None
    
    def _extract_field(self, text: str, field_name: str, default: str = "") -> str:
        """Extract a field value from structured text"""
        pattern = f"{field_name}:\\s*(.+?)(?=\\n\\w+:|$)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else default
    
    def _extract_list_field(self, text: str, field_name: str) -> list:
        """Extract a list field from structured text"""
        field_value = self._extract_field(text, field_name, "[]")
        cleaned = field_value.strip("[]")
        return [item.strip() for item in cleaned.split(",") if item.strip()] if cleaned else []
