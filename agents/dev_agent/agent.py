"""Development Agent - Specialized in coding and project work."""

from langchain_core.tools import tool
from core.base_agent import BaseAgent
from agents.dev_agent.prompts import get_dev_prompt
from agents.dev_agent.tools import (
    file_operations,
    git_operations,
    project_status
)


class DevelopmentAgent(BaseAgent):
    """Development specialist with inter-agent communication."""
    
    def __init__(self, coordinator):
        super().__init__(coordinator, "Dev")
    
    def get_temperature(self):
        """Lower temperature for more consistent code generation."""
        return 0.5
    
    def get_tools(self):
        """Dev agent's tools."""
        coordinator = self.coordinator
        
        @tool
        def ask_research_agent(query: str) -> str:
            """Request documentation or research from Research Agent."""
            return coordinator.send_message('dev', 'research', query)
        
        @tool
        def ask_system_agent(action: str) -> str:
            """Request system operation from System Agent."""
            return coordinator.send_message('dev', 'system', action)
        
        return [
            file_operations,
            git_operations,
            project_status,
            ask_research_agent,
            ask_system_agent,
        ]
    
    def get_prompt_template(self):
        return get_dev_prompt()