from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Anthropic Claude
    anthropic_api_key: SecretStr | None = None

    # OpenAI / OpenRouter / any OpenAI-compatible endpoint
    openai_api_key: SecretStr | None = None
    openai_base_url: str = "https://api.openai.com/v1"

    # Ollama (local, no key required)
    ollama_base_url: str = "http://localhost:11434/v1"

    # Defaults — all overridable via .env
    default_provider: str = "anthropic"
    anthropic_model: str = "claude-sonnet-4-6"
    openai_model: str = "gpt-4o-mini"
    ollama_model: str = "llama3"


settings = Settings()
