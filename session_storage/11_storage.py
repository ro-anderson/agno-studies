from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.postgres import PostgresStorage
from rich.pretty import pprint

# PostgreSQL connection configuration
POSTGRES_USER = "admin_user"
POSTGRES_PASSWORD = "xQ0-Rv60FfHnYF-dtjFG"
POSTGRES_DB = "stratum"
POSTGRES_HOST = "18.205.233.238"

# Construct PostgreSQL connection URL
db_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"

agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    # Fix the session id to continue the same session across execution cycles
    session_id="fixed_id_for_demo",
    storage=PostgresStorage(
        table_name="agent_sessions",
        schema="ai",
        db_url=db_url,
        auto_upgrade_schema=True,
        mode="agent"
    ),
    add_history_to_messages=True,
    num_history_runs=3,
)
agent.print_response("What was my last question?")
agent.print_response("What is the capital of France?")
agent.print_response("What was my last question?")
pprint(agent.get_messages_for_session())