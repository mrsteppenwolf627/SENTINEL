from pydantic_settings import BaseSettings
from enum import Enum

class Environment(str, Enum):
    LOCAL = "LOCAL"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"

class Settings(BaseSettings):
    APP_NAME: str = "Sentinel"
    ENVIRONMENT: Environment = Environment.LOCAL
    LOG_LEVEL: str = "INFO"
    
    # Audit
    AUDIT_FILE_PATH: str = "audit.log"
    DB_PATH: str = "sentinel.db"
    
    # Policy Defaults
    AUTO_APPROVE_SAFE_ACTIONS: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
