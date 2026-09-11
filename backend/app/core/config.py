from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "AI Document Intelligence API"
    APP_VERSION: str = "1.0.0"
    DATABASE_URL: str = "sqlite:///./documents.db"

    MAX_FILE_SIZE_MB: int = 10
    MAX_PAGES: int = 3
    OCR_ENABLED: bool = True

    # Anthropic
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"

    # Google Gemini
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.6-flash"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()