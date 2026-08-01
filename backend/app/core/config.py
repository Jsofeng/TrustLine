from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


"""
BaseSettings -> Instead of manually using os.getenv() automatically reads, parses, and validates matching environment variables or entries from a .env file at runtime

Takes .env URL's & gets converted into 

settings.database_url
settings.redis_url
"""

class Settings(BaseSettings): 
    model_config = SettingsConfigDict(env_file=".env", extra="ignore") #ignore extra variables

    #environment variables are case-insensitive by default.
    database_url: str
    migration_database_url: str 
    test_database_url: str 
    redis_url: str

@lru_cache # Helper for Settings() a cache for retrieving settings so doesn't have to be recalled hundreds of times
def get_settings() -> Settings:
    return Settings()



