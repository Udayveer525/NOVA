# main.py
import os
from dotenv import load_dotenv
from core.agent import Nova

def main() -> None:
    load_dotenv()
    nova = Nova()
    print("🧠 Nova Agent is online! (with web search capability)")
    
    print("Type 'exit' or Ctrl-C to shut down.")

    try:
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() == "exit":
                break
                
            response = nova.chat(user_input)
            print(f"Nova: {response}")
            
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        print("\n👋 Shutting down Nova. Goodbye!")

if __name__ == "__main__":
    main()
