import os
import asyncio # Kept for main, as Agno or other tools might still use async features
from dotenv import load_dotenv
from textwrap import dedent
from datetime import datetime
import requests # For synchronous HTTP requests

# --- Settings ---
load_dotenv()

class Settings:
    def __init__(self):
        self.TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
        self.NEWSAPI_API_KEY = os.getenv("NEWSAPI_API_KEY")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not self.TAVILY_API_KEY:
            print("Warning: TAVILY_API_KEY not found in environment variables.")
        if not self.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY not found in environment variables.")

def get_settings():
    return Settings()

settings = get_settings()

# --- Agno Imports ---
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.tavily import TavilyTools
from agno.tools import tool

# --- Tool Definition (Synchronous) ---
@tool(
    name="get_recent_news",  # Keep the name LLM expects from instructions
    show_result=True
)
def get_recent_news_tool( # Changed to a standard 'def' function
    q: str,
    language: str = 'en',
    pageSize: int = 5
) -> str:
    """
    Fetches recent news articles based on a query string using an external API.
    Use this tool specifically when a user asks for recent news, latest updates,
    or headlines on a particular topic.

    Args:
        q: The keyword or phrase to search for in news articles.
        language: The 2-letter ISO-639-1 code for the language of the news
                  (e.g., 'en' for English, 'es' for Spanish, 'fr' for French).
                  Defaults to 'en'.
        pageSize: The number of news articles to return. Defaults to 5. Max is 100.

    Returns:
        A string containing the formatted news headlines and URLs,
        or an error message if the news cannot be fetched.
    """
    print(f"[Debug] SYNC get_recent_news_tool called with: q='{q}', language='{language}', pageSize={pageSize}")
    if not settings.NEWSAPI_API_KEY:
        return "Error: NEWSAPI_API_KEY not configured for the news fetching tool. Please set it in your environment."

    # Synchronous API call using 'requests' library
    # You may need to install it: pip install requests
    try:
        api_url = "https://newsapi.org/v2/top-headlines"
        params = {
            "q": q,
            "language": language,
            "pageSize": pageSize,
            "apiKey": settings.NEWSAPI_API_KEY,
            "sortBy": "publishedAt"  # Get the latest articles
        }
        response = requests.get(api_url, params=params, timeout=10) # 10-second timeout
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        data = response.json()
        articles = data.get("articles", [])

        if not articles:
            return f"No recent news found for '{q}' (language: {language})."

        formatted_news = []
        for article in articles:
            title = article.get('title', 'N/A')
            url = article.get('url', 'N/A')
            source_name = article.get('source', {}).get('name', 'N/A') # Safely get source name
            formatted_news.append(f"- {title} (Source: {source_name}): {url}")
        
        return f"Recent news for '{q}' ({language}):\n" + "\n".join(formatted_news)
    except requests.exceptions.HTTPError as e:
        error_details = e.response.text
        try: # Try to parse JSON error from NewsAPI for better message
            error_json = e.response.json()
            if 'message' in error_json:
                error_details = error_json['message']
        except ValueError: # Not a JSON response
            pass
        return f"Error fetching news (HTTP {e.response.status_code}): {error_details}"
    except requests.exceptions.RequestException as e:
        # For other network issues like timeouts, connection errors
        return f"Error fetching news (Network issue): {str(e)}"
    except Exception as e:
        # Catch-all for any other unexpected errors
        return f"An unexpected error occurred in get_recent_news_tool: {str(e)}"

# --- Agent Setup ---
current_date_str = datetime.now().strftime("%Y-%m-%d")

media_monitoring_agno_agent = Agent(
    model=OpenAIChat(
        id="gpt-4o",
        api_key=settings.OPENAI_API_KEY
    ),
    tools=[
        TavilyTools(api_key=settings.TAVILY_API_KEY),
        get_recent_news_tool, # Pass the synchronous tool function
    ],
    description=dedent("""\
        You are the Sequencr Media Monitoring Assistant. You help users track news,
        social media trends, and online content related to their interests or industry.
    """),
    instructions=dedent(f"""\
        Today's date is {current_date_str}.
        You have access to the following tools:
        1. `tavily_search`: Use this for general web searches, finding specific information,
           researching topics, or answering broad questions when news headlines are not
           specifically requested. Example: "What is the impact of AI on journalism?".
        2. `get_recent_news`: Use this tool specifically when the user asks for recent news,
           latest updates, or headlines on a particular topic.
           Example: "Find recent news about renewable energy." or "Latest headlines on AI?".

        Analyze the user's query carefully and choose the most appropriate tool.
        If "recent news", "latest articles", "headlines" are mentioned, prefer `get_recent_news`.
        Otherwise, for general information, use `tavily_search`.
        Cite sources when using `tavily_search`.
        For `get_recent_news`, pass the user's query (q), and optionally language and pageSize.
    """),
    show_tool_calls=True,
    markdown=True,
)

# --- Main Execution ---
if __name__ == "__main__":
    # main can remain async if agno.print_response itself is awaitable or
    # if other async operations are planned within main.
    # If print_response is purely synchronous, main could become synchronous too.
    async def main():
        if not settings.OPENAI_API_KEY:
            print("Error: OPENAI_API_KEY is not set. Please set it in your environment.")
            return
        if not settings.TAVILY_API_KEY:
             print("Warning: TAVILY_API_KEY is not set. Tavily search may fail or require environment variable.")
        if not settings.NEWSAPI_API_KEY: # Good to have a startup warning too
            print("Warning: NEWS_API_KEY is not set. The 'get_recent_news' tool will return an error message if called.")

        # Test queries from previous attempts
        #test_queries = [
        #    ("What are the latest headlines on quantum computing?", "Asking for recent news"),
        #    ("Explain the current state of fusion energy research.", "Asking for general information (should use Tavily)"),
        #    ("Get me the 3 latest news articles about electric vehicles in German.", "Recent news with parameters implied"),
        #    ("Tell me about recent developments in AI.", "A more ambiguous query to test tool selection"),
        #    ("give me an media monitoring report for Netflix", "User's specific failing query") # The one that showed the coroutine error
        #]

        #for query, description in test_queries:
        #    print(f"\n\n--- Query Test: {description} ---")
        #    print(f"User Prompt: {query}")
        #    media_monitoring_agno_agent.print_response(
        #        query,
        #        stream=True # Streaming should still function
        #    )
        #    # Optional: await asyncio.sleep(1) # If making many calls rapidly to external APIs

        print("--- Query 1: Asking for recent news ---")
        # Use print_response instead of print_response_async
        media_monitoring_agno_agent.print_response(
            "give me an media monitoring report for Trump",
            stream=True
        )

    asyncio.run(main())