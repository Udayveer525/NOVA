"""Shared Gemini grounding utilities for research tools."""

from google.genai import types

from core.config import GEMINI_MODEL


def _extract_sources(response, limit: int = 3) -> str:
    """Extract grounding source URLs from a Gemini response."""
    metadata = getattr(response, "grounding_metadata", None)
    if not metadata:
        return ""

    chunks = getattr(metadata, "grounding_chunks", None) or []
    sources = []
    for chunk in chunks[:limit]:
        web = getattr(chunk, "web", None)
        if web and getattr(web, "uri", None):
            sources.append(f"• {web.uri}")

    if sources:
        return "\n\n📚 Sources:\n" + "\n".join(sources)
    return ""


def web_search(client, query: str) -> str:
    """Search the web using Gemini Google Search grounding."""
    grounding_tool = types.Tool(google_search=types.GoogleSearch())

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=f"Search for and provide detailed, accurate information about: {query}",
        config=types.GenerateContentConfig(tools=[grounding_tool]),
    )

    return response.text + _extract_sources(response)


def read_documentation(client, url: str) -> str:
    """Read and summarize documentation from a URL."""
    url_tool = types.Tool(url_context=types.UrlContext())

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=f"""Read and summarize the key information from: {url}

Provide:
1. Main topics covered
2. Key concepts/APIs
3. Important examples
4. Best practices mentioned""",
        config=types.GenerateContentConfig(tools=[url_tool], max_output_tokens=1000),
    )

    return f"📚 Documentation from {url}:\n\n{response.text}"


def search_and_read_docs(client, topic: str) -> str:
    """Search for documentation and read the most relevant result."""
    search_tool = types.Tool(google_search=types.GoogleSearch())
    url_tool = types.Tool(url_context=types.UrlContext())

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=(
            f"Find the official documentation for '{topic}' and read the most "
            f"relevant page. Provide a comprehensive summary with key information, "
            f"examples, and usage details."
        ),
        config=types.GenerateContentConfig(
            tools=[search_tool, url_tool],
            max_output_tokens=1200,
        ),
    )

    return response.text + _extract_sources(response)
