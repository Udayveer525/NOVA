from langchain_core.tools import tool
from google import genai
from google.genai import types


def create_research_tools(api_manager):
    """Factory function to create research tools with API manager access."""
    
    @tool
    def web_search(query: str) -> str:
        """Search the web for current information.
        
        Use for: news, prices, current events, recent updates
        """
        try:
            print(f"🔍 Searching web for: {query}")
            
            # Get rotated key from API manager
            key_info = api_manager._get_available_key()
            if not key_info:
                return "❌ All API keys exhausted. Please try tomorrow."
            
            client = genai.Client(api_key=key_info['key'])
            grounding_tool = types.Tool(google_search=types.GoogleSearch())
            
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=f"Search for and provide detailed information about: {query}",
                config=types.GenerateContentConfig(tools=[grounding_tool])
            )
            
            result = response.text
            
            # Extract sources if available
            if hasattr(response, 'grounding_metadata') and response.grounding_metadata:
                sources = []
                if hasattr(response.grounding_metadata, 'grounding_chunks'):
                    for chunk in response.grounding_metadata.grounding_chunks[:3]:
                        if hasattr(chunk, 'web') and chunk.web:
                            sources.append(f"• {chunk.web.uri}")
                
                if sources:
                    result += f"\n\n📚 Sources:\n" + "\n".join(sources)
            
            return result
            
        except Exception as e:
            return f"❌ Web search error: {str(e)}"
    
    
    @tool
    def read_documentation(url: str) -> str:
        """Read documentation from a specific URL.
        
        Use when you have exact documentation URL.
        """
        try:
            print(f"📖 Reading documentation from: {url}")
            
            # Get rotated key from API manager
            key_info = api_manager._get_available_key()
            if not key_info:
                return "❌ All API keys exhausted. Please try tomorrow."
            
            client = genai.Client(api_key=key_info['key'])
            url_tool = types.Tool(url_context=types.UrlContext())
            
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=f"""Read and summarize the key information from: {url}

Provide:
1. Main topics covered
2. Key concepts/APIs
3. Important examples
4. Best practices mentioned""",
                config=types.GenerateContentConfig(tools=[url_tool], max_output_tokens=1000)
            )
            
            return f"📚 Documentation from {url}:\n\n{response.text}"
            
        except Exception as e:
            return f"❌ Failed to read documentation: {str(e)}"
    
    
    @tool
    def search_and_read_docs(topic: str) -> str:
        """Search for documentation and read the most relevant result.
        
        Use for: learning new topics, finding framework docs
        Example: 'React hooks', 'FastAPI tutorial'
        """
        try:
            print(f"🔍📖 Finding and reading docs for: {topic}")
            
            # Get rotated key from API manager
            key_info = api_manager._get_available_key()
            if not key_info:
                return "❌ All API keys exhausted. Please try tomorrow."
            
            client = genai.Client(api_key=key_info['key'])
            
            # Use both search and URL tools
            search_tool = types.Tool(google_search=types.GoogleSearch())
            url_tool = types.Tool(url_context=types.UrlContext())
            
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=f"Find the official documentation for '{topic}' and read the most relevant page. Provide a comprehensive summary with key information, examples, and usage details.",
                config=types.GenerateContentConfig(
                    tools=[search_tool, url_tool],
                    max_output_tokens=1200
                )
            )
            
            return response.text
            
        except Exception as e:
            return f"❌ Documentation search error: {str(e)}"
    
    return [web_search, read_documentation, search_and_read_docs]