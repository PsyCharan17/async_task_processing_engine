from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = {"env_file": ".env"}

settings = Settings()