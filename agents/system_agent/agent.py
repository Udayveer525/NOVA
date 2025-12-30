"""System Agent - Specialized in system operations and app management."""

from langchain_core.tools import tool
from core.base_agent import BaseAgent
from agents.system_agent.prompts import get_system_prompt
from agents.system_agent.tools import system_controller


class SystemAgent(BaseAgent):
    """System management specialist."""
    
    def __init__(self, coordinator):
        super().__init__(coordinator, "System")
    
    def get_tools(self):
        """System agent's tools."""
        coordinator = self.coordinator
        
        @tool
        def ask_research_agent(query: str) -> str:
            """Request information from Research Agent."""
            return coordinator.send_message('system', 'research', query)
        
        return [
            system_controller,
            ask_research_agent,
        ]
    
    def get_prompt_template(self):
        return get_system_prompt()