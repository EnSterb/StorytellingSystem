from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # App
    DEBUG: bool = False
    DOCS_ENABLED: bool = True
    APP_TITLE: str = "Story Service"
    APP_VERSION: str = "0.1.0"

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Mail
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_TLS: bool = True

    FRONTEND_URL: str
    API_GATEWAY: str
    STORY_SERVICE_URL: str
    RAG_SERVICE_URL: str
    LLM_SERVICE_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
