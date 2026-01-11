"""
Solution Expert Agent - Provides expert solutions for complex issues
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


class SolutionExpertAgent(BaseAgent):
    """Solution expert agent that provides expert-level solutions"""
    
    def __init__(self):
        super().__init__(AgentRole.SOLUTION_EXPERT)
    
    def _get_system_prompt(self) -> str:
        return """You are an expert solution provider. Your role is to:

1. Analyze complex customer issues in depth
2. Develop comprehensive, expert-level solutions
3. Provide detailed step-by-step resolution plans
4. Assess solution feasibility and risks
5. Offer alternative approaches when needed
6. Ensure solutions are practical and actionable

Your solutions should be:
- Comprehensive and detailed
- Step-by-step and actionable
- Risk-aware with mitigations
- Including resource requirements
- Clear about timeframes and follow-up needs
- Professional and authoritative

Always provide complete solutions with clear next steps and success criteria."""

    async def process(self, state: AgentState) -> AgentState:
        """Process customer query with expert solution"""
        state = self.set_current_agent(state)
        
        if state.customer_query and state.analysis_result:
            # Develop comprehensive solution
            solution = await self._develop_comprehensive_solution(state)
            state.solution = solution
            
            # Validate solution
            validation = await self._validate_solution(solution, state)
            state.metadata["solution_validation"] = validation
            
            # Create solution message
            solution_message = await self._generate_solution_message(solution)
            state = self.add_message_to_history(state, solution_message)
            
            # Add follow-up plan
            follow_up_plan = await self._create_follow_up_plan(solution)
            state.metadata["follow_up_plan"] = follow_up_plan
        
        return state
    
    async def _develop_comprehensive_solution(self, state: AgentState) -> Solution:
        """Develop comprehensive solution for the issue"""
        from src.models.state import Solution
        
        query = state.customer_query
        analysis = state.analysis_result
        
        prompt = f"""
        Develop a comprehensive solution for this customer issue:
        
        Original Query: {query.original_message}
        Analysis Summary: {analysis.analysis_summary}
        Severity: {analysis.severity}
        Category: {analysis.category}
        Keywords: {', '.join(analysis.keywords)}
        
        Provide:
        Solution Type: [clear solution category]
        Steps: [detailed step-by-step instructions]
        Resources: [helpful resources, links, tools]
        Confidence: [0.0-1.0]
        Estimated Time: [timeframe for resolution]
        Follow-up Required: [yes/no]
        Risk Assessment: [potential risks and mitigations]
        """
        
        response = await self.call_llm(prompt)
        
        return Solution(
            query_id=query.query_id,
            solution_type=self._extract_field(response, "Solution Type"),
            steps=self._extract_steps(response),
            resources=self._extract_list_field(response, "Resources"),
            confidence_score=self._safe_float(self._extract_field(response, "Confidence", "0.8")),
            estimated_resolution_time=self._extract_field(response, "Estimated Time"),
            follow_up_required="yes" in self._extract_field(response, "Follow-up Required", "no").lower()
        )
    
    async def _validate_solution(self, solution: Solution, state: AgentState) -> Dict[str, Any]:
        """Validate the solution for feasibility and completeness"""
        validation_prompt = f"""
        Validate this solution for feasibility and completeness:
        
        Solution Type: {solution.solution_type}
        Number of Steps: {len(solution.steps)}
        Resources Provided: {len(solution.resources)}
        Confidence: {solution.confidence_score}
        Estimated Time: {solution.estimated_resolution_time}
        
        Assess:
        1. Feasibility (high/medium/low)
        2. Completeness (high/medium/low)
        3. Clarity (high/medium/low)
        4. Risk Level (high/medium/low)
        5. Overall Quality Score (0.0-1.0)
        """
        
        response = await self.call_llm(validation_prompt)
        
        return {
            "feasibility": self._extract_field(response, "Feasibility"),
            "completeness": self._extract_field(response, "Completeness"),
            "clarity": self._extract_field(response, "Clarity"),
            "risk_level": self._extract_field(response, "Risk Level"),
            "quality_score": self._safe_float(self._extract_field(response, "Overall Quality Score", "0.8"))
        }
    
    async def _generate_solution_message(self, solution: Solution) -> str:
        """Generate a clear solution message for the customer"""
        prompt = f"""
        Create a clear, professional solution message for the customer based on:
        
        Solution Type: {solution.solution_type}
        Steps: {len(solution.steps)} detailed steps
        Estimated Time: {solution.estimated_resolution_time}
        Confidence: {solution.confidence_score}
        
        The message should:
        1. Acknowledge the issue
        2. Present the solution clearly
        3. Explain the steps
        4. Set expectations
        5. Provide reassurance
        """
        
        return await self.call_llm(prompt)
    
    async def _create_follow_up_plan(self, solution: Solution) -> Dict[str, Any]:
        """Create follow-up plan if needed"""
        if not solution.follow_up_required:
            return {"required": False}
        
        follow_up_prompt = f"""
        Create a follow-up plan for this solution:
        
        Solution Type: {solution.solution_type}
        Estimated Time: {solution.estimated_resolution_time}
        Steps Required: {len(solution.steps)}
        
        Provide:
        Follow-up Timing: [when to follow up]
        Success Criteria: [what indicates success]
        Contingency Plan: [if solution doesn't work]
        Contact Method: [preferred contact method]
        """
        
        response = await self.call_llm(follow_up_prompt)
        
        return {
            "required": True,
            "timing": self._extract_field(response, "Follow-up Timing"),
            "success_criteria": self._extract_field(response, "Success Criteria"),
            "contingency_plan": self._extract_field(response, "Contingency Plan"),
            "contact_method": self._extract_field(response, "Contact Method")
        }
    
    def _extract_steps(self, text: str) -> List[str]:
        """Extract steps from solution text"""
        # Look for numbered steps or bullet points
        steps = []
        
        # Try numbered steps first
        numbered_pattern = r'\d+\.\s*([^\n]+)'
        numbered_matches = re.findall(numbered_pattern, text)
        if numbered_matches:
            steps = [match.strip() for match in numbered_matches]
        
        # Try bullet points if no numbered steps
        if not steps:
            bullet_pattern = r'[•\-\*]\s*([^\n]+)'
            bullet_matches = re.findall(bullet_pattern, text)
            if bullet_matches:
                steps = [match.strip() for match in bullet_matches]
        
        return steps if steps else ["Solution steps not clearly formatted"]
    
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
