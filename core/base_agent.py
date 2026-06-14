"""Base Agent — foundation for all specialized agents."""

from abc import ABC, abstractmethod

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

from core.config import MAX_AGENT_ITERATIONS, MEMORY_CONTEXT_LIMIT


class BaseAgent(ABC):
    """Base class that all agents inherit from."""

    def __init__(self, coordinator, agent_name: str):
        self.coordinator = coordinator
        self.agent_name = agent_name
        self.memory = coordinator.memory
        self.api_manager = coordinator.api_manager
        self.temperature = self.get_temperature()
        self.tools = self.get_tools()
        self.prompt_template = self._create_prompt()

    @abstractmethod
    def get_tools(self):
        """Return list of tools for this agent."""
        pass

    @abstractmethod
    def get_prompt_template(self) -> str:
        """Return prompt template for this agent."""
        pass

    def get_temperature(self) -> float:
        """Return temperature setting (override if needed)."""
        return 0.7

    def _create_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", self.get_prompt_template()),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])

    def execute(self, task: str, context: str = "") -> str:
        """Execute a task with automatic key rotation on quota errors."""
        max_retries = len(self.api_manager.api_keys)
        last_error = None

        for attempt in range(max_retries):
            self.api_manager.begin_request_cycle()
            try:
                llm = self.api_manager.get_llm(temperature=self.temperature)

                agent = create_tool_calling_agent(
                    llm=llm,
                    tools=self.tools,
                    prompt=self.prompt_template,
                )

                executor = AgentExecutor(
                    agent=agent,
                    tools=self.tools,
                    verbose=True,
                    handle_parsing_errors=True,
                    max_iterations=MAX_AGENT_ITERATIONS,
                )

                recent_memory = "\n".join(
                    self.memory.get_recent_conversation(limit=MEMORY_CONTEXT_LIMIT)
                )

                result = executor.invoke({
                    "input": task,
                    "memory": recent_memory,
                    "context": context,
                })

                return result["output"]

            except Exception as e:
                error_str = str(e)
                last_error = error_str

                if self._is_quota_error(error_str):
                    print(
                        f"⚠️ Key exhausted, trying next key... "
                        f"(attempt {attempt + 1}/{max_retries})"
                    )
                    self.api_manager.mark_current_key_exhausted()
                    continue

                return f"❌ {self.agent_name} error: {error_str}"

            finally:
                self.api_manager.end_request_cycle()

        return (
            f"❌ All {len(self.api_manager.api_keys)} API keys exhausted. "
            f"Last error: {last_error}"
        )

    @staticmethod
    def _is_quota_error(error_str: str) -> bool:
        lower = error_str.lower()
        return "429" in error_str or "quota" in lower or "rate limit" in lower
