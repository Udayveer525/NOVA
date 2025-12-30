"""Agent Coordinator - Manages all agents and facilitates communication."""

import os
from datetime import datetime
from core.api_manager import APIManager
from core.memory_manager import MemoryManager


class AgentCoordinator:
    """Central hub that coordinates all agents."""
    
    def __init__(self):
        print("🚀 Initializing Nova Multi-Agent System...")
        
        # Shared resources
        self.api_manager = APIManager()
        self.memory = MemoryManager()
        
        # Agent registry
        self._agents = {}
        
        # Initialize agents (lazy loading)
        self._supervisor = None
        self._dev_agent = None
        self._system_agent = None
        self._research_agent = None
        
        print("✅ Nova Coordinator ready!")
    
    @property
    def supervisor(self):
        """Lazy load Supervisor."""
        if self._supervisor is None:
            from agents.supervisor.agent import SupervisorAgent
            self._supervisor = SupervisorAgent(self)
            self._agents['supervisor'] = self._supervisor
            print("✅ Supervisor loaded")
        return self._supervisor
    
    @property
    def dev_agent(self):
        """Lazy load Development Agent."""
        if self._dev_agent is None:
            from agents.dev_agent.agent import DevelopmentAgent
            self._dev_agent = DevelopmentAgent(self)
            self._agents['dev'] = self._dev_agent
            print("✅ Development Agent loaded")
        return self._dev_agent
    
    @property
    def system_agent(self):
        """Lazy load System Agent."""
        if self._system_agent is None:
            from agents.system_agent.agent import SystemAgent
            self._system_agent = SystemAgent(self)
            self._agents['system'] = self._system_agent
            print("✅ System Agent loaded")
        return self._system_agent
    
    @property
    def research_agent(self):
        """Lazy load Research Agent."""
        if self._research_agent is None:
            from agents.research_agent.agent import ResearchAgent
            self._research_agent = ResearchAgent(self)
            self._agents['research'] = self._research_agent
            print("✅ Research Agent loaded")
        return self._research_agent
    
    def get_agent(self, agent_name: str):
        """Get reference to any agent."""
        agent_map = {
            'supervisor': self.supervisor,
            'dev': self.dev_agent,
            'system': self.system_agent,
            'research': self.research_agent
        }
        return agent_map.get(agent_name)
    
    def send_message(self, from_agent: str, to_agent: str, content: str) -> str:
        """Enable inter-agent communication."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"📨 [{timestamp}] {from_agent} → {to_agent}")
        
        # Get target agent and execute
        target = self.get_agent(to_agent)
        if target:
            return target.execute(content)
        else:
            return f"❌ Agent '{to_agent}' not found"
    
    def chat(self, user_input: str) -> str:
        """Main entry point for user interaction."""
        # Save to shared memory
        self.memory.save_exchange("User", user_input)
        
        # Always start with supervisor
        response = self.supervisor.execute(user_input)
        
        # Save response
        self.memory.save_exchange("Nova", response)
        
        return response
