from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools
from agno.tools.yfinance import YFinanceTools

thinking_agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[
        ReasoningTools(add_instructions=True),
        YFinanceTools(
            stock_price=True,
            analyst_recommendations=True,
            company_info=True,
            company_news=True,
        ),
    ],
    instructions="Use tables where possible",
    show_tool_calls=True,
    markdown=True,
)

thinking_agent.print_response("Write a report comparing NVDA to TSLA", stream=True)