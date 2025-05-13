import os
import asyncio
from dotenv import load_dotenv
from textwrap import dedent
from datetime import datetime

# --- Start: Placeholder for your settings and utility function ---
load_dotenv()

class Settings:
    def __init__(self):
        self.TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
        self.NEWS_API_KEY = os.getenv("NEWS_API_KEY")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not self.TAVILY_API_KEY:
            print("Warning: TAVILY_API_KEY not found in environment variables.")
        if not self.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY not found in environment variables.")

def get_settings():
    return Settings()

settings = get_settings()
# --- End: Placeholder ---

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.tavily import TavilyTools
from agno.tools import tool

@tool(
    name="get_recent_news",
    show_result=True
)
async def get_recent_news_tool(
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
    if not settings.NEWS_API_KEY:
        return "Error: NEWS_API_KEY not configured for the news fetching tool."

    print(f"[Debug] get_recent_news_tool (placeholder) called with: q='{q}', language='{language}', pageSize={pageSize}")
    # Replace with your actual NewsAPI call logic. For example:
    # import httpx
    # try:
    #     async with httpx.AsyncClient() as client:
    #         api_url = "https://newsapi.org/v2/top-headlines"
    #         params = {
    #             "q": q,
    #             "language": language,
    #             "pageSize": pageSize,
    #             "apiKey": settings.NEWS_API_KEY,
    #             "sortBy": "publishedAt" # Often good for "latest"
    #         }
    #         response = await client.get(api_url, params=params)
    #         response.raise_for_status()
    #         data = response.json()
    #         articles = data.get("articles", [])
    #         if not articles:
    #             return f"No recent news found for '{q}' (language: {language})."
    #         formatted_news = "\n".join([
    #             f"- {article.get('title', 'N/A')}: {article.get('url', 'N/A')}"
    #             for article in articles
    #         ])
    #         return f"Recent news for '{q}' ({language}):\n{formatted_news}"
    # except httpx.HTTPStatusError as e:
    #     return f"Error fetching news (HTTP {e.response.status_code}): {e.response.text}"
    # except Exception as e:
    #     return f"An unexpected error occurred while fetching news: {str(e)}"
    return f"Formatted news results for '{q}' in '{language}' (pageSize: {pageSize}). (Placeholder response from get_recent_news_tool)"

current_date_str = datetime.now().strftime("%Y-%m-%d")

media_monitoring_agno_agent = Agent(
    model=OpenAIChat(
        id="gpt-4o",
        api_key=settings.OPENAI_API_KEY
    ),
    tools=[
        TavilyTools(api_key=settings.TAVILY_API_KEY),
        get_recent_news_tool,
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
           specifically requested. For example, if the user asks "What is the impact of AI on journalism?".
        2. `get_recent_news`: Use this tool specifically when the user asks for recent news,
           latest updates, or headlines on a particular topic.
           For example, if the user asks "Find recent news about renewable energy." or
           "What are the latest headlines on AI?".

        Analyze the user's query carefully and choose the most appropriate tool based on their need.
        If they want general information or a broad search, use `tavily_search`.
        If they explicitly ask for "recent news", "latest articles", "headlines", or similar phrases
        indicating a desire for current news, use `get_recent_news`.
        When using `tavily_search`, try to cite your sources.
        When using `get_recent_news`, ensure you pass the user's query (q), and optionally language and pageSize if specified or appropriate.
    """),
    show_tool_calls=True,
    markdown=True,
)

if __name__ == "__main__":
    async def main():
        if not settings.OPENAI_API_KEY:
            print("Error: OPENAI_API_KEY is not set. Please set it as an environment variable or in the Settings class.")
            return
        if not settings.TAVILY_API_KEY:
             print("Warning: TAVILY_API_KEY is not set. Tavily search may fail.")
        if not settings.NEWS_API_KEY:
            print("Warning: NEWS_API_KEY is not set. Recent news fetching will return an error message.")


        print("--- Query 1: Asking for recent news ---")
        # Use print_response instead of print_response_async
        media_monitoring_agno_agent.print_response(
            "give me an media monitoring report for Netflix",
            stream=True
        )
       # print("\n\n--- Query 2: Asking for general information (should use Tavily) ---")
       # media_monitoring_agno_agent.print_response(
       #     "Explain the current state of fusion energy research.",
       #     stream=True
       # )
       # print("\n\n--- Query 3: Recent news with parameters implied ---")
       # media_monitoring_agno_agent.print_response(
       #     "Get me the 3 latest news articles about electric vehicles in German.",
       #     stream=True
       # )
       # print("\n\n--- Query 4: A more ambiguous query to test tool selection ---")
       # media_monitoring_agno_agent.print_response(
       #     "Tell me about recent developments in AI.",
       #     stream=True
       # )

    asyncio.run(main())