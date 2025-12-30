"""Base Agent - Foundation for all specialized agents."""

from abc import ABC, abstractmethod
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate


class BaseAgent(ABC):
    """Base class that all agents inherit from."""
    
    def __init__(self, coordinator, agent_name):
        self.coordinator = coordinator
        self.agent_name = agent_name
        self.memory = coordinator.memory
        self.api_manager = coordinator.api_manager
        
        # DON'T create LLM here - create per request instead
        self.temperature = self.get_temperature()
        
        # Tools are defined by child classes
        self.tools = self.get_tools()
        
        # Create prompt template
        self.prompt_template = self._create_prompt()
    
    @abstractmethod
    def get_tools(self):
        """Return list of tools for this agent."""
        pass
    
    @abstractmethod
    def get_prompt_template(self):
        """Return prompt template for this agent."""
        pass
    
    def get_temperature(self):
        """Return temperature setting (override if needed)."""
        return 0.7
    
    def _create_prompt(self):
        """Create ChatPromptTemplate with agent's specific prompt."""
        return ChatPromptTemplate.from_messages([
            ("system", self.get_prompt_template()),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
    
    def execute(self, task: str, context: str = "") -> str:
        """Execute a task with optional context."""
        
        max_retries = len(self.api_manager.api_keys)  # Try all available keys
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Create fresh LLM with next available key
                llm = self.api_manager.get_llm(temperature=self.temperature)
                
                # Create agent with new LLM
                agent = create_tool_calling_agent(
                    llm=llm,
                    tools=self.tools,
                    prompt=self.prompt_template
                )
                
                executor = AgentExecutor(
                    agent=agent,
                    tools=self.tools,
                    verbose=True,
                    handle_parsing_errors=True,
                    max_iterations=15
                )
                
                # Get recent memory for context
                recent_memory = "\n".join(self.memory.get_recent_conversation(limit=20))
                
                result = executor.invoke({
                    "input": task,
                    "memory": recent_memory,
                    "context": context
                })
                
                return result["output"]
                
            except Exception as e:
                error_str = str(e)
                last_error = error_str
                
                # Check if it's a quota/rate limit error
                if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                    print(f"⚠️ Key exhausted, trying next key... (attempt {attempt + 1}/{max_retries})")
                    
                    # Mark current key as exhausted
                    if self.api_manager.current_key_index < len(self.api_manager.api_keys):
                        current_key = self.api_manager.api_keys[self.api_manager.current_key_index]
                        current_key['requests_today'] = self.api_manager.RPD_LIMIT  # Mark as full
                        print(f"❌ {current_key['name']} exhausted, rotating to next key")
                    
                    # Try next key
                    continue
                else:
                    # Non-quota error, don't retry
                    return f"❌ {self.agent_name} error: {str(e)}"
        
        # All keys exhausted
        return f"❌ All {len(self.api_manager.api_keys)} API keys exhausted. Error: {last_error}"
    
    def ask_agent(self, target_agent: str, query: str) -> str:
        """Request help from another agent (inter-agent communication)."""
        print(f"📨 {self.agent_name} → {target_agent}: {query}")
        return self.coordinator.send_message(
            from_agent=self.agent_name,
            to_agent=target_agent,
            content=query
        )
