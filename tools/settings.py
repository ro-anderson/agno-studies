from os import environ
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # API configuration
    API_HOST: str = environ.get("API_HOST", "127.0.0.1")
    API_PORT: int = int(environ.get("API_PORT", "8100"))
    
    # LLM Configuration
    LLM_PROVIDER: str = environ.get("LLM_PROVIDER", "openai")  # "anthropic" or "openai"
    
    # Anthropic Configuration
    ANTHROPIC_API_KEY: str = environ.get("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")
    ANTHROPIC_TEMPERATURE: float = float(environ.get("ANTHROPIC_TEMPERATURE", "0"))
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = environ.get("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = environ.get("OPENAI_MODEL", "gpt-4-turbo-preview")
    OPENAI_TEMPERATURE: float = float(environ.get("OPENAI_TEMPERATURE", "0.7"))
    
    # Rate Limiter Configuration
    RATE_LIMITER_RPS: int = int(environ.get("RATE_LIMITER_RPS", "4"))
    RATE_LIMITER_CHECK_SECONDS: float = float(environ.get("RATE_LIMITER_CHECK_SECONDS", "0.1"))
    RATE_LIMITER_BUCKET_SIZE: int = int(environ.get("RATE_LIMITER_BUCKET_SIZE", "10"))
    
    # Search Configuration
    MAX_SEARCH_QUERIES: int = int(environ.get("MAX_SEARCH_QUERIES", "3"))
    MAX_SEARCH_RESULTS: int = int(environ.get("MAX_SEARCH_RESULTS", "3"))
    MAX_REFLECTION_STEPS: int = int(environ.get("MAX_REFLECTION_STEPS", "0"))
    INCLUDE_SEARCH_RESULTS: bool = environ.get("INCLUDE_SEARCH_RESULTS", "False").lower() == "true"

    #opik
    OTEL_EXPORTER_OTLP_ENDPOINT: str = environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:5173/api/v1/private/otel")
    OTEL_EXPORTER_OTLP_HEADERS: str = environ.get("OTEL_EXPORTER_OTLP_HEADERS", 'projectName=graph-tests')

def get_settings():
    return Config() 