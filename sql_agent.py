from textwrap import dedent
from typing import Optional
import os

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.sql import SQLTools
from agno.storage.sqlite import SqliteStorage
from sqlalchemy import create_engine

from db.session import db_url

# Get database path from environment variable or use default
db_path = os.environ.get("CHINOOK_DB_PATH", "./data/chinook.db")
engine = create_engine(f'sqlite:///{db_path}')

def get_sql_agent(
    model_id: str = "gpt-4o",
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = True,
) -> Agent:
    additional_context = ""
    if user_id:
        additional_context += "<context>"
        additional_context += f"You are interacting with the user: {user_id}"
        additional_context += "</context>"
    
    return Agent(
        name="SQL Agent",
        agent_id="sql_agent",
        user_id=user_id,
        session_id=session_id,
        model=OpenAIChat(id=model_id),
        # Tools available to the agent
        tools=[SQLTools(db_engine=engine)],
        # Storage for the agent - using SQLite instead of PostgreSQL
        storage=SqliteStorage(table_name="sql_agent_sessions", db_file="agent.db"),
        # Description of the agent
        description=dedent("""\
            You are a SQL Agent, specialized in querying and analyzing the Chinook database.
            The Chinook database represents a digital media store, including tables for artists, albums, 
            media tracks, invoices, and customers. You can help users explore and analyze this data.
        """),
        # Instructions for the agent
        instructions=dedent("""\
            Respond to the user by following these steps:

            1. When asked about the database:
               - Use SQL tools to explore the database schema
               - List available tables and their structures when requested
               - Explain relationships between tables when relevant

            2. When asked to query data:
               - Write clean, efficient SQL queries
               - Format results in a readable way
               - Explain your query approach when appropriate
               - Use proper SQL best practices

            3. When analyzing data:
               - Provide insights based on the query results
               - Suggest follow-up queries that might be interesting
               - Explain patterns or anomalies in the data

            4. Maintain context:
               - Remember previous queries in the conversation
               - Build upon previous results when appropriate
               - Reference previous findings when relevant

            5. Handle errors gracefully:
               - If a query fails, explain why and suggest corrections
               - Provide guidance on proper SQL syntax when needed
        """),
        additional_context=additional_context,
        # Format responses using markdown
        markdown=True,
        # Add the current time to the instructions
        add_datetime_to_instructions=True,
        # Send the last 3 messages from the chat history
        add_history_to_messages=True,
        num_history_responses=3,
        # Add a tool to read the chat history if needed
        read_chat_history=True,
        # Show debug logs
        debug_mode=debug_mode,
        show_tool_calls=True,
    ) 


sql_agent=get_sql_agent()
sql_agent.print_response("list all the tables in the database")
