"""
LLM client dispatcher — selects the right provider from config or per-request override.
"""
from functools import lru_cache

from fastapi import HTTPException

from backend.config import settings
from backend.models.analysis import TheoryAnalysis
from backend.models.response import EnrichedOutput
from backend.llm.providers import LLMProvider, AnthropicProvider, OpenAICompatibleProvider


@lru_cache(maxsize=8)
def _get_provider(name: str) -> LLMProvider:
    """
    Instantiate and cache a provider by name.
    lru_cache keeps SDK client objects alive across requests — same as the
    old module-level singleton, but now per-provider.
    """
    if name == "anthropic":
        if not settings.anthropic_api_key:
            raise HTTPException(status_code=503, detail="ANTHROPIC_API_KEY is not configured")
        return AnthropicProvider(
            api_key=settings.anthropic_api_key.get_secret_value(),
            model=settings.anthropic_model,
        )

    if name == "ollama":
        return OpenAICompatibleProvider(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            api_key="ollama",
        )

    if name == "openai":
        if not settings.openai_api_key:
            raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured")
        return OpenAICompatibleProvider(
            model=settings.openai_model,
            base_url=settings.openai_base_url,
            api_key=settings.openai_api_key.get_secret_value(),
        )

    raise HTTPException(
        status_code=400,
        detail=f"Unknown provider '{name}'. Supported: anthropic, ollama, openai.",
    )


def generate_explanation(
    analysis: TheoryAnalysis,
    input_tab: str,
    provider: str | None = None,
) -> EnrichedOutput:
    """
    Public API. Pass provider=None to use the server default from config
    (DEFAULT_PROVIDER env var, defaults to 'anthropic').
    """
    name = provider or settings.default_provider
    return _get_provider(name).generate(analysis, input_tab)
