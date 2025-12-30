"""Nova Multi-Agent System - Main Entry Point."""

import os
from dotenv import load_dotenv
from core.coordinator import AgentCoordinator
from core.api_manager import APIManager


def main():
    """Initialize and run Nova."""
    
    # Load environment variables
    load_dotenv()

    
    # Initialize Nova
    print("\n" + "="*60)
    print("🌟 NOVA - Multi-Agent Personal AI Companion")
    print("="*60 + "\n")
    
    coordinator = AgentCoordinator()
    
    print("\n💬 Chat with Nova (type 'exit' to quit, 'stats' for usage)\n")
    
    # Chat loop
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\nNova: Take care, Udayveer! See you soon! 👋")
                break
            
            if user_input.lower() == 'stats':
                usage = APIManager()
                print(usage.get_usage_stats())
                print()
                continue
            
            # Get response from Nova
            response = coordinator.chat(user_input)
            
            print(f"\nNova: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\nNova: Interrupted! Bye! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")


if __name__ == "__main__":
    main()
