from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False
    log_level: str = "INFO"

    github_app_id: str = ""
    github_private_key_path: str = "./certs/github_app.pem"
    github_webhook_secret: str = ""
    github_app_installation_id: str = ""

    database_url: str = "postgresql+asyncpg://pr_reviewer_user:changeme@localhost:5432/pr_reviewer"

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "llama3"

    weaviate_url: str = "http://localhost:8080"
    weaviate_api_key: str = ""

    bandit_enabled: bool = True
    semgrep_enabled: bool = True
    eslint_enabled: bool = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
