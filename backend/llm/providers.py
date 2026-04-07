"""
LLM provider implementations.

All providers share the same generate() interface.
SDK imports are deferred to __init__ so a missing package only fails
when that specific provider is instantiated, not at import time.
"""
import json
import re
from typing import Protocol, runtime_checkable

from fastapi import HTTPException

from backend.models.analysis import TheoryAnalysis
from backend.models.response import EnrichedOutput, PracticeExercise
from backend.llm.prompts import SYSTEM_PROMPT, build_user_prompt


# ── Shared helpers ────────────────────────────────────────────────────────────

def _parse_llm_json(raw_text: str) -> dict:
    text = raw_text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            return json.loads(m.group(0))
        raise HTTPException(status_code=502, detail="LLM returned non-JSON response")


def _build_enriched_output(data: dict, analysis: TheoryAnalysis, input_tab: str) -> EnrichedOutput:
    exercises = [
        PracticeExercise(number=ex["number"], description=ex["description"])
        for ex in data.get("practice_exercises", [])
    ]
    confidence_label = (
        "high" if analysis.key_confidence >= 0.8
        else "medium" if analysis.key_confidence >= 0.5
        else "low"
    )
    return EnrichedOutput(
        theory=analysis,
        beginner_summary=data.get("beginner_summary", ""),
        theory_deep_dive=data.get("theory_deep_dive", ""),
        scale_suggestions_narrative=data.get("scale_suggestions_narrative", ""),
        guide_tones_narrative=data.get("guide_tones_narrative", ""),
        practice_exercises=exercises,
        cheat_sheet=data.get("cheat_sheet", ""),
        input_tab=input_tab,
        confidence_label=confidence_label,
    )


# ── Protocol ──────────────────────────────────────────────────────────────────

@runtime_checkable
class LLMProvider(Protocol):
    def generate(self, analysis: TheoryAnalysis, input_tab: str) -> EnrichedOutput:
        ...


# ── Anthropic ─────────────────────────────────────────────────────────────────

class AnthropicProvider:
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6") -> None:
        import anthropic
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def generate(self, analysis: TheoryAnalysis, input_tab: str) -> EnrichedOutput:
        import anthropic
        try:
            message = self._client.messages.create(
                model=self._model,
                max_tokens=1500,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": build_user_prompt(analysis)}],
            )
        except anthropic.APIError as e:
            raise HTTPException(status_code=502, detail=f"LLM API error: {e}") from e

        text_block = next((b for b in message.content if b.type == "text"), None)
        if text_block is None:
            raise HTTPException(status_code=502, detail="LLM returned no text content")
        data = _parse_llm_json(text_block.text)
        return _build_enriched_output(data, analysis, input_tab)


# ── OpenAI-compatible (Ollama, OpenRouter, LM Studio, vLLM, OpenAI) ───────────

class OpenAICompatibleProvider:
    """
    Works with any OpenAI-compatible endpoint:
    - Ollama:     base_url=http://localhost:11434/v1  api_key="ollama"
    - OpenRouter: base_url=https://openrouter.ai/api/v1  api_key=<key>
    - LM Studio:  base_url=http://localhost:1234/v1  api_key="lm-studio"
    - OpenAI:     base_url=https://api.openai.com/v1  api_key=<key>
    """
    def __init__(self, model: str, base_url: str, api_key: str = "ollama") -> None:
        from openai import OpenAI
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model = model

    def generate(self, analysis: TheoryAnalysis, input_tab: str) -> EnrichedOutput:
        from openai import OpenAIError
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                max_tokens=1500,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": build_user_prompt(analysis)},
                ],
            )
        except OpenAIError as e:
            raise HTTPException(status_code=502, detail=f"LLM API error: {e}") from e

        data = _parse_llm_json(response.choices[0].message.content or "")
        return _build_enriched_output(data, analysis, input_tab)
