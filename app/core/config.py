from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from enum import Enum


class Environment(str, Enum):
    LOCAL = "LOCAL"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    APP_NAME: str = "Sentinel"
    ENVIRONMENT: Environment = Environment.LOCAL
    LOG_LEVEL: str = "INFO"

    # Audit
    AUDIT_FILE_PATH: str = "audit.log"
    DB_PATH: str = "sentinel.db"

    # Policy Defaults
    # Controls whether MODERATE-risk actions (e.g. RESTART_SERVICE, SCALE_UP)
    # are auto-executed without human approval. SAFE-risk actions are always auto-approved.
    AUTO_APPROVE_MODERATE_ACTIONS: bool = True

    # LLM Brain (Phase 2b)
    ANTHROPIC_API_KEY: str = ""
    LLM_MODEL: str = "claude-sonnet-4-6"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgrespassword@localhost:5432/sentinel"


settings = Settings()
