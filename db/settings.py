from os import getenv
from typing import Optional

from pydantic_settings import BaseSettings


class DbSettings(BaseSettings):
    """Database settings that can be set using environment variables.

    Reference: https://docs.pydantic.dev/latest/usage/pydantic_settings/
    """

    # Database configuration
    db_host: str = getenv("DB_HOST", "db")
    db_port: int = int(getenv("DB_PORT", "5432"))
    db_user: str = getenv("DB_USER", "admin_user")
    db_pass: str = getenv("DB_PASS", "admin_password")
    db_database: str = getenv("DB_DATABASE", "stratum")
    db_driver: str = "postgresql+psycopg"
    # Create/Upgrade database on startup using alembic
    migrate_db: bool = getenv("MIGRATE_DB", "False").lower() in ("true", "t", "1", "yes", "y")

    def get_db_url(self) -> str:
        # Always use explicit environment variables rather than None values
        db_url = "{}://{}{}@{}:{}/{}".format(
            self.db_driver,
            self.db_user,
            f":{self.db_pass}" if self.db_pass else "",
            self.db_host,
            self.db_port,
            self.db_database,
        )
        
        print(f"Using database URL: {db_url}")
        return db_url


# Create DbSettings object
db_settings = DbSettings()
