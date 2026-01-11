"""
Demo script showing how to use the multi-agent system
"""
import asyncio
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.main import CustomerServiceSystem


async def demo_queries():
    """Demonstrate different types of customer queries"""
    
    # Initialize the system
    system = CustomerServiceSystem()
    
    # Start a session
    session_id = await system.start_interactive_session()
    
    # Demo queries covering different scenarios
    demo_queries = [
        {
            "type": "Technical Issue",
            "query": "I keep getting error code 500 when trying to access the dashboard",
            "description": "Technical problem requiring analysis"
        },
        {
            "type": "Billing Issue", 
            "query": "I was charged twice for my monthly subscription",
            "description": "Billing problem needing investigation"
        },
        {
            "type": "Account Issue",
            "query": "I forgot my password and can't reset it",
            "description": "Account access problem"
        },
        {
            "type": "Complex Integration",
            "query": "How do I integrate your API with our enterprise system for real-time data sync?",
            "description": "Complex technical integration requiring expert help"
        },
        {
            "type": "Security Concern",
            "query": "I think someone accessed my account without permission",
            "description": "Security issue requiring immediate attention"
        }
    ]
    
    print("Multi-Agent Customer Service System Demo")
    print("=" * 50)
    
    for i, demo in enumerate(demo_queries, 1):
        print(f"\nDemo {i}: {demo['type']}")
        print(f"Description: {demo['description']}")
        print(f"Query: \"{demo['query']}\"")
        print("-" * 40)
        
        try:
            # Process the query
            results = await system.handle_customer_query(session_id, demo['query'])
            
            # Display key results
            if "error" not in results:
                agent_path = results.get("agent_path", [])
                analysis = results.get("analysis_result", {})
                solution = results.get("solution", {})
                
                print(f"Agent Path: {' -> '.join(agent_path)}")
                
                if analysis:
                    if hasattr(analysis, 'category'):
                        print(f"Category: {analysis.category}")
                        print(f"Severity: {analysis.severity}")
                        print(f"Confidence: {analysis.confidence_score:.2f}")
                    else:
                        print(f"Category: {analysis.get('category', 'N/A')}")
                        print(f"Severity: {analysis.get('severity', 'N/A')}")
                        print(f"Confidence: {analysis.get('confidence_score', 0):.2f}")
                
                if solution:
                    if hasattr(solution, 'solution_type'):
                        print(f"Solution Type: {solution.solution_type}")
                        print(f"Estimated Time: {solution.estimated_resolution_time}")
                        print(f"Confidence: {solution.confidence_score:.2f}")
                    else:
                        print(f"Solution Type: {solution.get('solution_type', 'N/A')}")
                        print(f"Estimated Time: {solution.get('estimated_resolution_time', 'N/A')}")
                        print(f"Confidence: {solution.get('confidence_score', 0):.2f}")
                
                print("Query processed successfully")
            else:
                print(f"Error: {results['error']}")
                
        except Exception as e:
            print(f"Unexpected error: {e}")
        
        print("=" * 50)
    
    # Show session summary
    print("\nSession Summary:")
    try:
        summary = await system.memory_store.get_session_summary(session_id)
        print(f"  Total Messages: {summary.get('total_messages', 0)}")
        
        agent_stats = summary.get('agent_stats', {})
        if agent_stats:
            print("  Agent Activity:")
            for agent, stats in agent_stats.items():
                print(f"    {agent}: {stats.get('message_count', 0)} messages")
    except Exception as e:
        print(f"  Error retrieving summary: {e}")
    
    # Cleanup
    await system.cleanup()
    print("\nDemo completed!")


async def interactive_demo():
    """Run an interactive demo with user input"""
    system = CustomerServiceSystem()
    
    print("Interactive Demo Mode")
    print("Type your queries or 'quit' to exit")
    print("-" * 30)
    
    session_id = await system.start_interactive_session()
    
    while True:
        try:
            query = input("\nYour query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query:
                continue
            
            print("Processing...")
            results = await system.handle_customer_query(session_id, query)
            
            if "error" not in results:
                system.display_results(results)
            else:
                print(f"Error: {results['error']}")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    await system.cleanup()
    print("Goodbye!")


def check_environment():
    """Check if environment is properly configured"""
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set up your .env file with the required variables")
        print("Copy .env.example to .env and add your API keys")
        return False
    
    print("Environment configured correctly")
    return True


async def main():
    """Main demo function"""
    print("Multi-Agent Customer Service System")
    print("Demo Script")
    print("=" * 40)
    
    # Check environment
    if not check_environment():
        return
    
    # Choose demo mode
    print("\nChoose demo mode:")
    print("1. Pre-defined queries demo")
    print("2. Interactive demo")
    print("3. Both")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            await demo_queries()
        elif choice == "2":
            await interactive_demo()
        elif choice == "3":
            await demo_queries()
            print("\n" + "=" * 50)
            await interactive_demo()
        else:
            print("Invalid choice. Running pre-defined queries demo...")
            await demo_queries()
            
    except KeyboardInterrupt:
        print("\nDemo cancelled")
    except Exception as e:
        print(f"Demo error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
