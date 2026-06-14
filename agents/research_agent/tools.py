"""Research Agent tools — web search and documentation reading."""

from langchain_core.tools import tool

from core import gemini_tools


def create_research_tools(api_manager):
    """Create research tools bound to the shared API manager."""

    @tool
    def web_search(query: str) -> str:
        """Search the web for current information.

        Use for: news, prices, current events, recent updates, weather, facts.
        """
        try:
            print(f"🔍 Searching web for: {query}")
            client = api_manager.get_genai_client()
            return gemini_tools.web_search(client, query)
        except Exception as e:
            return f"❌ Web search error: {e}"

    @tool
    def read_documentation(url: str) -> str:
        """Read documentation from a specific URL.

        Use when you have an exact documentation URL.
        """
        try:
            print(f"📖 Reading documentation from: {url}")
            client = api_manager.get_genai_client()
            return gemini_tools.read_documentation(client, url)
        except Exception as e:
            return f"❌ Failed to read documentation: {e}"

    @tool
    def search_and_read_docs(topic: str) -> str:
        """Search for documentation and read the most relevant result.

        Use for: learning new topics, finding framework docs.
        Example: 'React hooks', 'FastAPI tutorial'
        """
        try:
            print(f"🔍📖 Finding and reading docs for: {topic}")
            client = api_manager.get_genai_client()
            return gemini_tools.search_and_read_docs(client, topic)
        except Exception as e:
            return f"❌ Documentation search error: {e}"

    return [web_search, read_documentation, search_and_read_docs]
