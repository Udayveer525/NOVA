"""Nova Multi-Agent System — Main Entry Point."""

import sys

from dotenv import load_dotenv

from core.coordinator import AgentCoordinator


def main():
    load_dotenv()

    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    print("\n" + "=" * 60)
    print("🌟 NOVA - Multi-Agent Personal AI Companion")
    print("=" * 60 + "\n")

    try:
        coordinator = AgentCoordinator()
    except ValueError as e:
        print(f"\n❌ Configuration error: {e}")
        print("   Create a .env file with GOOGLE_API_KEY=your_key_here")
        sys.exit(1)

    print("\n💬 Chat with Nova (type 'exit' to quit, 'stats' for usage)\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit", "bye"):
                print("\nNova: Take care! See you soon! 👋")
                break

            if user_input.lower() == "stats":
                print(coordinator.api_manager.get_usage_stats())
                print()
                continue

            if user_input.lower() == "help":
                print(_help_text())
                print()
                continue

            response = coordinator.chat(user_input)
            print(f"\nNova: {response}\n")

        except KeyboardInterrupt:
            print("\n\nNova: Interrupted! Bye! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def _help_text() -> str:
    return """Available commands:
  exit / quit / bye  — End the session
  stats              — Show API key usage
  help               — Show this message

Nova routes your requests to specialized agents:
  • Dev Agent      — coding, files, git, terminal
  • System Agent   — open apps, system controls
  • Research Agent — web search, documentation"""


if __name__ == "__main__":
    main()
