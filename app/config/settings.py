from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_provider: str
    model_name: str
    temperature: float
    ollama_base_url: str

    embedding_model: str

    # openai_api_key: str | None = None
    # anthropic_api_key: str | None = None
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )



settings = Settings()