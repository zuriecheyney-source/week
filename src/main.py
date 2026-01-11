"""
Main application entry point for multi-agent customer service system
"""
import asyncio
import uuid
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any, Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.runtime import configure_stdio
from src.models.state import AgentState, CustomerQuery, Message, MessageType
from src.workflow.graph import MultiAgentWorkflow
from src.memory.memory_store import MemoryStore
from src.tools.knowledge_base import KnowledgeBaseTool
from src.tools.web_search import WebSearchTool


class CustomerServiceSystem:
    """Main customer service system orchestrator"""
    
    def __init__(self):
        configure_stdio()
        self.console = Console(markup=False, emoji=False)
        self.memory_store = MemoryStore()
        self.knowledge_base = KnowledgeBaseTool()
        self.web_search = WebSearchTool()
        
        # Load environment variables
        load_dotenv()
        
        # Validate environment
        self._validate_environment()
    
    def _validate_environment(self):
        """Validate required environment variables"""
        required_vars = ["OPENAI_API_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            self.console.print(f"Error: Missing environment variables: {missing_vars}", style="red")
            self.console.print("Please set up your .env file with the required variables", style="yellow")
            raise EnvironmentError(f"Missing environment variables: {missing_vars}")
    
    async def start_interactive_session(self) -> str:
        """Start an interactive customer service session"""
        session_id = str(uuid.uuid4())
        
        self.console.print(Panel(
            Text("Multi-Agent Customer Service System", style="bold blue"),
            subtitle="Powered by LangGraph"
        ))
        
        self.console.print("\nSession started!", style="green")
        self.console.print(f"Session ID: {session_id}", style="dim")
        self.console.print("\nType 'quit' to exit, 'help' for commands\n", style="yellow")
        
        return session_id
    
    async def handle_customer_query(self, session_id: str, query: str) -> Dict[str, Any]:
        """Handle a customer query through the multi-agent system"""
        try:
            # Create initial state
            initial_state = self._create_initial_state(query)
            
            # Create workflow
            workflow = MultiAgentWorkflow(self.memory_store, session_id)
            
            # Run workflow
            final_state = await workflow.run_workflow(initial_state)
            
            # Extract results
            results = self._extract_results(final_state)
            
            # Cleanup
            await workflow.cleanup()
            
            return results
            
        except Exception as e:
            self.console.print(f"Error processing query: {e}", style="red")
            return {"error": str(e), "status": "failed"}
    
    def _create_initial_state(self, query: str) -> AgentState:
        """Create initial agent state from customer query"""
        import uuid
        
        customer_query = CustomerQuery(
            query_id=str(uuid.uuid4()),
            original_message=query,
            category=None,
            priority="medium",
            status="pending"
        )
        
        # Add user message to conversation history
        user_message = Message(
            id=f"user_{uuid.uuid4()}",
            type=MessageType.USER_QUERY,
            sender="user",
            content=query,
            metadata={"source": "interactive"}
        )
        
        return AgentState(
            customer_query=customer_query,
            conversation_history=[user_message],
            current_agent=None,
            metadata={"session_start": str(uuid.uuid4())}
        )
    
    def _extract_results(self, state) -> Dict[str, Any]:
        """Extract results from the final agent state"""
        # Handle both AgentState and dict objects
        if hasattr(state, 'customer_query'):
            # It's an AgentState object
            customer_query = state.customer_query.dict() if state.customer_query else None
            analysis_result = state.analysis_result.dict() if state.analysis_result else None
            solution = state.solution.dict() if state.solution else None
            conversation_history = [msg.dict() for msg in state.conversation_history]
            metadata = state.metadata
        else:
            # It's a dict object
            customer_query = state.get('customer_query')
            analysis_result = state.get('analysis_result')
            solution = state.get('solution')
            conversation_history = state.get('conversation_history', [])
            metadata = state.get('metadata', {})
        
        results = {
            "status": "completed",
            "customer_query": customer_query,
            "analysis_result": analysis_result,
            "solution": solution,
            "conversation_history": conversation_history,
            "agent_path": self._extract_agent_path(conversation_history),
            "metadata": metadata
        }
        
        return results
    
    def _extract_agent_path(self, history: list) -> List[str]:
        """Extract the path of agents that handled the conversation"""
        agents = []
        for message in history:
            if hasattr(message, 'sender'):
                sender = message.sender
            else:
                sender = message.get('sender', 'unknown')
            
            if sender not in ["user"] and sender not in agents:
                agents.append(sender)
        return agents
    
    def display_results(self, results: Dict[str, Any]):
        """Display the results in a formatted way"""
        if "error" in results:
            self.console.print(f"Error: {results['error']}", style="red")
            return
        
        # Display agent path
        agent_path = results.get("agent_path", [])
        if agent_path:
            path_text = " -> ".join(agent_path)
            self.console.print(f"Agent Path: {path_text}", style="blue")
        
        # Display analysis
        analysis = results.get("analysis_result")
        if analysis:
            if hasattr(analysis, 'category'):
                # It's a Pydantic model
                self.console.print("\nAnalysis Results:", style="bold")
                self.console.print(f"  Category: {analysis.category}")
                self.console.print(f"  Severity: {analysis.severity}")
                self.console.print(f"  Keywords: {', '.join(analysis.keywords)}")
                self.console.print(f"  Confidence: {analysis.confidence_score:.2f}")
            else:
                # It's a dict
                self.console.print("\nAnalysis Results:", style="bold")
                self.console.print(f"  Category: {analysis.get('category', 'N/A')}")
                self.console.print(f"  Severity: {analysis.get('severity', 'N/A')}")
                self.console.print(f"  Keywords: {', '.join(analysis.get('keywords', []))}")
                self.console.print(f"  Confidence: {analysis.get('confidence_score', 0):.2f}")
        
        # Display solution
        solution = results.get("solution")
        if solution:
            if hasattr(solution, 'solution_type'):
                # It's a Pydantic model
                self.console.print("\nSolution:", style="bold")
                self.console.print(f"  Type: {solution.solution_type}")
                self.console.print(f"  Estimated Time: {solution.estimated_resolution_time}")
                self.console.print(f"  Confidence: {solution.confidence_score:.2f}")
                
                steps = solution.steps
                if steps:
                    self.console.print("\n  Steps:", style="bold")
                    for i, step in enumerate(steps, 1):
                        self.console.print(f"    {i}. {step}")
                
                resources = solution.resources
                if resources:
                    self.console.print("\n  Resources:", style="bold")
                    for resource in resources:
                        self.console.print(f"    - {resource}")
            else:
                # It's a dict
                self.console.print("\nSolution:", style="bold")
                self.console.print(f"  Type: {solution.get('solution_type', 'N/A')}")
                self.console.print(f"  Estimated Time: {solution.get('estimated_resolution_time', 'N/A')}")
                self.console.print(f"  Confidence: {solution.get('confidence_score', 0):.2f}")
                
                steps = solution.get('steps', [])
                if steps:
                    self.console.print("\n  Steps:", style="bold")
                    for i, step in enumerate(steps, 1):
                        self.console.print(f"    {i}. {step}")
                
                resources = solution.get('resources', [])
                if resources:
                    self.console.print("\n  Resources:", style="bold")
                    for resource in resources:
                        self.console.print(f"    - {resource}")
        
        # Display conversation summary
        history = results.get("conversation_history", [])
        if history:
            self.console.print("\nConversation Summary:", style="bold")
            for message in history[-3:]:  # Show last 3 messages
                if hasattr(message, 'sender'):
                    sender = message.sender
                    content = message.content
                else:
                    sender = message.get('sender', 'Unknown')
                    content = message.get('content', '')
                
                content_preview = content[:100] + "..." if len(content) > 100 else content
                self.console.print(f"  {sender}: {content_preview}")
    
    async def run_interactive_mode(self):
        """Run the system in interactive mode"""
        session_id = await self.start_interactive_session()
        
        while True:
            try:
                # Get user input
                self.console.print("\nYour query: ", style="bold blue", end="")
                query = self.console.input().strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    self.console.print("Goodbye!", style="green")
                    break
                
                if query.lower() == 'help':
                    self._show_help()
                    continue
                
                if query.lower() == 'history':
                    await self._show_session_history(session_id)
                    continue
                
                if not query:
                    self.console.print("Please enter a query or 'help' for commands", style="yellow")
                    continue
                
                # Process the query
                self.console.print("Processing your query...", style="dim")
                results = await self.handle_customer_query(session_id, query)
                
                # Display results
                self.display_results(results)
                
            except KeyboardInterrupt:
                self.console.print("\nGoodbye!", style="green")
                break
            except Exception as e:
                try:
                    self.console.print(f"Unexpected error: {str(e)}", style="red")
                except:
                    print(f"Unexpected error: {str(e)}")
    
    def _show_help(self):
        """Show help information"""
        help_text = """
Available Commands:
- help - Show this help message
- history - Show session history
- quit or exit - End the session

Example Queries:
- "I can't log into my account"
- "I was charged twice for my subscription"
- "How do I integrate your API with my system?"
- "My data export is failing"
        """
        
        self.console.print(help_text)
    
    async def _show_session_history(self, session_id: str):
        """Show session history"""
        try:
            summary = await self.memory_store.get_session_summary(session_id)
            
            if not summary:
                self.console.print("[yellow]No session history found[/yellow]")
                return
            
            self.console.print(f"[bold]Session Summary:[/bold]")
            self.console.print(f"  Created: {summary.get('created_at', 'N/A')}")
            self.console.print(f"  Last Updated: {summary.get('last_updated', 'N/A')}")
            self.console.print(f"  Total Messages: {summary.get('total_messages', 0)}")
            
            agent_stats = summary.get('agent_stats', {})
            if agent_stats:
                self.console.print("\n  [bold]Agent Activity:[/bold]")
                for agent, stats in agent_stats.items():
                    self.console.print(f"    {agent}: {stats.get('message_count', 0)} messages")
            
        except Exception as e:
            self.console.print(f"[red]Error retrieving history: {str(e)}[/red]")
    
    async def cleanup(self):
        """Cleanup system resources"""
        await self.web_search.close()
        await self.memory_store.close()


async def main():
    """Main entry point"""
    system = CustomerServiceSystem()
    
    try:
        await system.run_interactive_mode()
    finally:
        await system.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
