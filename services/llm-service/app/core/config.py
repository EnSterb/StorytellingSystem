from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DEBUG: bool = False
    DOCS_ENABLED: bool = True
    APP_TITLE: str = "LLM Service"
    APP_VERSION: str = "0.1.0"

    # LLM backend
    LLM_BASE_URL: str
    LLM_API_KEY: str
    LLM_MODEL: str

    # Параметры генерации
    LLM_MAX_TOKENS: int = 1024
    LLM_TEMPERATURE: float = 0.7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
