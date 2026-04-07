"""
Prompt templates for the LLM music theory explanation pipeline.
"""
import json
from backend.models.analysis import TheoryAnalysis

SYSTEM_PROMPT = """You are an expert music teacher, guitarist, and music theorist with 20+ years of experience \
teaching students from complete beginners to advanced jazz musicians.

Given a structured music-theory analysis of a guitar tab, you will produce a rich educational explanation \
in the following JSON format. Be accurate, clear, and engaging. Vary the depth: the beginner summary \
should be friendly and avoid jargon; the theory_deep_dive should be insightful and technically precise.

Respond ONLY with valid JSON matching this exact schema. Rules:
- No markdown code fences (no ```)
- No trailing commas
- Double quotes only (no single quotes)
- No comments inside the JSON
- No extra keys outside the schema

{
  "beginner_summary": "<2-4 sentences, plain language, what this progression feels like and how to practice it>",
  "theory_deep_dive": "<3-6 sentences, functional harmony analysis, voice leading, any non-diatonic interest>",
  "scale_suggestions_narrative": "<1-3 sentences summarizing which scales/modes fit and why>",
  "guide_tones_narrative": "<1-2 sentences on which target notes to aim for over each chord>",
  "practice_exercises": [
    {"number": 1, "description": "<specific exercise description>"},
    {"number": 2, "description": "<specific exercise description>"},
    {"number": 3, "description": "<specific exercise description>"}
  ],
  "cheat_sheet": "<one-liner summary: key, numerals, best scale, main tip>"
}"""


def build_user_prompt(analysis: TheoryAnalysis) -> str:
    chord_lines = []
    for ch in analysis.chords:
        scales_str = ", ".join(s.name for s in ch.scales)
        chord_lines.append(
            f"  - Position {ch.position}: {ch.chord_name} ({ch.roman_numeral})"
            f" | diatonic={ch.is_diatonic}"
            + (f" [{ch.non_diatonic_type}]" if ch.non_diatonic_type else "")
            + f" | guide tones: {', '.join(ch.guide_tones)}"
            + f" | suggested scales: {scales_str}"
        )

    chords_block = "\n".join(chord_lines)
    progression = " — ".join(analysis.progression_numerals)
    flags = []
    if analysis.has_borrowed_chords:
        flags.append("borrowed chords present")
    if analysis.has_secondary_dominants:
        flags.append("secondary dominants present")
    if analysis.has_modulation:
        flags.append("modulation detected")
    flags_str = ", ".join(flags) if flags else "all diatonic"

    return f"""Analyze the following guitar tab music theory data and produce an educational explanation.

Key: {analysis.key} {analysis.mode} (confidence: {analysis.key_confidence:.0%})
Progression: {progression}
Harmonic flags: {flags_str}

Chord-by-chord breakdown:
{chords_block}

Generate the JSON explanation now."""
