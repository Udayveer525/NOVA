# agents/supervisor/agent.py

from langchain_core.tools import tool
from core.base_agent import BaseAgent
from agents.supervisor.prompts import get_supervisor_prompt


class SupervisorAgent(BaseAgent):
    """Supervisor that routes to specialized agents."""
    
    def __init__(self, coordinator):
        self.user_name = "Udayveer"
        self.coordinator = coordinator  # Store coordinator reference
        super().__init__(coordinator, "Supervisor")
    
    def get_tools(self):
        """Supervisor's tools: routing and basic web search."""
        
        # Create closure-based tools that capture self
        coordinator = self.coordinator
        
        @tool
        def route_to_agent(agent: str, task: str) -> str:
            """Route task to specialized agent.
            
            Args:
                agent: 'dev', 'system', or 'research'
                task: Description of what to do
            """
            print(f"🔀 Routing to {agent} agent...")
            
            result = coordinator.send_message(
                from_agent='supervisor',
                to_agent=agent,
                content=task
            )
            
            return f"✅ {agent.title()} Agent completed:\n{result}"
        
        @tool
        def web_search_simple(query: str) -> str:
            """Quick web search for casual questions."""
            # Route to research agent for actual search
            result = coordinator.send_message(
                from_agent='supervisor',
                to_agent='research',
                content=f"Quick search: {query}"
            )
            return result
        
        return [
            route_to_agent,
            web_search_simple,
        ]
    
    def get_prompt_template(self):
        """Get supervisor's prompt."""
        return get_supervisor_prompt(self.user_name)
