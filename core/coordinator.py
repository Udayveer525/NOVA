"""Agent Coordinator — manages all agents and facilitates communication."""

from datetime import datetime

from core.api_manager import APIManager
from core.memory_manager import MemoryManager


class AgentCoordinator:
    """Central hub that coordinates all agents."""

    def __init__(self):
        print("🚀 Initializing Nova Multi-Agent System...")

        self.api_manager = APIManager()
        self.memory = MemoryManager()

        self._agents: dict = {}
        self._agent_loaders = {
            "supervisor": self._load_supervisor,
            "dev": self._load_dev,
            "system": self._load_system,
            "research": self._load_research,
        }

        print("✅ Nova Coordinator ready!")

    def _load_supervisor(self):
        from agents.supervisor.agent import SupervisorAgent

        return SupervisorAgent(self)

    def _load_dev(self):
        from agents.dev_agent.agent import DevelopmentAgent

        return DevelopmentAgent(self)

    def _load_system(self):
        from agents.system_agent.agent import SystemAgent

        return SystemAgent(self)

    def _load_research(self):
        from agents.research_agent.agent import ResearchAgent

        return ResearchAgent(self)

    def get_agent(self, agent_name: str):
        """Get an agent by name, loading it lazily on first access."""
        if agent_name not in self._agent_loaders:
            return None

        if agent_name not in self._agents:
            agent = self._agent_loaders[agent_name]()
            self._agents[agent_name] = agent
            print(f"✅ {agent.agent_name} Agent loaded")

        return self._agents[agent_name]

    def send_message(self, from_agent: str, to_agent: str, content: str) -> str:
        """Enable inter-agent communication."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"📨 [{timestamp}] {from_agent} → {to_agent}")

        target = self.get_agent(to_agent)
        if not target:
            return f"❌ Agent '{to_agent}' not found"

        return target.execute(content)

    def chat(self, user_input: str) -> str:
        """Main entry point for user interaction."""
        self.memory.save_exchange("User", user_input)
        response = self.get_agent("supervisor").execute(user_input)
        self.memory.save_exchange("Nova", response)
        return response
