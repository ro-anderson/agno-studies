from typing import Iterator
from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from agno.utils.pprint import pprint_run_response

agent = Agent(model=OpenAIChat(id="gpt-4o-mini"))

# Run agent and return the response as a variable
agent.print_response("Tell me a 5 second short story about a robot")