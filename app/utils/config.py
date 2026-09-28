from functools import lru_cache
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Zoey-Commerce AI"
    app_version: str = "0.1.0"
    environment: str = "development"

    openai_api_key: SecretStr = SecretStr("")

    langsmith_api_key: str = ""
    langchain_tracing_v2: bool = True
    langchain_project: str = "ZoeyCommerceAI"

    meta_verify_token: str = "ZoeyBambini_Secure_Token_2026_!"
    meta_access_token: str = ""
    meta_phone_number_id: str = ""

    redis_url: str = "redis://localhost:6379/0"

    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str =  "redis://localhost:6379/2"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()



settings = get_settings()
