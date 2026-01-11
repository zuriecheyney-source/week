"""
Dynamic routing and decision making for multi-agent system
"""
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.models.state import AgentState, AgentRole, AnalysisResult


class RoutingDecision(Enum):
    """Routing decision types"""
    CONTINUE_CURRENT = "continue_current"
    HANDOFF_TO_ANALYST = "handoff_to_analyst"
    HANDOFF_TO_EXPERT = "handoff_to_expert"
    ESCALATE = "escalate"
    END_CONVERSATION = "end_conversation"


class RoutingEngine:
    """Dynamic routing engine for multi-agent system"""
    
    def __init__(self):
        self.routing_rules = self._initialize_routing_rules()
        self.decision_history = []
    
    def _initialize_routing_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize routing rules based on various factors"""
        return {
            "severity_based": {
                "critical": {"target": AgentRole.SOLUTION_EXPERT, "reason": "Critical severity requires expert intervention"},
                "high": {"target": AgentRole.SOLUTION_EXPERT, "reason": "High severity needs expert attention"},
                "medium": {"target": AgentRole.PROBLEM_ANALYST, "reason": "Medium severity needs analysis"},
                "low": {"target": AgentRole.PROBLEM_ANALYST, "reason": "Low severity can be handled by analyst"}
            },
            "category_based": {
                "technical": {"target": AgentRole.SOLUTION_EXPERT, "reason": "Technical issues require expert solutions"},
                "billing": {"target": AgentRole.PROBLEM_ANALYST, "reason": "Billing issues need investigation"},
                "account": {"target": AgentRole.PROBLEM_ANALYST, "reason": "Account issues need analysis"},
                "general": {"target": AgentRole.RECEPTIONIST, "reason": "General inquiries can be handled by receptionist"}
            },
            "confidence_based": {
                "low": {"target": AgentRole.SOLUTION_EXPERT, "reason": "Low confidence requires expert review"},
                "medium": {"target": AgentRole.PROBLEM_ANALYST, "reason": "Medium confidence needs analysis"},
                "high": {"target": AgentRole.AGENT_ROLE, "reason": "High confidence allows current agent to continue"}
            }
        }
    
    async def make_routing_decision(self, state: AgentState, current_agent: AgentRole) -> Tuple[RoutingDecision, AgentRole, str]:
        """Make routing decision based on current state and rules"""
        
        # Analyze current situation
        analysis_factors = await self._analyze_routing_factors(state, current_agent)
        
        # Apply routing rules
        decision = await self._apply_routing_rules(analysis_factors, current_agent)
        
        # Record decision
        self.decision_history.append({
            "timestamp": str(analysis_factors.get("timestamp")),
            "session_context": analysis_factors.get("session_context"),
            "decision": decision.value,
            "reason": decision[2] if isinstance(decision, tuple) else ""
        })
        
        return decision
    
    async def _analyze_routing_factors(self, state: AgentState, current_agent: AgentRole) -> Dict[str, Any]:
        """Analyze factors that influence routing decisions"""
        from datetime import datetime
        
        factors = {
            "timestamp": datetime.now(),
            "current_agent": current_agent,
            "session_context": {
                "message_count": len(state.conversation_history),
                "has_solution": state.solution is not None,
                "has_analysis": state.analysis_result is not None,
                "handoff_reason": state.handoff_reason
            }
        }
        
        # Extract analysis factors if available
        if state.analysis_result:
            factors["severity"] = state.analysis_result.severity
            factors["category"] = state.analysis_result.category
            factors["confidence"] = state.analysis_result.confidence_score
            factors["keywords"] = state.analysis_result.keywords
        
        # Extract query factors if available
        if state.customer_query:
            factors["query_priority"] = state.customer_query.priority
            factors["query_status"] = state.customer_query.status
        
        # Analyze conversation patterns
        factors["conversation_patterns"] = self._analyze_conversation_patterns(state.conversation_history)
        
        return factors
    
    def _analyze_conversation_patterns(self, history: List) -> Dict[str, Any]:
        """Analyze conversation patterns for routing insights"""
        if not history:
            return {"pattern": "no_history"}
        
        # Count messages by type
        agent_messages = [msg for msg in history if msg.sender != "user"]
        user_messages = [msg for msg in history if msg.sender == "user"]
        
        # Check for escalation indicators
        escalation_keywords = ["urgent", "emergency", "critical", "escalate", "manager", "supervisor"]
        escalation_detected = any(
            any(keyword in msg.content.lower() for keyword in escalation_keywords)
            for msg in history
        )
        
        # Check for resolution indicators
        resolution_keywords = ["resolved", "fixed", "solved", "working", "thank you", "thanks"]
        resolution_detected = any(
            any(keyword in msg.content.lower() for keyword in resolution_keywords)
            for msg in history[-3:]  # Check last 3 messages
        )
        
        return {
            "pattern": "analyzed",
            "total_messages": len(history),
            "agent_messages": len(agent_messages),
            "user_messages": len(user_messages),
            "escalation_detected": escalation_detected,
            "resolution_detected": resolution_detected,
            "last_agent": history[-1].sender if history else None
        }
    
    async def _apply_routing_rules(self, factors: Dict[str, Any], current_agent: AgentRole) -> Tuple[RoutingDecision, AgentRole, str]:
        """Apply routing rules to make decision"""
        
        # Check for escalation patterns
        if factors.get("conversation_patterns", {}).get("escalation_detected"):
            return (RoutingDecision.ESCALATE, AgentRole.SOLUTION_EXPERT, "Escalation keywords detected")
        
        # Check for resolution patterns
        if factors.get("conversation_patterns", {}).get("resolution_detected"):
            return (RoutingDecision.END_CONVERSATION, current_agent, "Resolution indicators detected")
        
        # Apply severity-based routing
        severity = factors.get("severity", "medium")
        if severity in self.routing_rules["severity_based"]:
            rule = self.routing_rules["severity_based"][severity]
            return (RoutingDecision.HANDOFF_TO_EXPERT, rule["target"], rule["reason"])
        
        # Apply category-based routing
        category = factors.get("category", "general")
        if category in self.routing_rules["category_based"]:
            rule = self.routing_rules["category_based"][category]
            if rule["target"] != current_agent:
                if rule["target"] == AgentRole.SOLUTION_EXPERT:
                    return (RoutingDecision.HANDOFF_TO_EXPERT, rule["target"], rule["reason"])
                elif rule["target"] == AgentRole.PROBLEM_ANALYST:
                    return (RoutingDecision.HANDOFF_TO_ANALYST, rule["target"], rule["reason"])
        
        # Apply confidence-based routing
        confidence = factors.get("confidence", 0.8)
        if confidence < 0.6:
            rule = self.routing_rules["confidence_based"]["low"]
            return (RoutingDecision.HANDOFF_TO_EXPERT, rule["target"], rule["reason"])
        
        # Default: continue with current agent
        return (RoutingDecision.CONTINUE_CURRENT, current_agent, "Continue with current processing")
    
    async def get_routing_explanation(self, decision: RoutingDecision, 
                                   confidence: float, reason: str) -> str:
        """Generate human-readable explanation for routing decision"""
        explanations = {
            RoutingDecision.CONTINUE_CURRENT: f"Continuing with current agent (confidence: {confidence:.1f}) - {reason}",
            RoutingDecision.HANDOFF_TO_ANALYST: f"Handing off to problem analyst (confidence: {confidence:.1f}) - {reason}",
            RoutingDecision.HANDOFF_TO_EXPERT: f"Handing off to solution expert (confidence: {confidence:.1f}) - {reason}",
            RoutingDecision.ESCALATE: f"Escalating to solution expert (confidence: {confidence:.1f}) - {reason}",
            RoutingDecision.END_CONVERSATION: f"Ending conversation (confidence: {confidence:.1f}) - {reason}"
        }
        
        return explanations.get(decision, f"Unknown routing decision: {decision}")
    
    def get_decision_history(self) -> List[Dict[str, Any]]:
        """Get history of routing decisions"""
        return self.decision_history
    
    def clear_decision_history(self):
        """Clear decision history"""
        self.decision_history = []
    
    async def optimize_routing_rules(self, performance_data: Dict[str, Any]):
        """Optimize routing rules based on performance data"""
        # This would implement machine learning or statistical analysis
        # to optimize routing rules based on historical performance
        
        success_rates = performance_data.get("success_rates", {})
        avg_resolution_times = performance_data.get("avg_resolution_times", {})
        
        # Simple rule optimization based on success rates
        for category, success_rate in success_rates.items():
            if success_rate < 0.7:  # Low success rate
                # Consider changing routing for this category
                if category in self.routing_rules["category_based"]:
                    current_target = self.routing_rules["category_based"][category]["target"]
                    if current_target == AgentRole.PROBLEM_ANALYST:
                        # Try routing to solution expert instead
                        self.routing_rules["category_based"][category]["target"] = AgentRole.SOLUTION_EXPERT
                        self.routing_rules["category_based"][category]["reason"] += " (optimized for success rate)"
        
        print(f"Routing rules optimized based on performance data")
