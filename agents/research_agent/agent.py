"""Research Agent - Specialized in information gathering and documentation."""

from langchain_core.tools import tool
from core.base_agent import BaseAgent
from agents.research_agent.prompts import get_research_prompt
from agents.research_agent.tools import create_research_tools


class ResearchAgent(BaseAgent):
    """Research specialist with comprehensive information gathering."""
    
    def __init__(self, coordinator):
        super().__init__(coordinator, "Research")
    
    def get_tools(self):
        """Research agent's tools with API manager integration."""
        
        # Create research tools with API manager access
        research_tools = create_research_tools(self.api_manager)
        
        # Create inter-agent communication tools
        coordinator = self.coordinator
        
        @tool
        def ask_dev_agent(request: str) -> str:
            """Request code examples or development help from Dev Agent."""
            return coordinator.send_message('research', 'dev', request)
        
        @tool
        def ask_system_agent(action: str) -> str:
            """Request system operation from System Agent."""
            return coordinator.send_message('research', 'system', action)
        
        # Combine all tools
        return research_tools + [ask_dev_agent, ask_system_agent]
    
    def get_prompt_template(self):
        """Get research agent's prompt."""
        return get_research_prompt()
