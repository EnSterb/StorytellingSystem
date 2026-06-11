from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_TITLE: str = "API Gateway"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    DOCS_ENABLED: bool = True

    # JWT (те же значения что в story-service)
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    # Upstream сервисы
    STORY_SERVICE_URL: str = "http://localhost:8001"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
